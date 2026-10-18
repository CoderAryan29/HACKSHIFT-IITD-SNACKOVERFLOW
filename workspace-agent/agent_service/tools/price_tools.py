from __future__ import annotations

import logging
from typing import Any

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from agent_service.db.session import session_scope

logger = logging.getLogger(__name__)


@tool
def get_mandi_prices_tool(
    commodity: str,
    mandi_id: int | None = None,
    mandi_name: str | None = None,
    district: str | None = None,
    state: str | None = None,
    days: int = 30,
) -> dict[str, Any]:
    """Read latest real prices for a crop, optionally filtered by mandi name, district, or state."""
    if not commodity.strip():
        return {"error": "commodity is required"}
    if not 1 <= days <= 365:
        return {"error": "days must be between 1 and 365"}

    query = """
        SELECT DISTINCT ON (
                   p.mandi_id, p.commodity, COALESCE(p.variety, '')
               )
               p.price_date, p.mandi_id, m.name AS mandi,
               m.district, m.state, p.commodity, p.variety,
               p.min_price, p.max_price, p.modal_price, p.arrivals_qtl
        FROM mandi_prices AS p
        JOIN mandis AS m ON m.id = p.mandi_id
        WHERE regexp_replace(lower(trim(p.commodity)), '(es|s)$', '') =
              regexp_replace(lower(trim(:commodity)), '(es|s)$', '')
          AND p.price_date >= CURRENT_DATE - (:days * INTERVAL '1 day')
    """
    parameters: dict[str, Any] = {"commodity": commodity, "days": days}
    if mandi_id is not None:
        query += " AND p.mandi_id = :mandi_id"
        parameters["mandi_id"] = mandi_id
    if mandi_name and mandi_name.strip():
        query += " AND m.name ILIKE :mandi_name"
        parameters["mandi_name"] = f"%{mandi_name.strip()}%"
    if district and district.strip():
        query += " AND m.district ILIKE :district"
        parameters["district"] = f"%{district.strip()}%"
    if state and state.strip():
        query += " AND m.state ILIKE :state"
        parameters["state"] = f"%{state.strip()}%"
    query += """
        ORDER BY p.mandi_id, p.commodity, COALESCE(p.variety, ''),
                 p.price_date DESC
        LIMIT 500
    """

    try:
        with session_scope() as db:
            rows = db.execute(text(query), parameters).mappings().all()
        return {
            "source": "Supabase mandi_prices",
            "filters": {
                "commodity": commodity,
                "mandi_name": mandi_name,
                "district": district,
                "state": state,
                "days": days,
            },
            "prices": [dict(row) for row in rows],
        }
    except SQLAlchemyError:
        logger.exception("Could not retrieve mandi prices")
        return {"error": "Price data is currently unavailable from the market database."}


@tool
def get_price_forecast_tool(
    commodity: str, mandi_id: int | None = None
) -> dict[str, Any]:
    """Read an existing real forecast from the Supabase price_forecasts table."""
    if not commodity.strip():
        return {"error": "commodity is required"}

    query = """
        SELECT mandi_id, commodity, issued_on, target_date,
               horizon_days, p10, p50, p90, model_version
        FROM price_forecasts
        WHERE commodity = :commodity
    """
    parameters: dict[str, Any] = {"commodity": commodity}
    if mandi_id is not None:
        query += " AND mandi_id = :mandi_id"
        parameters["mandi_id"] = mandi_id
    query += " ORDER BY target_date ASC LIMIT 180"

    try:
        with session_scope() as db:
            rows = db.execute(text(query), parameters).mappings().all()
        return {
            "source": "Supabase price_forecasts",
            "forecasts": [dict(row) for row in rows],
        }
    except SQLAlchemyError as error:
        return {"error": f"Price forecast unavailable: {error}"}
