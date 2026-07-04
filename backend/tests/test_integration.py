from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.routers.travel import get_orchestrator, get_gemini_service
from app.schemas.travel import CultureLensResponse, DestinationInfo, WeatherOverview, BudgetOverview, EtiquetteGuide, SustainabilityTips, SafetyGuide, PackingChecklist

client = TestClient(app)

# Mock CultureLensResponse matching the schemas/travel.py response model
mock_travel_response = CultureLensResponse(
    destination=DestinationInfo(
        name="Kyoto, Japan",
        latitude=35.0116,
        longitude=135.7681,
        country="Japan",
        currency_code="JPY",
        timezone="Asia/Tokyo"
    ),
    summary="A cultural hub filled with shrines and traditional foods.",
    top_attractions=[],
    hidden_gems=[],
    heritage=[],
    stories=[],
    food=[],
    events=[],
    weather=WeatherOverview(
        current_temp="18°C",
        conditions="Sunny",
        weekly_forecast=["Day 1: Sunny", "Day 2: Clear"]
    ),
    budget=BudgetOverview(
        currency="JPY",
        estimated_daily_cost="15000 JPY",
        saving_tips=["Buy bus day passes"]
    ),
    itinerary=[],
    local_phrases=[],
    etiquette=EtiquetteGuide(
        greetings="Bow politely",
        dress_code="Modest in temples",
        photography_rules="Respect private signs",
        temple_etiquette="Remove shoes",
        dining_etiquette="Do not pass food chopsticks-to-chopsticks",
        tipping="No tipping allowed",
        local_customs="Keep voice low in public",
        common_mistakes=["Walking and eating"]
    ),
    sustainability=SustainabilityTips(
        public_transport="Use Hankyu Line",
        walking_routes="Walk along Kamo river",
        local_businesses="Eat at traditional Nishiki shops",
        plastic_reduction="Bring personal bottle",
        responsible_tourism="Do not harass Maikos"
    ),
    safety=SafetyGuide(
        emergency_number="110",
        common_scams=["Overpriced bars"],
        safe_neighborhoods=["Gion", "Shimogyo"],
        health_tips=["Drink water"]
    ),
    packing=PackingChecklist(
        essentials=["Passport", "Charger"],
        seasonal_items=["Umbrella"],
        cultural_items=["Easy slip-off shoes"]
    )
)

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
    mock_gemini = MagicMock()
    mock_gemini.generate_chat_response.return_value = "Hello! Welcome to Kyoto."
    
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
        mock_gemini.generate_chat_response.assert_called_once()
    finally:
        app.dependency_overrides.clear()
