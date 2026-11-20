"""Weather from MET Norway's Locationforecast 2.0 (api.met.no).

Why MET Norway: Open-Meteo's free tier is limited per IP, and Render's free
plan shares outbound IPs, so its daily quota was exhausted by other tenants
(HTTP 429). MET Norway sets no daily or per-IP cap; it asks clients to:

- send an identifying User-Agent with a contact (403 without one),
- respect `Expires` and revalidate with `If-Modified-Since`,
- truncate coordinates to 4 decimals (403 with 5 or more),
- keep total traffic under 20 requests/second,
- credit the data (CC BY 4.0).

Terms: https://api.met.no/doc/TermsOfService
"""
import logging
import math
import re
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger("app.clients.weather")

ATTRIBUTION = "Weather data: MET Norway (CC BY 4.0)"

_SYMBOL_RE = re.compile(
    r"^(?P<intensity>light|heavy)?s?(?P<kind>rain|sleet|snow)(?P<showers>showers)?(?P<thunder>andthunder)?$"
)
_SIMPLE_SYMBOLS = {
    "clearsky": "Clear sky",
    "fair": "Fair",
    "partlycloudy": "Partly cloudy",
    "cloudy": "Cloudy",
    "fog": "Fog",
}


def describe_symbol(symbol_code: Optional[str]) -> str:
    """Turn a MET symbol code such as 'lightrainshowers_day' into 'Light rain showers'."""
    if not symbol_code:
        return "Unknown"
    base = symbol_code.split("_", 1)[0]
    if base in _SIMPLE_SYMBOLS:
        return _SIMPLE_SYMBOLS[base]
    m = _SYMBOL_RE.match(base)
    if not m:
        return base.replace("_", " ").capitalize()
    words = [m["intensity"] or "", m["kind"]]
    if m["showers"]:
        words.append("showers")
    text = " ".join(w for w in words if w)
    if m["thunder"]:
        text += " and thunder"
    return text[0].upper() + text[1:]


def _truncate(value: float) -> float:
    """Truncate (not round) to 4 decimals, as MET's terms require."""
    return math.trunc(value * 10_000) / 10_000


def _expiry_from(headers: httpx.Headers, default_ttl: float) -> float:
    try:
        expires = parsedate_to_datetime(headers["Expires"]).timestamp()
        return max(expires, time.time() + 60)
    except (KeyError, TypeError, ValueError):
        return time.time() + default_ttl


class WeatherClient:
    """Current conditions and a 5-day outlook for a coordinate."""

    # Shared across the per-request instances FastAPI creates. Bounded so a
    # long-running process cannot grow it without limit.
    _cache: "OrderedDict[tuple, dict]" = OrderedDict()
    _cache_max_entries = 512
    _default_ttl = 3 * 3600  # MET: outside the Nordics, data updates every 6 h

    def __init__(self, client: httpx.AsyncClient = None):
        self.url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
        self.client = client
        self.headers = {"User-Agent": settings.MET_USER_AGENT}

    async def get_forecast(self, lat: float, lon: float) -> Optional[dict]:
        """Return {"current_temp", "conditions", "weekly_forecast"} or None on failure."""
        lat, lon = _truncate(lat), _truncate(lon)
        key = (lat, lon)
        entry = self._cache.get(key)
        if entry and time.time() < entry["expires"]:
            return entry["result"]

        headers = dict(self.headers)
        if entry and entry.get("last_modified"):
            headers["If-Modified-Since"] = entry["last_modified"]

        params = {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}"}
        try:
            if self.client:
                response = await self.client.get(self.url, params=params, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS, follow_redirects=True) as local:
                    response = await local.get(self.url, params=params, headers=headers)
        except httpx.HTTPError:
            logger.warning("MET Norway request failed for (%s, %s)", lat, lon, exc_info=True)
            return entry["result"] if entry else None

        if response.status_code == 304 and entry:
            entry["expires"] = _expiry_from(response.headers, self._default_ttl)
            self._cache.move_to_end(key)
            return entry["result"]

        if response.status_code != 200:
            logger.warning(
                "MET Norway returned HTTP %s for (%s, %s): %s",
                response.status_code, lat, lon, response.text[:200],
            )
            return entry["result"] if entry else None

        try:
            result = self._summarise(response.json(), lon)
        except (KeyError, IndexError, TypeError, ValueError):
            logger.warning("Unexpected MET Norway response shape for (%s, %s)", lat, lon, exc_info=True)
            return None

        self._cache[key] = {
            "result": result,
            "expires": _expiry_from(response.headers, self._default_ttl),
            "last_modified": response.headers.get("Last-Modified"),
        }
        self._cache.move_to_end(key)
        while len(self._cache) > self._cache_max_entries:
            self._cache.popitem(last=False)
        return result

    @staticmethod
    def _summarise(data: dict, lon: float) -> dict:
        series = data["properties"]["timeseries"]
        first = series[0]["data"]
        temp = first["instant"]["details"]["air_temperature"]
        symbol = None
        for window in ("next_1_hours", "next_6_hours", "next_12_hours"):
            symbol = first.get(window, {}).get("summary", {}).get("symbol_code")
            if symbol:
                break

        # Compact responses carry no daily max/min, so derive them from the
        # hourly temperatures. Times are UTC; bucket by an approximate local
        # day (longitude / 15 hours) so "Day 1" means the traveller's day.
        offset = timedelta(hours=round(lon / 15))
        days: "OrderedDict[str, dict]" = OrderedDict()
        for point in series:
            when = datetime.fromisoformat(point["time"].replace("Z", "+00:00")).astimezone(timezone.utc) + offset
            day = days.setdefault(when.date().isoformat(), {"temps": [], "symbol": None, "noon_gap": 24})
            day["temps"].append(point["data"]["instant"]["details"]["air_temperature"])
            day_symbol = (point["data"].get("next_6_hours") or point["data"].get("next_1_hours") or {}).get("summary", {}).get("symbol_code")
            gap = abs(when.hour - 12)
            if day_symbol and gap < day["noon_gap"]:  # prefer the symbol nearest midday
                day["symbol"], day["noon_gap"] = day_symbol, gap

        weekly = []
        for i, day in enumerate(list(days.values())[:5]):
            weekly.append(
                f"Day {i + 1}: Max {max(day['temps']):.1f}°C, Min {min(day['temps']):.1f}°C "
                f"({describe_symbol(day['symbol'])})"
            )

        return {
            "current_temp": f"{temp:.1f}°C",
            "conditions": describe_symbol(symbol),
            "weekly_forecast": weekly,
        }
