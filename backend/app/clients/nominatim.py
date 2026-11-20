import logging
import time
from typing import Optional

import httpx
from app.config import settings

logger = logging.getLogger("app.clients.nominatim")


class NominatimClient:
    """External client to interface with OpenStreetMap Nominatim Geocoding API."""

    _cache: dict = {}
    _cache_ttl = 86400

    def __init__(self, client: httpx.AsyncClient = None) -> None:
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)",
            # Without this, names come back in the local script (e.g. 京都市).
            "Accept-Language": "en",
        }
        self.client = client

    async def get_coordinates(self, destination: str) -> Optional[dict]:
        """Resolve a destination to coordinates, country and bounding box.

        Returns None when the destination cannot be geocoded. Callers must treat
        that as a user-facing error rather than inventing a location.
        """
        cleaned_dest = destination.strip().lower()
        entry = self._cache.get(cleaned_dest)
        if entry is not None:
            val, expiry = entry
            if time.time() < expiry:
                return val
            self._cache.pop(cleaned_dest, None)

        url = f"{self.base_url}/search"
        params = {"q": destination, "format": "json", "limit": 1, "addressdetails": 1}

        try:
            if self.client:
                response = await self.client.get(url, params=params, headers=self.headers)
            else:
                async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as local_client:
                    response = await local_client.get(url, params=params)
        except httpx.HTTPError:
            logger.warning("Nominatim request failed for %r", destination, exc_info=True)
            return None

        if response.status_code != 200:
            logger.warning("Nominatim returned HTTP %s for %r", response.status_code, destination)
            return None

        data = response.json()
        if not data:
            return None

        first = data[0]
        address = first.get("address", {})
        country_code = address.get("country_code")
        if not country_code:
            return None

        try:
            bounding_box = [float(x) for x in first.get("boundingbox", [])] or None
        except (TypeError, ValueError):
            bounding_box = None

        short_name = (first.get("name") or destination.split(",")[0]).strip()
        result = {
            "name": first.get("display_name", destination),
            # The place itself ("Kyoto"), for lookups that need a title rather
            # than a full address ("Kyoto, Kyoto Prefecture, Japan").
            "short_name": short_name,
            "latitude": float(first["lat"]),
            "longitude": float(first["lon"]),
            "country": address.get("country", ""),
            "country_code": country_code.upper(),
            "bounding_box": bounding_box,
        }
        self._cache[cleaned_dest] = (result, time.time() + self._cache_ttl)
        return result
