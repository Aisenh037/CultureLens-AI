import time
import httpx
from app.config import settings

class CurrencyClient:
    """Client to retrieve currency exchange rates relative to USD from Frankfurter API."""

    _rates_cache = None
    _rates_expiry = 0.0
    _cache_ttl = 21600  # 6 hours

    def __init__(self, client: httpx.AsyncClient = None):
        self.url = "https://api.frankfurter.app/latest"
        self.client = client

    async def get_usd_exchange_rates(self) -> dict:
        """Fetches exchange rates relative to USD."""
        if self._rates_cache and time.time() < self._rates_expiry:
            return self._rates_cache

        params = {"from": "USD"}
        client = self.client
        if client is not None:
            try:
                response = await client.get(self.url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get("rates", {})
                    if rates:
                        self.__class__._rates_cache = rates
                        self.__class__._rates_expiry = time.time() + self._cache_ttl
                    return rates
            except Exception:
                pass
        else:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as temp_client:
                try:
                    response = await temp_client.get(self.url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        rates = data.get("rates", {})
                        if rates:
                            self.__class__._rates_cache = rates
                            self.__class__._rates_expiry = time.time() + self._cache_ttl
                        return rates
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
