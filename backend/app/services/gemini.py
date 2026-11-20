import logging
from functools import lru_cache

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.config import settings
from app.schemas.travel import CultureLensResponse

logger = logging.getLogger("app.services.gemini")


# Fast transient failures worth one quick retry. 504 is deliberately absent:
# the SDK sends our timeout to Google as X-Server-Timeout, so a 504 means the
# whole deadline was used up, and retrying would double an already long wait.
RETRYABLE_STATUS_CODES = (429, 500, 502, 503)


def http_options(timeout_ms: int) -> types.HttpOptions:
    """Deadline plus one quick retry on transient errors."""
    return types.HttpOptions(
        timeout=timeout_ms,
        retry_options=types.HttpRetryOptions(
            attempts=2,  # the first try plus one retry
            initial_delay=1.0,
            max_delay=4.0,
            http_status_codes=list(RETRYABLE_STATUS_CODES),
        ),
    )


@lru_cache(maxsize=8)
def _client(api_key: str, timeout_ms: int) -> genai.Client:
    """One client per (key, timeout), reused across requests.

    FastAPI builds a GeminiService per request; caching the client keeps its
    connection pool alive instead of re-creating it every call.
    """
    return genai.Client(api_key=api_key, http_options=http_options(timeout_ms))


class GeminiService:
    """Wrapper around the Google Gen AI SDK (`google-genai`).

    The structured-output schema is the Pydantic `CultureLensResponse` model
    itself: the SDK converts it (including nested models and field
    descriptions) into Gemini's response schema, so there is one source of
    truth for the response shape instead of a hand-maintained copy.
    """

    def __init__(self) -> None:
        self.model = settings.GEMINI_MODEL
        # A full structured itinerary takes ~60-90 s to generate; chat replies
        # are short. Separate deadlines keep chat from hanging for minutes.
        self.client = _client(settings.GEMINI_API_KEY, int(settings.GEMINI_ITINERARY_TIMEOUT_SECONDS * 1000))
        self.chat_client = _client(settings.GEMINI_API_KEY, int(settings.GEMINI_CHAT_TIMEOUT_SECONDS * 1000))

    async def generate_structured_itinerary(self, prompt: str) -> CultureLensResponse:
        """Generate an itinerary constrained to the CultureLensResponse schema."""
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CultureLensResponse,
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=prompt, config=config
            )
        except Exception as e:
            logger.exception("Gemini structured generation request failed.")
            raise ValueError(f"Gemini structured response generation failed: {e}") from e

        # `parsed` is populated when the SDK could validate the JSON against the
        # schema. Fall back to validating the raw text ourselves so a schema
        # mismatch surfaces as a clear validation error rather than None.
        if isinstance(response.parsed, CultureLensResponse):
            return response.parsed
        try:
            return CultureLensResponse.model_validate_json(response.text or "")
        except ValidationError as e:
            logger.error("Gemini output did not match CultureLensResponse: %s", e)
            raise ValueError("Gemini returned output that does not match the response schema.") from e

    async def generate_chat_response(self, prompt: str) -> str:
        """Generate conversational text for the interactive tour guide."""
        try:
            response = await self.chat_client.aio.models.generate_content(model=self.model, contents=prompt)
        except Exception as e:
            logger.exception("Chat response generation failed.")
            raise ValueError(f"Gemini chat failed: {e}") from e
        return (response.text or "").strip()
