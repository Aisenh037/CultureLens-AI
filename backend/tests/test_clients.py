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

