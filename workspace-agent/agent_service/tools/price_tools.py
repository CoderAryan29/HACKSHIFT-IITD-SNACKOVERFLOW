from __future__ import annotations

from typing import Any

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from agent_service.db.session import session_scope


@tool
def get_mandi_prices_tool(
    commodity: str, mandi_id: int | None = None, days: int = 30
) -> dict[str, Any]:
    """Read recent real mandi prices from the existing Supabase mandi_prices table."""
    if not commodity.strip():
        return {"error": "commodity is required"}
    if not 1 <= days <= 365:
        return {"error": "days must be between 1 and 365"}

    query = """
        SELECT price_date, mandi_id, commodity, variety,
               min_price, max_price, modal_price, arrivals_qtl
        FROM mandi_prices
        WHERE commodity = :commodity
          AND price_date >= CURRENT_DATE - (:days * INTERVAL '1 day')
    """
    parameters: dict[str, Any] = {"commodity": commodity, "days": days}
    if mandi_id is not None:
        query += " AND mandi_id = :mandi_id"
        parameters["mandi_id"] = mandi_id
    query += " ORDER BY price_date DESC LIMIT 500"

    try:
        with session_scope() as db:
            rows = db.execute(text(query), parameters).mappings().all()
        return {"source": "Supabase mandi_prices", "prices": [dict(row) for row in rows]}
    except SQLAlchemyError as error:
        return {"error": f"Price data unavailable: {error}"}


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
