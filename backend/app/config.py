import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration and settings management."""
    
    PROJECT_NAME: str = "CultureLens AI API"
    VERSION: str = "1.0.0"
    
    # Gemini API Credentials
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "models/gemini-3.5-flash")
    
    # Allowed CORS Origins (Comma-separated string)
    ALLOWED_ORIGINS_RAW: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        if not self.ALLOWED_ORIGINS_RAW:
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_RAW.split(",")]
        
    # Security Configurations
    MAX_CONTENT_LENGTH: int = 1024 * 1024  # 1 MB Limit
    REQUEST_TIMEOUT_SECONDS: float = 90.0   # API timeout limit
    
    # HTTPX Client parameters
    MAX_CONNECTIONS: int = 100
    MAX_KEEPALIVE_CONNECTIONS: int = 20
    
settings = Settings()
