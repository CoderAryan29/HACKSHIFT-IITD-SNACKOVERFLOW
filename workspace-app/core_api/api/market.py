
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from core_api.db.models import Mandi, MandiPrice, PriceForecast
from core_api.db.session import get_db

router = APIRouter(tags=["Market Data"])


@router.get("/mandis")
def get_mandis(
    district_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Mandi)

    if district_id is not None:
        query = query.filter(Mandi.district_id == district_id)

    rows = query.order_by(Mandi.name).limit(500).all()

    return {
        "count": len(rows),
        "mandis": [
            {
                "id": row.id,
                "name": row.name,
                "state": row.state,
                "district": row.district,
                "district_id": row.district_id,
                "lat": row.lat,
                "lng": row.lng,
                "agmarknet_code": row.agmarknet_code,
            }
            for row in rows
        ],
    }


@router.get("/prices/records")
def get_price_records(
    commodity: str | None = Query(default=None, min_length=2),
    mandi_id: int | None = None,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    since = date.today() - timedelta(days=days - 1)

    query = (
        db.query(MandiPrice, Mandi.name.label("mandi_name"))
        .join(Mandi, Mandi.id == MandiPrice.mandi_id)
        .filter(MandiPrice.price_date >= since)
    )

    if commodity:
        normalized_commodity = func.regexp_replace(
            func.lower(func.trim(MandiPrice.commodity)), "(es|s)$", ""
        )
        normalized_search = func.regexp_replace(
            func.lower(func.trim(commodity.strip())), "(es|s)$", ""
        )
        query = query.filter(
            normalized_commodity == normalized_search
        )

    if mandi_id is not None:
        query = query.filter(MandiPrice.mandi_id == mandi_id)

    rows = query.order_by(
        MandiPrice.price_date.desc()
    ).limit(1000).all()

    return {
        "count": len(rows),
        "days": days,
        "source": "supabase",
        "prices": [
            {
                "id": price.id,
                "date": price.price_date,
                "commodity": price.commodity,
                "variety": price.variety,
                "mandi_id": price.mandi_id,
                "mandi": mandi_name,
                "min_price": price.min_price,
                "max_price": price.max_price,
                "modal_price": price.modal_price,
                "arrivals_qtl": price.arrivals_qtl,
            }
            for price, mandi_name in rows
        ],
    }


@router.get("/prices/forecast")
def get_price_forecast(
    commodity: str = Query(..., min_length=2),
    mandi_id: int = Query(...),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PriceForecast)
        .filter(
            PriceForecast.mandi_id == mandi_id,
            func.lower(PriceForecast.commodity)
            == commodity.strip().lower(),
            PriceForecast.target_date >= date.today(),
        )
        .order_by(PriceForecast.target_date.asc())
        .limit(90)
        .all()
    )

    return {
        "commodity": commodity,
        "mandi_id": mandi_id,
        "count": len(rows),
        "source": "stored_forecast",
        "forecasts": [
            {
                "issued_on": row.issued_on,
                "target_date": row.target_date,
                "horizon_days": row.horizon_days,
                "p10": row.p10,
                "p50": row.p50,
                "p90": row.p90,
                "model_version": row.model_version,
            }
            for row in rows
        ],
        "note": (
            "No stored forecasts found. Forecasts must be generated "
            "and saved before they can be returned."
            if not rows
            else None
        ),
    }


@router.get("/prices/advice")
def get_price_advice(
    commodity: str = Query(..., min_length=2),
    quantity_qtl: float = Query(..., gt=0),
    mandi_id: int | None = None,
    farm_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(MandiPrice).filter(
        func.lower(MandiPrice.commodity) == commodity.strip().lower(),
        MandiPrice.modal_price.is_not(None),
    )

    if mandi_id is not None:
        query = query.filter(MandiPrice.mandi_id == mandi_id)

    latest_date = query.with_entities(
        func.max(MandiPrice.price_date)
    ).scalar()

    if latest_date is None:
        raise HTTPException(
            status_code=404,
            detail="No market price data found for this commodity and mandi.",
        )

    rows = (
        query.filter(MandiPrice.price_date == latest_date)
        .order_by(MandiPrice.modal_price.desc())
        .all()
    )

    prices = [
        float(row.modal_price)
        for row in rows
        if row.modal_price is not None
    ]

    if not prices:
        raise HTTPException(
            status_code=404,
            detail="No usable modal price found.",
        )

    reference_price = sum(prices) / len(prices)

    return {
        "commodity": commodity,
        "farm_id": str(farm_id) if farm_id else None,
        "mandi_id": mandi_id,
        "quantity_qtl": quantity_qtl,
        "price_date": latest_date,
        "reference_price_per_qtl": round(reference_price, 2),
        "estimated_gross_value_inr": round(
            reference_price * quantity_qtl, 2
        ),
        "recommendation": (
            "Compare this market reference with buyer offers after "
            "considering transport, quality and commission costs."
        ),
        "source": "supabase_market_data",
        "is_ml_forecast": False,
    }
