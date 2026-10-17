
from core_api.schemas.prices import PriceRecord


DEMO_PRICES = [
    PriceRecord(
        commodity="Wheat",
        mandi="Azadpur",
        state="Delhi",
        price_per_quintal=2500,
    ),
    PriceRecord(
        commodity="Potato",
        mandi="Azadpur",
        state="Delhi",
        price_per_quintal=1200,
    ),
]


def get_prices(
    commodity: str | None = None,
    state: str | None = None,
) -> list[PriceRecord]:
    results = DEMO_PRICES

    if commodity:
        results = [
            item for item in results
            if item.commodity.casefold() == commodity.casefold()
        ]

    if state:
        results = [
            item for item in results
            if item.state.casefold() == state.casefold()
        ]

    return results
