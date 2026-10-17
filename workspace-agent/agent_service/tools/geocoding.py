from __future__ import annotations

from typing import Any

import httpx
from langchain_core.tools import tool


@tool
def geocode_location(location: str, language: str = "en") -> dict[str, Any]:
    """Resolve a farmer's city, village, district, or place name to coordinates.

    Use this before get_weather_tool whenever the user provides a place name
    instead of trusted farm latitude and longitude.
    """
    location = location.strip()
    if not location:
        return {"error": "location is required"}

    try:
        response = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": location,
                "count": 5,
                "language": "hi" if language == "hi" else "en",
                "format": "json",
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        if not isinstance(results, list) or not results:
            return {"error": f"No location found for '{location}'"}

        candidates = [
            {
                "name": result.get("name"),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "country": result.get("country"),
                "admin1": result.get("admin1"),
                "admin2": result.get("admin2"),
                "timezone": result.get("timezone"),
            }
            for result in results
        ]
        return {"source": "Open-Meteo Geocoding", "query": location, "results": candidates}
    except (httpx.HTTPError, ValueError) as error:
        return {"error": f"Geocoding service unavailable: {error}"}
