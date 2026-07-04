import httpx
from app.config import settings

class CurrencyClient:
    """Client to retrieve currency exchange rates relative to USD from Frankfurter API."""

    def __init__(self, client: httpx.AsyncClient = None):
        self.url = "https://api.frankfurter.app/latest"
        self.client = client
        self._cache = None

    async def get_usd_exchange_rates(self) -> dict:
        """Fetches exchange rates relative to USD."""
        if self._cache is not None:
            return self._cache

        params = {"from": "USD"}
        try:
            if self.client:
                response = await self.client.get(self.url, params=params)
            else:
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as local_client:
                    response = await local_client.get(self.url, params=params)
                    
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                self._cache = rates
                return rates
        except Exception:
            pass
            
        # Fallback values if API is down
        fallback = {
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
        return fallback
