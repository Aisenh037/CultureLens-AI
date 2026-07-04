from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import travel
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared HTTPX AsyncClient using configured connection limits
    limits = httpx.Limits(
        max_connections=settings.MAX_CONNECTIONS,
        max_keepalive_connections=settings.MAX_KEEPALIVE_CONNECTIONS
    )
    app.state.http_client = httpx.AsyncClient(
        limits=limits,
        timeout=settings.REQUEST_TIMEOUT_SECONDS
    )
    yield
    # Safely close connection pool on shutdown
    await app.state.http_client.aclose()

app = FastAPI(
    title="AI Travel Guide & Itinerary API",
    description="Backend service for generating personalized travel plans and itineraries using Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(travel.router)

@app.get("/")
def read_root():
    """Simple API status healthcheck."""
    return {"status": "healthy", "service": "AI Travel Guide & Itinerary API"}

