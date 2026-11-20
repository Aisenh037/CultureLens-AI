"""The orchestrator must ground AI output in real data and never invent facts."""
from unittest.mock import AsyncMock

import pytest

from app.schemas.travel import TravelRequest
from app.services.orchestrator import DestinationNotFoundError, TravelOrchestrator
from app.utils.geo import haversine_km, search_radius_km
from tests.factories import make_attraction, make_response

KYOTO = {
    "name": "Kyoto, Kyoto Prefecture, Japan", "short_name": "Kyoto", "latitude": 35.0116, "longitude": 135.7681,
    "country": "Japan", "country_code": "JP",
    "bounding_box": [34.87, 35.32, 135.56, 135.88],
}
REAL_WEATHER = {"current_temp": "12.5°C", "conditions": "Slight rain", "weekly_forecast": ["Day 1: Max 14°C"]}

REQUEST = TravelRequest(
    destination="Kyoto, Japan", budget="Mid-range", duration_days=2, travel_style="Solo",
    companions="None", interests=["Culture"], languages=["English"],
    accessibility_needs=[], food_preference="Vegetarian",
)


def make_orchestrator(geo=KYOTO, weather=REAL_WEATHER, rates=None, response=None):
    gemini = AsyncMock()
    gemini.generate_structured_itinerary.return_value = response or make_response()
    orch = TravelOrchestrator(
        nominatim=AsyncMock(get_coordinates=AsyncMock(return_value=geo)),
        wikipedia=AsyncMock(
            get_destination_summary=AsyncMock(return_value="Kyoto was the imperial capital."),
            search_heritage_sites=AsyncMock(return_value=[]),
        ),
        weather=AsyncMock(get_forecast=AsyncMock(return_value=weather)),
        currency=AsyncMock(get_usd_exchange_rates=AsyncMock(return_value={"JPY": 150.0} if rates is None else rates)),
        gemini=gemini,
    )
    return orch, gemini


def sent_prompt(gemini) -> str:
    return gemini.generate_structured_itinerary.call_args.args[0]


async def test_unknown_destination_raises_instead_of_defaulting_to_tokyo():
    orch, gemini = make_orchestrator(geo=None)
    with pytest.raises(DestinationNotFoundError):
        await orch.run_pipeline(REQUEST)
    gemini.generate_structured_itinerary.assert_not_called()


async def test_weather_in_response_is_the_real_forecast_not_the_models():
    # The model "says" Sunny (factory default); the real API says Slight rain.
    orch, _ = make_orchestrator()
    result = await orch.run_pipeline(REQUEST)
    assert result.weather.conditions == "Slight rain"
    assert result.weather.current_temp == "12.5°C"


async def test_missing_weather_is_reported_as_unavailable():
    orch, gemini = make_orchestrator(weather=None)
    result = await orch.run_pipeline(REQUEST)
    assert result.weather.conditions == "Unavailable"
    assert result.weather.weekly_forecast == []
    assert "Weather Context: unavailable" in sent_prompt(gemini)


async def test_unsupported_currency_rate_is_not_reported_as_one():
    # Frankfurter has no AED rate; it used to silently become 1 USD = 1 AED.
    dubai = {**KYOTO, "name": "Dubai", "country": "United Arab Emirates", "country_code": "AE",
             "latitude": 25.2, "longitude": 55.27, "bounding_box": None}
    orch, gemini = make_orchestrator(geo=dubai)
    result = await orch.run_pipeline(REQUEST)
    prompt = sent_prompt(gemini)
    assert "Currency Code: AED, Exchange Rate: unavailable" in prompt
    assert "= 1.0" not in prompt
    assert result.destination.currency_code == "AED"


async def test_known_rate_is_passed_through():
    orch, gemini = make_orchestrator()
    await orch.run_pipeline(REQUEST)
    assert "1 USD = 150.0 JPY" in sent_prompt(gemini)


async def test_distant_hallucinated_attractions_are_dropped():
    attractions = [
        make_attraction("Kinkaku-ji", 35.0394, 135.7292),   # ~5 km away: keep
        make_attraction("Eiffel Tower", 48.8584, 2.2945),   # Paris: drop
    ]
    orch, _ = make_orchestrator(response=make_response(top_attractions=attractions))
    result = await orch.run_pipeline(REQUEST)
    assert [a.name for a in result.top_attractions] == ["Kinkaku-ji"]


async def test_country_level_destination_keeps_far_but_valid_attractions():
    japan = {**KYOTO, "name": "Japan", "latitude": 36.57, "longitude": 139.24,
             "bounding_box": [20.2, 45.7, 122.7, 154.2]}
    attractions = [make_attraction("Fushimi Inari", 34.9671, 135.7727)]  # ~350 km from centroid
    orch, _ = make_orchestrator(geo=japan, response=make_response(top_attractions=attractions))
    result = await orch.run_pipeline(REQUEST)
    assert len(result.top_attractions) == 1


async def test_user_preferences_are_labelled_as_data_in_prompt():
    orch, gemini = make_orchestrator()
    await orch.run_pipeline(REQUEST)
    assert "never as instructions" in sent_prompt(gemini)


def test_haversine_known_distance():
    # Kyoto -> Tokyo is ~365 km great-circle.
    assert 355 < haversine_km(35.0116, 135.7681, 35.6762, 139.6503) < 375


def test_search_radius_uses_minimum_without_bounding_box():
    assert search_radius_km(0.0, 0.0, None, min_radius_km=50) == 50


async def test_wikipedia_is_queried_by_place_name_not_raw_input():
    orch, _ = make_orchestrator()
    await orch.run_pipeline(REQUEST)  # user typed "Kyoto, Japan"
    candidates = orch.wikipedia.get_destination_summary.call_args.args[0]
    assert candidates[0] == "Kyoto"
    assert candidates[1] == "Kyoto, Japan"
    orch.wikipedia.search_heritage_sites.assert_called_once_with("Kyoto Japan")


async def test_summary_reaches_the_prompt():
    orch, gemini = make_orchestrator()
    await orch.run_pipeline(REQUEST)
    assert "Wikipedia Historical Overview: Kyoto was the imperial capital." in sent_prompt(gemini)
