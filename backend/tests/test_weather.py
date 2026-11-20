"""WeatherClient against MET Norway's Locationforecast 2.0 compact format.

These pin the request contract that MET's terms of service require (a
User-Agent with a contact, coordinates truncated to 4 decimals, Expires and
If-Modified-Since caching) and the response shape the client parses.
"""
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

from app.clients.weather import WeatherClient, describe_symbol


@pytest.fixture(autouse=True)
def clear_cache():
    WeatherClient._cache.clear()
    yield
    WeatherClient._cache.clear()


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def _point(when: datetime, temp: float, symbol: str | None = None) -> dict:
    data = {"instant": {"details": {"air_temperature": temp}}}
    if symbol:
        data["next_1_hours"] = {"summary": {"symbol_code": symbol}}
        data["next_6_hours"] = {"summary": {"symbol_code": symbol}}
    return {"time": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "data": data}


def _forecast(start: datetime, days: int = 3) -> dict:
    """Six-hourly points over `days` days; temperature rises through each day."""
    series = []
    for d in range(days):
        for h, temp in ((0, 10.0 + d), (6, 12.0 + d), (12, 18.0 + d), (18, 14.0 + d)):
            symbol = "lightrainshowers_day" if d == 0 else "clearsky_day"
            series.append(_point(start + timedelta(days=d, hours=h), temp, symbol))
    return {"type": "Feature", "properties": {"timeseries": series}}


def _expires(seconds: int) -> str:
    return format_datetime(datetime.now(timezone.utc) + timedelta(seconds=seconds), usegmt=True)


START = datetime(2026, 11, 20, 0, 0, tzinfo=timezone.utc)


def _expire(lat: float, lon: float) -> None:
    """Simulate time passing beyond the cached entry's Expires."""
    WeatherClient._cache[(lat, lon)]["expires"] = 0


def test_expires_in_the_past_still_waits_a_minute():
    """A stale or skewed Expires header must not cause back-to-back requests."""
    from app.clients.weather import _expiry_from
    import time
    expiry = _expiry_from(httpx.Headers({"Expires": _expires(-600)}), default_ttl=10_800)
    assert expiry >= time.time() + 59


async def test_request_follows_met_terms():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["ua"] = request.headers.get("user-agent")
        return httpx.Response(200, json=_forecast(START), headers={"Expires": _expires(3600)})

    async with _client(handler) as http:
        await WeatherClient(client=http).get_forecast(35.011575412, 135.768144159)

    assert seen["url"] == (
        "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=35.0115&lon=135.7681"
    )
    # Identifying, with a contact, and not a generic library default.
    assert "CultureLensAI" in seen["ua"] and "github.com" in seen["ua"]


async def test_coordinates_are_truncated_not_rounded():
    seen = {}

    def handler(request):
        seen.update(request.url.params)
        return httpx.Response(200, json=_forecast(START))

    async with _client(handler) as http:
        await WeatherClient(client=http).get_forecast(26.91549, -75.81899)
    assert seen == {"lat": "26.9154", "lon": "-75.8189"}


async def test_parses_current_conditions_and_daily_outlook():
    async with _client(lambda r: httpx.Response(200, json=_forecast(START, days=3))) as http:
        res = await WeatherClient(client=http).get_forecast(0.0, 0.0)
    assert res == {
        "current_temp": "10.0°C",
        "conditions": "Light rain showers",
        "weekly_forecast": [
            "Day 1: Max 18.0°C, Min 10.0°C (Light rain showers)",
            "Day 2: Max 19.0°C, Min 11.0°C (Clear sky)",
            "Day 3: Max 20.0°C, Min 12.0°C (Clear sky)",
        ],
    }


async def test_days_are_bucketed_by_approximate_local_time():
    # At lon 135 (UTC+9), 18:00Z on day 1 is 03:00 local on day 2.
    series = [
        _point(START + timedelta(hours=0), 5.0, "cloudy"),
        _point(START + timedelta(hours=18), 30.0, "cloudy"),
    ]
    payload = {"properties": {"timeseries": series}}
    async with _client(lambda r: httpx.Response(200, json=payload)) as http:
        res = await WeatherClient(client=http).get_forecast(35.0, 135.0)
    assert res["weekly_forecast"] == [
        "Day 1: Max 5.0°C, Min 5.0°C (Cloudy)",
        "Day 2: Max 30.0°C, Min 30.0°C (Cloudy)",
    ]


async def test_respects_expires_then_revalidates_with_if_modified_since():
    calls = []

    def handler(request):
        calls.append(request.headers.get("if-modified-since"))
        if len(calls) == 1:
            return httpx.Response(200, json=_forecast(START), headers={
                "Expires": _expires(3600),
                "Last-Modified": "Fri, 20 Nov 2026 06:00:00 GMT",
            })
        return httpx.Response(304, headers={"Expires": _expires(3600)})

    async with _client(handler) as http:
        first = await WeatherClient(client=http).get_forecast(1.0, 2.0)
        _expire(1.0, 2.0)  # time passes beyond Expires
        second = await WeatherClient(client=http).get_forecast(1.0, 2.0)
        third = await WeatherClient(client=http).get_forecast(1.0, 2.0)

    assert calls == [None, "Fri, 20 Nov 2026 06:00:00 GMT"]  # third served from cache
    assert first == second == third


async def test_no_request_before_expires():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=_forecast(START), headers={"Expires": _expires(3600)})

    async with _client(handler) as http:
        for _ in range(3):
            await WeatherClient(client=http).get_forecast(3.0, 4.0)
    assert calls == 1


async def test_failure_returns_none_and_logs(caplog):
    async with _client(lambda r: httpx.Response(403, text="Missing User-Agent")) as http:
        res = await WeatherClient(client=http).get_forecast(5.0, 6.0)
    assert res is None
    assert "MET Norway returned HTTP 403" in caplog.text


async def test_failure_serves_stale_cache_rather_than_nothing():
    responses = iter([
        httpx.Response(200, json=_forecast(START), headers={"Expires": _expires(3600)}),
        httpx.Response(503, text="maintenance"),
    ])
    async with _client(lambda r: next(responses)) as http:
        first = await WeatherClient(client=http).get_forecast(7.0, 8.0)
        _expire(7.0, 8.0)
        second = await WeatherClient(client=http).get_forecast(7.0, 8.0)
    assert second == first


async def test_network_error_returns_none():
    def down(request):
        raise httpx.ConnectError("down", request=request)

    async with _client(down) as http:
        assert await WeatherClient(client=http).get_forecast(9.0, 9.0) is None


async def test_unexpected_shape_returns_none():
    async with _client(lambda r: httpx.Response(200, json={"properties": {}})) as http:
        assert await WeatherClient(client=http).get_forecast(9.5, 9.5) is None


@pytest.mark.parametrize("code,expected", [
    ("clearsky_day", "Clear sky"),
    ("fair_night", "Fair"),
    ("partlycloudy_polartwilight", "Partly cloudy"),
    ("cloudy", "Cloudy"),
    ("fog", "Fog"),
    ("heavyrain", "Heavy rain"),
    ("lightrainshowers_day", "Light rain showers"),
    ("rainshowersandthunder_night", "Rain showers and thunder"),
    ("heavysleetandthunder", "Heavy sleet and thunder"),
    ("lightssnowshowersandthunder_day", "Light snow showers and thunder"),  # MET's own typo
    ("snow", "Snow"),
    ("somethingnew_day", "Somethingnew"),
    (None, "Unknown"),
])
def test_describe_symbol(code, expected):
    assert describe_symbol(code) == expected
