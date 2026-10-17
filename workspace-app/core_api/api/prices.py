
from fastapi import APIRouter, Query

from core_api.schemas.prices import PriceListResponse
from core_api.services.price_advice import get_prices as fetch_prices

router = APIRouter(prefix="/prices", tags=["Mandi Prices"])


@router.get("/", response_model=PriceListResponse)
def get_prices(
    commodity: str | None = Query(default=None, min_length=2),
    state: str | None = Query(default=None, min_length=2),
):
    prices = fetch_prices(commodity=commodity, state=state)

    return {
        "count": len(prices),
        "source": "demo",
        "prices": prices,
    }
