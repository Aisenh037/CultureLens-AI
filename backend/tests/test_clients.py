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
