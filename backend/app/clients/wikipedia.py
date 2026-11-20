import time
import httpx
from urllib.parse import quote
from app.config import settings

class WikipediaClient:
    """External client to interface with Wikipedia APIs to fetch factual descriptions."""

    _summary_cache = {}
    _search_cache = {}
    _cache_ttl = 86400  # 24 hours

    def __init__(self, client: httpx.AsyncClient = None) -> None:
        self.summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
        self.search_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)"
        }
        self.client = client
        self._summary_cache = self.__class__._summary_cache
        self._search_cache = self.__class__._search_cache


    async def get_page_summary(self, page_title: str) -> str:
        """Fetches the introductory summary of a Wikipedia page."""
        cleaned_title = page_title.strip().lower()
        if cleaned_title in self._summary_cache:
            entry = self._summary_cache[cleaned_title]
            if isinstance(entry, tuple) and len(entry) == 2:
                val, expiry = entry
                if time.time() < expiry:
                    return val
                else:
                    del self._summary_cache[cleaned_title]
            else:
                return entry

        url = f"{self.summary_url}/{quote(page_title)}"
        try:
            if self.client:
                response = await self.client.get(url, headers=self.headers)
            else:
                async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as local_client:
                    response = await local_client.get(url)
                    
            if response.status_code == 200:
                data = response.json()
                # A disambiguation page ("Cambridge may refer to...") is not a
                # description of the place, so treat it as no match.
                extract = "" if data.get("type") == "disambiguation" else data.get("extract", "")
                self._summary_cache[cleaned_title] = (extract, time.time() + self._cache_ttl)
                return extract
        except Exception:
            pass
        return ""

    async def get_destination_summary(self, candidates: list[str]) -> str:
        """Return the first non-empty summary among candidate page titles.

        What a user types ("Kyoto, Japan") is rarely a Wikipedia title, so the
        orchestrator passes the geocoded short name first, then fallbacks.
        """
        seen = set()
        for title in candidates:
            key = (title or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            extract = await self.get_page_summary(title.strip())
            if extract:
                return extract
        return ""

    async def search_heritage_sites(self, destination: str) -> list[dict]:
        """Queries articles related to history, culture, and heritage sites of a destination."""
        cleaned_dest = destination.strip().lower()
        if cleaned_dest in self._search_cache:
            entry = self._search_cache[cleaned_dest]
            if isinstance(entry, tuple) and len(entry) == 2:
                val, expiry = entry
                if time.time() < expiry:
                    return val
                else:
                    del self._search_cache[cleaned_dest]
            else:
                return entry

        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{destination} history heritage sites attractions",
            "format": "json",
            "origin": "*"
        }
        
        try:
            if self.client:
                response = await self.client.get(self.search_url, params=params, headers=self.headers)
            else:
                async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as local_client:
                    response = await local_client.get(self.search_url, params=params)
                    
            if response.status_code == 200:
                data = response.json()
                search_results = data.get("query", {}).get("search", [])
                
                results = []
                # Get summary for top 3 articles
                for item in search_results[:3]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    # Remove HTML tags from snippet
                    clean_snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                    results.append({
                        "title": title,
                        "snippet": clean_snippet
                    })
                self._search_cache[cleaned_dest] = (results, time.time() + self._cache_ttl)
                return results
        except Exception:
            pass
        return []

