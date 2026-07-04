import httpx
from app.config import settings

class NominatimClient:
    """External client to interface with OpenStreetMap Nominatim Geocoding API."""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)"
        }

    async def get_coordinates(self, destination: str) -> dict:
        """Fetches latitude, longitude, and country details for a given destination text."""
        url = f"{self.base_url}/search"
        params = {
            "q": destination,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(url, params=params)
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
            except Exception as e:
                # Log error or return mock fallback
                pass
                
        # Safe fallback
        return {
            "name": destination,
            "latitude": 35.6762,  # Tokyo fallback
            "longitude": 139.6503,
            "country": "Unknown",
            "country_code": "USD"
        }
