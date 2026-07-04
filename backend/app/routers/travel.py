import httpx
from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.travel import TravelRequest, CultureLensResponse, ChatRequest, ChatMessage
from app.utils.sanitization import sanitize_string
from app.prompts.travel_prompt import build_chat_prompt
from app.services.orchestrator import TravelOrchestrator
from app.services.gemini import GeminiService
from app.clients.nominatim import NominatimClient
from app.clients.wikipedia import WikipediaClient
from app.clients.weather import WeatherClient
from app.clients.currency import CurrencyClient
from app.config import settings
import logging

logger = logging.getLogger("app.routers.travel")

router = APIRouter(prefix="/api/travel", tags=["travel"])

# Dependency Injection Providers
def get_http_client(request: Request) -> httpx.AsyncClient:
    return getattr(request.app.state, "http_client", None)

def get_nominatim_client(http_client: httpx.AsyncClient = Depends(get_http_client)) -> NominatimClient:
    return NominatimClient(client=http_client)

def get_wikipedia_client(http_client: httpx.AsyncClient = Depends(get_http_client)) -> WikipediaClient:
    return WikipediaClient(client=http_client)

def get_weather_client(http_client: httpx.AsyncClient = Depends(get_http_client)) -> WeatherClient:
    return WeatherClient(client=http_client)

def get_currency_client(http_client: httpx.AsyncClient = Depends(get_http_client)) -> CurrencyClient:
    return CurrencyClient(client=http_client)

def get_gemini_service() -> GeminiService:
    return GeminiService()

def get_orchestrator(
    nominatim: NominatimClient = Depends(get_nominatim_client),
    wikipedia: WikipediaClient = Depends(get_wikipedia_client),
    weather: WeatherClient = Depends(get_weather_client),
    currency: CurrencyClient = Depends(get_currency_client),
    gemini: GeminiService = Depends(get_gemini_service)
) -> TravelOrchestrator:
    return TravelOrchestrator(
        nominatim=nominatim,
        wikipedia=wikipedia,
        weather=weather,
        currency=currency,
        gemini=gemini
    )

def check_request_size(request: Request) -> None:
    """Enforces request body size limits from headers."""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if length > settings.MAX_CONTENT_LENGTH:
                raise HTTPException(
                    status_code=413, 
                    detail="Request body size exceeds the allowed limit."
                )
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid Content-Length header."
            )

def sanitize_travel_request(payload: TravelRequest) -> TravelRequest:
    """Sanitizes inputs to prevent XSS or prompt injections."""
    sanitized_interests = [sanitize_string(interest) for interest in payload.interests]
    sanitized_languages = [sanitize_string(lang) for lang in payload.languages]
    sanitized_access = [sanitize_string(acc) for acc in payload.accessibility_needs]
    
    return TravelRequest(
        destination=sanitize_string(payload.destination),
        budget=sanitize_string(payload.budget),
        duration_days=payload.duration_days,
        travel_style=sanitize_string(payload.travel_style),
        companions=sanitize_string(payload.companions),
        interests=sanitized_interests,
        languages=sanitized_languages,
        accessibility_needs=sanitized_access,
        food_preference=sanitize_string(payload.food_preference)
    )

@router.post("/generate", response_model=CultureLensResponse)
async def generate_travel_plan(
    payload: TravelRequest, 
    request: Request,
    orchestrator: TravelOrchestrator = Depends(get_orchestrator)
) -> CultureLensResponse:
    """Sanitizes input preferences, aggregates factual external context, and runs Gemini to generate an itinerary."""
    check_request_size(request)
    
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API Key is not configured on the server."
        )
        
    sanitized_payload = sanitize_travel_request(payload)
    
    try:
        result = await orchestrator.run_pipeline(sanitized_payload)
        return result
    except Exception as e:
        logger.exception("Failed to run travel orchestration pipeline.")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate travel guide and itinerary due to an internal server error. Please try again."
        )

@router.post("/chat")
async def chat_with_guide(
    payload: ChatRequest, 
    request: Request,
    gemini: GeminiService = Depends(get_gemini_service)
) -> dict[str, str]:
    """Converses with the Interactive Tour Guide chatbot in context of the itinerary."""
    check_request_size(request)
    
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API Key is not configured on the server."
        )
        
    sanitized_message = sanitize_string(payload.message)
    sanitized_history = [
        ChatMessage(role=sanitize_string(msg.role), content=sanitize_string(msg.content))
        for msg in payload.history
    ]
    
    prompt = build_chat_prompt(sanitized_message, sanitized_history, payload.itinerary_context)
    
    try:
        reply = await gemini.generate_chat_response(prompt)
        return {"reply": reply}
    except Exception as e:
        logger.exception("Failed to generate chat response.")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve guide response due to an internal server error. Please try again."
        )


