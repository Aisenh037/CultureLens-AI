from app.schemas.travel import (
    AttractionItem, CultureLensResponse, DestinationInfo, WeatherOverview, BudgetOverview,
    EtiquetteGuide, SustainabilityTips, SafetyGuide, PackingChecklist,
)


def make_attraction(name: str, latitude: float, longitude: float, **overrides) -> AttractionItem:
    base = dict(
        name=name, hero_image="", location="Somewhere", latitude=latitude, longitude=longitude,
        historical_summary="h", ai_story="s", architecture="a", interesting_facts=["f"],
        best_visiting_time="Morning", estimated_cost="Free", travel_duration="1h",
        crowd_level="Low", photography_tips="p", nearby_hidden_gem="g", accessibility="ok",
        map_link="https://maps.google.com/?q=x",
    )
    base.update(overrides)
    return AttractionItem(**base)


def make_response(**overrides) -> CultureLensResponse:
    """A complete, valid CultureLensResponse; pass field overrides as needed."""
    base = dict(
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
    base.update(overrides)
    return CultureLensResponse(**base)
