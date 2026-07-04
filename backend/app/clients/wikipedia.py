import httpx
from urllib.parse import quote
from app.config import settings

class WikipediaClient:
    """External client to interface with Wikipedia APIs to fetch factual descriptions."""

    def __init__(self):
        self.summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
        self.search_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {
            "User-Agent": "CultureLensAI/1.0 (contact@culturelens.ai; hackathon project)"
        }

    async def get_page_summary(self, page_title: str) -> str:
        """Fetches the introductory summary of a Wikipedia page."""
        url = f"{self.summary_url}/{quote(page_title)}"
        async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("extract", "")
            except Exception:
                pass
        return ""

    async def search_heritage_sites(self, destination: str) -> list[dict]:
        """Queries articles related to history, culture, and heritage sites of a destination."""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{destination} history heritage sites attractions",
            "format": "json",
            "origin": "*"
        }
        
        async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(self.search_url, params=params)
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
                    return results
            except Exception:
                pass
        return []
