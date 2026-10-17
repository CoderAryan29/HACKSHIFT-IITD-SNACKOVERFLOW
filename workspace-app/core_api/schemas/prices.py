
from typing import Literal

from pydantic import BaseModel, Field


class PriceRecord(BaseModel):
    commodity: str = Field(min_length=2)
    mandi: str = Field(min_length=2)
    state: str = Field(min_length=2)
    price_per_quintal: float = Field(gt=0)
    currency: Literal["INR"] = "INR"


class PriceListResponse(BaseModel):
    count: int = Field(ge=0)
    source: Literal["demo"]
    prices: list[PriceRecord]
