from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.rate_limit import limiter
from app.routers import travel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared HTTPX AsyncClient using configured connection limits
    limits = httpx.Limits(
        max_connections=settings.MAX_CONNECTIONS,
        max_keepalive_connections=settings.MAX_KEEPALIVE_CONNECTIONS
    )
    app.state.http_client = httpx.AsyncClient(
        limits=limits,
        timeout=settings.REQUEST_TIMEOUT_SECONDS,
        # Public APIs move (Frankfurter's 301 broke FX rates silently).
        follow_redirects=True,
    )
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="AI Travel Guide & Itinerary API",
    description="Backend service for generating personalized travel plans and itineraries using Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    """Reject oversized bodies before they are read and parsed.

    A size check inside the route runs only after FastAPI has already parsed the
    body, so it cannot protect anything. Requests without a Content-Length
    (chunked) are bounded by the per-field limits on the request schemas.
    """
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            too_large = int(content_length) > settings.MAX_CONTENT_LENGTH
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})
        if too_large:
            return JSONResponse(status_code=413, content={"detail": "Request body size exceeds the allowed limit."})
    return await call_next(request)


# CORS: explicit origins only. The API uses no cookies or auth headers, so
# credentials stay disabled.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(travel.router)


@app.get("/")
def read_root():
    """Simple API status healthcheck."""
    return {"status": "healthy", "service": "AI Travel Guide & Itinerary API"}
