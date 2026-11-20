from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.routers.travel import get_orchestrator, get_gemini_service
from tests.factories import make_response

client = TestClient(app)
mock_travel_response = make_response()

def test_generate_travel_endpoint():
    """Ensures /api/travel/generate returns valid response when using dependency overrides."""
    # Configure mock orchestrator
    mock_orchestrator = AsyncMock()
    mock_orchestrator.run_pipeline.return_value = mock_travel_response
    
    # Inject override
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    
    payload = {
        "destination": "Kyoto, Japan",
        "budget": "Mid-range",
        "duration_days": 3,
        "travel_style": "Solo",
        "companions": "None",
        "interests": ["Culture"],
        "languages": ["English"],
        "accessibility_needs": ["None"],
        "food_preference": "Vegetarian"
    }
    
    try:
        response = client.post("/api/travel/generate", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["destination"]["name"] == "Kyoto, Japan"
        assert json_data["weather"]["conditions"] == "Sunny"
        mock_orchestrator.run_pipeline.assert_called_once()
    finally:
        app.dependency_overrides.clear()

def test_chat_endpoint():
    """Ensures /api/travel/chat returns the guide response using dependency overrides."""
    class MockGeminiService:
        def __init__(self):
            self.calls = 0

        async def generate_chat_response(self, prompt: str) -> str:
            self.calls += 1
            return "Hello! Welcome to Kyoto."

    mock_gemini = MockGeminiService()
    app.dependency_overrides[get_gemini_service] = lambda: mock_gemini
    
    payload = {
        "message": "Hello!",
        "history": [],
        "itinerary_context": None
    }
    
    try:
        response = client.post("/api/travel/chat", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["reply"] == "Hello! Welcome to Kyoto."
        assert mock_gemini.calls == 1
    finally:
        app.dependency_overrides.clear()



