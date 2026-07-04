import time
import httpx
from app.config import settings

class NominatimClient:
    """External client to interface with OpenStreetMap Nominatim Geocoding API."""

    _cache = {}
    _cache_ttl = 86400

    def __init__(self, client: httpx.AsyncClient = None):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)"
        }
        self.client = client
        self._cache = self.__class__._cache

    async def get_coordinates(self, destination: str) -> dict:
        """Fetches latitude, longitude, and country details for a given destination text."""
        cleaned_dest = destination.strip().lower()
        if cleaned_dest in self._cache:
            entry = self._cache[cleaned_dest]
            if isinstance(entry, tuple) and len(entry) == 2:
                val, expiry = entry
                if time.time() < expiry:
                    return val
                else:
                    del self._cache[cleaned_dest]
            else:
                return entry

        url = f"{self.base_url}/search"
        params = {
            "q": destination,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        try:
            # Use injected lifespan client or instantiate a local one (SOLID decoupling)
            if self.client:
                response = await self.client.get(url, params=params, headers=self.headers)
            else:
                async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as local_client:
                    response = await local_client.get(url, params=params)
                    
            if response.status_code == 200:
                data = response.json()
                if data:
                    first_result = data[0]
                    address = first_result.get("address", {})
                    
                    country = address.get("country", "")
                    country_code = address.get("country_code", "us")
                    
                    result = {
                        "name": first_result.get("display_name", destination),
                        "latitude": float(first_result.get("lat", 0.0)),
                        "longitude": float(first_result.get("lon", 0.0)),
                        "country": country,
                        "country_code": country_code.upper()
                    }
                    self._cache[cleaned_dest] = (result, time.time() + self._cache_ttl)
                    return result
        except Exception:
            pass
                
        # Safe fallback
        return {
            "name": destination,
            "latitude": 35.6762,  # Tokyo fallback
            "longitude": 139.6503,
            "country": "Unknown",
            "country_code": "USD"
        }

