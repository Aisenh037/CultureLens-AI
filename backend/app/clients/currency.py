import logging
import time

import httpx
from app.config import settings

logger = logging.getLogger("app.clients.currency")


class CurrencyClient:
    """Client to retrieve currency exchange rates relative to USD from Frankfurter API.

    Frankfurter publishes ECB reference rates, which cover ~30 currencies. A
    currency missing from the result is genuinely unknown, so callers must not
    substitute a default rate.
    """

    # Class-level so the cache survives the per-request client instances that
    # FastAPI dependency injection creates.
    _cache: tuple[dict, float] | None = None
    _cache_ttl = 3600  # ECB rates update once a day; an hour is plenty fresh.

    def __init__(self, client: httpx.AsyncClient = None):
        self.url = "https://api.frankfurter.app/latest"
        self.client = client

    async def get_usd_exchange_rates(self) -> dict[str, float]:
        """Fetch exchange rates relative to USD. Returns {} if the API is unavailable."""
        cached = CurrencyClient._cache
        if cached is not None and time.time() < cached[1]:
            return cached[0]

        params = {"from": "USD"}
        try:
            if self.client:
                response = await self.client.get(self.url, params=params)
            else:
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as local_client:
                    response = await local_client.get(self.url, params=params)
        except httpx.HTTPError:
            logger.warning("Frankfurter request failed", exc_info=True)
            return {}

        if response.status_code != 200:
            logger.warning("Frankfurter returned HTTP %s", response.status_code)
            return {}

        rates = {k: float(v) for k, v in response.json().get("rates", {}).items()}
        rates["USD"] = 1.0
        CurrencyClient._cache = (rates, time.time() + self._cache_ttl)
        return rates
