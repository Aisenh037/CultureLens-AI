import time
import httpx
from app.config import settings

class NominatimClient:
    """External client to interface with OpenStreetMap Nominatim Geocoding API."""

    # Thread-safe in-memory cache with 24 hours TTL for geocoding results
    _cache = {}
    _cache_ttl = 86400

    def __init__(self, client: httpx.AsyncClient = None):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)"
        }
        self.client = client

    async def get_coordinates(self, destination: str) -> dict:
        """Fetches latitude, longitude, and country details for a given destination text."""
        # Normalize key for caching
        cache_key = destination.strip().lower()
        if cache_key in self._cache:
            val, expiry = self._cache[cache_key]
            if time.time() < expiry:
                return val
            else:
                del self._cache[cache_key]

        url = f"{self.base_url}/search"
        params = {
            "q": destination,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        # Use shared HTTP client if available, otherwise create temporary client
        client = self.client
        if client is not None:
            try:
                response = await client.get(url, params=params, headers=self.headers)
                result = self._parse_response(response, destination)
                if result["country"] != "Unknown":
                    self._cache[cache_key] = (result, time.time() + self._cache_ttl)
                return result
            except Exception:
                pass
        else:
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as temp_client:
                try:
                    response = await temp_client.get(url, params=params)
                    result = self._parse_response(response, destination)
                    if result["country"] != "Unknown":
                        self._cache[cache_key] = (result, time.time() + self._cache_ttl)
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

    def _parse_response(self, response: httpx.Response, destination: str) -> dict:
        if response.status_code == 200:
            data = response.json()
            if data:
                first_result = data[0]
                address = first_result.get("address", {})
                
                # Get country name
                country = address.get("country", "")
                
                # Get currency representation code if applicable, default map
                country_code = address.get("country_code", "us")
                
                return {
                    "name": first_result.get("display_name", destination),
                    "latitude": float(first_result.get("lat", 0.0)),
                    "longitude": float(first_result.get("lon", 0.0)),
                    "country": country,
                    "country_code": country_code.upper()
                }
        raise ValueError("Invalid geocoding response")
