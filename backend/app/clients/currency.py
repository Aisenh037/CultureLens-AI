import httpx
from app.config import settings

class CurrencyClient:
    """Client to retrieve currency exchange rates relative to USD from Frankfurter API."""

    def __init__(self):
        self.url = "https://api.frankfurter.app/latest"

    async def get_usd_exchange_rates(self) -> dict:
        """Fetches exchange rates relative to USD."""
        params = {"from": "USD"}
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(self.url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("rates", {})
            except Exception:
                pass
        # Fallback values
        return {
            "JPY": 155.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "INR": 83.5,
            "AUD": 1.50,
            "CAD": 1.37,
            "CHF": 0.90,
            "CNY": 7.25,
            "NZD": 1.63
        }
