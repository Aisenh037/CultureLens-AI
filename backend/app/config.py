import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Application configuration and settings management."""

    PROJECT_NAME: str = "CultureLens AI API"
    VERSION: str = "1.0.0"

    # Gemini API Credentials
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    # Sent to Google as the server-side deadline. A full itinerary was taking
    # 60-90 s, so 90 s caused intermittent 504 DEADLINE_EXCEEDED in production.
    GEMINI_ITINERARY_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_ITINERARY_TIMEOUT_SECONDS", "150"))
    GEMINI_CHAT_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_CHAT_TIMEOUT_SECONDS", "60"))

    # Allowed CORS origins (comma-separated). There is deliberately no "*"
    # fallback: an unset value means "local dev only", never "anyone".
    ALLOWED_ORIGINS_RAW: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")

    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        origins = [o.strip() for o in self.ALLOWED_ORIGINS_RAW.split(",") if o.strip()]
        return [o for o in origins if o != "*"] or ["http://localhost:5173"]

    # Security Configurations
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", str(256 * 1024)))  # 256 KB
    REQUEST_TIMEOUT_SECONDS: float = 90.0

    # Rate limits (per client IP), slowapi syntax.
    RATE_LIMIT_ENABLED: bool = _env_bool("RATE_LIMIT_ENABLED", True)
    GENERATE_RATE_LIMIT: str = os.getenv("GENERATE_RATE_LIMIT", "5/minute;30/hour")
    CHAT_RATE_LIMIT: str = os.getenv("CHAT_RATE_LIMIT", "20/minute")

    # Grounding: generated attractions farther than this from the destination
    # (or its bounding box, whichever is larger) are discarded.
    MIN_ATTRACTION_RADIUS_KM: float = float(os.getenv("MIN_ATTRACTION_RADIUS_KM", "50"))

    # MET Norway requires an identifying User-Agent with a contact method
    # (https://api.met.no/doc/TermsOfService). Override with your own domain/email.
    MET_USER_AGENT: str = os.getenv(
        "MET_USER_AGENT", "CultureLensAI/1.0 github.com/Aisenh037/CultureLens-AI"
    )

    # HTTPX Client parameters
    MAX_CONNECTIONS: int = 100
    MAX_KEEPALIVE_CONNECTIONS: int = 20


settings = Settings()
