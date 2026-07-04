import pytest
from app.clients import NominatimClient, WikipediaClient, WeatherClient, CurrencyClient

def test_weather_code_interpretation():
    """Verify that WeatherClient interprets weather codes correctly."""
    client = WeatherClient()
    assert client._interpret_weather_code(0) == "Clear sky / Sunny"
    assert client._interpret_weather_code(95) == "Thunderstorm"
    assert "Clear" in client._interpret_weather_code(999)  # Fallback

@pytest.mark.asyncio
async def test_nominatim_fallback():
    """Verify that NominatimClient returns a standard safe fallback on connection error."""
    client = NominatimClient()
    # Test with invalid url to trigger error fallback
    client.base_url = "https://invalid.osm.url"
    res = await client.get_coordinates("Kyoto")
    assert res["country"] == "Unknown"
    assert res["latitude"] == 35.6762

@pytest.mark.asyncio
async def test_wikipedia_fallback():
    """Verify WikipediaClient returns empty extracts on connection error."""
    client = WikipediaClient()
    client.summary_url = "https://invalid.wikipedia.url"
    res = await client.get_page_summary("Kyoto")
    assert res == ""

@pytest.mark.asyncio
async def test_currency_fallback():
    """Verify CurrencyClient fallback returns a dictionary of rates."""
    client = CurrencyClient()
    client.url = "https://invalid.frankfurter.url"
    res = await client.get_usd_exchange_rates()
    assert isinstance(res, dict)
    assert "JPY" in res

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

