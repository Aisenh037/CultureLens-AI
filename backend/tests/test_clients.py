import httpx
import pytest
from app.clients import NominatimClient, WikipediaClient, WeatherClient, CurrencyClient

def test_weather_code_interpretation():
    """Verify that WeatherClient interprets weather codes correctly."""
    client = WeatherClient()
    assert client._interpret_weather_code(0) == "Clear sky / Sunny"
    assert client._interpret_weather_code(95) == "Thunderstorm"
    assert "Clear" in client._interpret_weather_code(999)  # Fallback

def _client(handler) -> httpx.AsyncClient:
    """An AsyncClient backed by an in-process handler: no real network in tests."""
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def _down(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("service down", request=request)


@pytest.mark.asyncio
async def test_nominatim_returns_none_when_service_down():
    """A failed lookup must not invent a location (it used to fall back to Tokyo)."""
    async with _client(_down) as http:
        res = await NominatimClient(client=http).get_coordinates("Atlantis-test-down")
    assert res is None


@pytest.mark.asyncio
async def test_nominatim_returns_none_for_unknown_place():
    async with _client(lambda r: httpx.Response(200, json=[])) as http:
        res = await NominatimClient(client=http).get_coordinates("Atlantis-test-empty")
    assert res is None


@pytest.mark.asyncio
async def test_nominatim_parses_result_with_bounding_box():
    payload = [{
        "display_name": "Kyoto, Japan", "lat": "35.0116", "lon": "135.7681",
        "boundingbox": ["34.87", "35.32", "135.56", "135.88"],
        "address": {"country": "Japan", "country_code": "jp"},
    }]
    async with _client(lambda r: httpx.Response(200, json=payload)) as http:
        res = await NominatimClient(client=http).get_coordinates("Kyoto-test-parse")
    assert res["country_code"] == "JP"
    assert res["bounding_box"] == [34.87, 35.32, 135.56, 135.88]


@pytest.mark.asyncio
async def test_wikipedia_fallback():
    """Verify WikipediaClient returns empty extracts on connection error."""
    async with _client(_down) as http:
        res = await WikipediaClient(client=http).get_page_summary("Kyoto-test-down")
    assert res == ""


@pytest.mark.asyncio
async def test_weather_returns_none_when_service_down():
    """No invented weather: the old fallback returned a fake '22°C, Mainly clear'."""
    async with _client(_down) as http:
        res = await WeatherClient(client=http).get_forecast(-12.3456, 98.7654)
    assert res is None


@pytest.mark.asyncio
async def test_currency_returns_empty_when_service_down():
    """No invented exchange rates when Frankfurter is unreachable."""
    CurrencyClient._cache = None
    async with _client(_down) as http:
        res = await CurrencyClient(client=http).get_usd_exchange_rates()
    assert res == {}


@pytest.mark.asyncio
async def test_currency_cache_survives_new_instances():
    """FastAPI builds a new client per request, so the cache must be class-level."""
    CurrencyClient._cache = None
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"rates": {"JPY": 150.0}})

    async with _client(handler) as http:
        first = await CurrencyClient(client=http).get_usd_exchange_rates()
        second = await CurrencyClient(client=http).get_usd_exchange_rates()
    assert first == second == {"JPY": 150.0, "USD": 1.0}
    assert calls == 1
    CurrencyClient._cache = None


@pytest.mark.asyncio
async def test_nominatim_caching():
    """Verify that NominatimClient caches successful geocoding requests."""
    import time
    client = NominatimClient()
    cache_key = "testcity123"
    client._cache[cache_key] = ({
        "name": "Cached Test City",
        "latitude": 42.0,
        "longitude": 42.0,
        "country": "Cached Land",
        "country_code": "CL"
    }, time.time() + 100)
    
    res = await client.get_coordinates(cache_key)
    assert res["name"] == "Cached Test City"
    assert res["latitude"] == 42.0

@pytest.mark.asyncio
async def test_wikipedia_caching():
    """Verify that WikipediaClient caches successful summary searches."""
    import time
    client = WikipediaClient()
    cache_key = "testpage123"
    client._summary_cache[cache_key] = ("Cached extract text", time.time() + 100)
    
    res = await client.get_page_summary(cache_key)
    assert res == "Cached extract text"

@pytest.mark.asyncio
async def test_weather_caching():
    """Verify that WeatherClient caches forecast results based on rounded coordinates."""
    import time
    client = WeatherClient()
    coords = (12.345, 67.891)
    rounded_coords = (12.35, 67.89)
    client._forecast_cache[rounded_coords] = ({
        "current_temp": "99°C",
        "conditions": "Super Hot",
        "weekly_forecast": []
    }, time.time() + 100)
    
    res = await client.get_forecast(*coords)
    assert res["current_temp"] == "99°C"
    assert res["conditions"] == "Super Hot"



# --- Provider contracts -------------------------------------------------------
# These pin the request format and response shape each public API documents,
# so a provider change fails CI instead of silently degrading production.

@pytest.mark.asyncio
async def test_weather_uses_current_open_meteo_contract():
    seen = {}

    def handler(request):
        seen.update(request.url.params)
        return httpx.Response(200, json={
            "current": {"temperature_2m": 12.5, "weather_code": 61},
            "daily": {
                "time": ["2026-11-20", "2026-11-21"],
                "temperature_2m_max": [14.0, 15.1],
                "temperature_2m_min": [6.2, 7.0],
                "weather_code": [61, 0],
            },
        })

    async with _client(handler) as http:
        res = await WeatherClient(client=http).get_forecast(11.111, 22.222)
    assert seen["current"] == "temperature_2m,weather_code"
    assert "weather_code" in seen["daily"]
    assert "current_weather" not in seen
    assert res == {
        "current_temp": "12.5°C",
        "conditions": "Slight rain",
        "weekly_forecast": [
            "Day 1: Max 14.0°C, Min 6.2°C (Slight rain)",
            "Day 2: Max 15.1°C, Min 7.0°C (Clear sky / Sunny)",
        ],
    }


@pytest.mark.asyncio
async def test_weather_non_200_is_none_and_logged(caplog):
    async with _client(lambda r: httpx.Response(400, json={"reason": "bad param"})) as http:
        res = await WeatherClient(client=http).get_forecast(33.333, 44.444)
    assert res is None
    assert "Open-Meteo returned HTTP 400" in caplog.text


@pytest.mark.asyncio
async def test_currency_uses_frankfurter_dev_with_usd_base():
    CurrencyClient._cache = None
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"amount": 1.0, "base": "USD", "rates": {"INR": 84.1}})

    async with _client(handler) as http:
        rates = await CurrencyClient(client=http).get_usd_exchange_rates()
    assert seen["url"] == "https://api.frankfurter.dev/v1/latest?base=USD"
    assert rates == {"INR": 84.1, "USD": 1.0}
    CurrencyClient._cache = None


@pytest.mark.asyncio
async def test_shared_client_follows_provider_redirects():
    """A 301 from a provider (as Frankfurter's old domain now returns) must be followed."""
    CurrencyClient._cache = None

    def handler(request):
        if request.url.host == "api.frankfurter.dev":
            return httpx.Response(301, headers={"Location": "https://moved.example/latest?base=USD"})
        return httpx.Response(200, json={"rates": {"JPY": 150.0}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True) as http:
        rates = await CurrencyClient(client=http).get_usd_exchange_rates()
    assert rates["JPY"] == 150.0
    CurrencyClient._cache = None


def test_app_http_client_follows_redirects():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app):
        assert app.state.http_client.follow_redirects is True


@pytest.mark.asyncio
async def test_nominatim_requests_english_names():
    seen = {}

    def handler(request):
        seen["lang"] = request.headers.get("accept-language")
        return httpx.Response(200, json=[])

    async with _client(handler) as http:
        await NominatimClient(client=http).get_coordinates("Kyoto-test-lang")
    assert seen["lang"] == "en"
