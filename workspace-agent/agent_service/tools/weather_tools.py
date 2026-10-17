from __future__ import annotations

from typing import Any

import httpx
from langchain_core.tools import tool


@tool
def get_weather_tool(latitude: float, longitude: float, days: int = 7) -> dict[str, Any]:
    """Fetch a real daily forecast from Open-Meteo for latitude and longitude."""
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return {"error": "Invalid latitude or longitude"}
    if not 1 <= days <= 7:
        return {"error": "days must be between 1 and 7"}
    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "forecast_days": days,
                "timezone": "auto",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        return {
            "source": "Open-Meteo",
            "latitude": latitude,
            "longitude": longitude,
            "timezone": payload.get("timezone"),
            "daily": payload.get("daily", {}),
        }
    except (httpx.HTTPError, ValueError) as error:
        return {"error": f"Weather service unavailable: {error}"}
