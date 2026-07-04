import time
import httpx
from urllib.parse import quote
from app.config import settings

class WikipediaClient:
    """External client to interface with Wikipedia APIs to fetch factual descriptions."""

    _summary_cache = {}
    _heritage_cache = {}
    _cache_ttl = 86400  # 24 hours

    def __init__(self, client: httpx.AsyncClient = None):
        self.summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
        self.search_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)"
        }
        self.client = client

    async def get_page_summary(self, page_title: str) -> str:
        """Fetches the introductory summary of a Wikipedia page."""
        cache_key = page_title.strip().lower()
        if cache_key in self._summary_cache:
            val, expiry = self._summary_cache[cache_key]
            if time.time() < expiry:
                return val
            else:
                del self._summary_cache[cache_key]

        url = f"{self.summary_url}/{quote(page_title)}"
        client = self.client
        if client is not None:
            try:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    res = data.get("extract", "")
                    if res:
                        self._summary_cache[cache_key] = (res, time.time() + self._cache_ttl)
                    return res
            except Exception:
                pass
        else:
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as temp_client:
                try:
                    response = await temp_client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        res = data.get("extract", "")
                        if res:
                            self._summary_cache[cache_key] = (res, time.time() + self._cache_ttl)
                        return res
                except Exception:
                    pass
        return ""

    async def search_heritage_sites(self, destination: str) -> list[dict]:
        """Queries articles related to history, culture, and heritage sites of a destination."""
        cache_key = destination.strip().lower()
        if cache_key in self._heritage_cache:
            val, expiry = self._heritage_cache[cache_key]
            if time.time() < expiry:
                return val
            else:
                del self._heritage_cache[cache_key]

        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{destination} history heritage sites attractions",
            "format": "json",
            "origin": "*"
        }
        
        client = self.client
        if client is not None:
            try:
                response = await client.get(self.search_url, params=params, headers=self.headers)
                res = self._parse_search_response(response)
                if res:
                    self._heritage_cache[cache_key] = (res, time.time() + self._cache_ttl)
                return res
            except Exception:
                pass
        else:
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as temp_client:
                try:
                    response = await temp_client.get(self.search_url, params=params)
                    res = self._parse_search_response(response)
                    if res:
                        self._heritage_cache[cache_key] = (res, time.time() + self._cache_ttl)
                    return res
                except Exception:
                    pass
        return []

    def _parse_search_response(self, response: httpx.Response) -> list[dict]:
        if response.status_code == 200:
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            results = []
            for item in search_results[:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                clean_snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                results.append({
                    "title": title,
                    "snippet": clean_snippet
                })
            return results
        return []
