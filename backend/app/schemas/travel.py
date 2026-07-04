from pydantic import BaseModel, Field, conint
from typing import List, Optional, Dict

# Request Model
class TravelRequest(BaseModel):
    destination: str = Field(..., description="Target destination (e.g. Kyoto, Japan)")
    budget: str = Field(..., description="Budget class: Budget, Mid-range, or Luxury")
    duration_days: conint(ge=1, le=14) = Field(..., description="Trip duration in days (1 to 14)")
    travel_style: str = Field(..., description="Solo, Couple, Family, or Friends")
    companions: str = Field(..., description="Companion type description")
    interests: List[str] = Field(..., description="List of user interests")
    languages: List[str] = Field(..., description="User's preferred languages")
    accessibility_needs: List[str] = Field(..., description="Accessibility requirements")
    food_preference: str = Field(..., description="Dietary restrictions or culinary styles")


# Response Nested Models
class DestinationInfo(BaseModel):
    name: str = Field(..., description="Verified name of the destination")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    country: str = Field(..., description="Country name")
    currency_code: str = Field(..., description="Local currency code")
    timezone: str = Field(..., description="Local timezone")

class AttractionItem(BaseModel):
    name: str = Field(..., description="Name of the attraction")
    hero_image: str = Field(..., description="Hero image URL from Wikimedia/Unsplash")
    location: str = Field(..., description="Street or neighborhood location name")
    latitude: float = Field(..., description="Approximate latitude coordinate of the landmark (must be close to the destination center)")
    longitude: float = Field(..., description="Approximate longitude coordinate of the landmark (must be close to the destination center)")
    historical_summary: str = Field(..., description="Factual historical summary")
    ai_story: str = Field(..., description="Immersive narrative about the spot")
    architecture: str = Field(..., description="Architectural design style description")
    interesting_facts: List[str] = Field(..., description="Fascinating trivia facts")
    best_visiting_time: str = Field(..., description="Ideal visiting hour/season")
    estimated_cost: str = Field(..., description="Approximate ticket/entry cost")
    travel_duration: str = Field(..., description="Recommended stay duration")
    crowd_level: str = Field(..., description="Typical crowd density level")
    photography_tips: str = Field(..., description="Suggestions for photography")
    nearby_hidden_gem: str = Field(..., description="Closest off-beat gem")
    accessibility: str = Field(..., description="Wheelchair or sensory access details")
    map_link: str = Field(..., description="Google Maps search link")

class HiddenGemItem(BaseModel):
    name: str = Field(..., description="Name of the hidden gem")
    why_locals_love_it: str = Field(..., description="What makes this spot special to residents")
    interesting_story: str = Field(..., description="Folk story or unique history of the gem")
    best_time: str = Field(..., description="Best time to visit")
    nearby_food: str = Field(..., description="Authentic local food nearby")
    estimated_budget: str = Field(..., description="Cost representation")
    photography_spot: str = Field(..., description="Specific capture spot")

class HeritageItem(BaseModel):
    name: str = Field(..., description="Name of the cultural/historic site")
    description: str = Field(..., description="General description of the site")
    significance: str = Field(..., description="Cultural or UNESCO significance details")

class StoryItem(BaseModel):
    title: str = Field(..., description="Engaging story title")
    narration: str = Field(..., description="Narrator description of the historical lore")
    associated_attraction: str = Field(..., description="Attraction name linked to the story")

class FoodItem(BaseModel):
    dish: str = Field(..., description="Dish name")
    history: str = Field(..., description="Historical culinary origin story")
    ingredients: List[str] = Field(..., description="Primary ingredients used")
    vegetarian_status: str = Field(..., description="Vegetarian/Vegan status (Yes/No/Adaptable)")
    average_cost: str = Field(..., description="Estimated cost")
    nearby_area: str = Field(..., description="Suggested neighborhood to try it")
    dining_etiquette: str = Field(..., description="Traditional dining guidelines")

class EventItem(BaseModel):
    name: str = Field(..., description="Name of seasonal festival or event")
    timing: str = Field(..., description="When it occurs (months, dates)")
    description: str = Field(..., description="Details of the event celebration")

class WeatherOverview(BaseModel):
    current_temp: str = Field(..., description="Current temperature representation")
    conditions: str = Field(..., description="General conditions (Sunny, Rainy, etc.)")
    weekly_forecast: List[str] = Field(..., description="Forecast snippets for subsequent days")

class BudgetOverview(BaseModel):
    currency: str = Field(..., description="Local currency symbol/code")
    estimated_daily_cost: str = Field(..., description="Expected daily spend based on profile")
    saving_tips: List[str] = Field(..., description="Smart recommendations to save money")

class ActivityItem(BaseModel):
    time_slot: str = Field(..., description="Morning, Afternoon, or Evening")
    activity_name: str = Field(..., description="Name of the planned spot/tour")
    description: str = Field(..., description="Detailed instructions and notes")
    duration: str = Field(..., description="Time interval spent")
    cost: str = Field(..., description="Expected cost")
    category: str = Field(..., description="Heritage, Hidden Gem, Food, or Leisure")

class DayPlan(BaseModel):
    day_number: int = Field(..., description="Day number index (e.g. 1)")
    theme: str = Field(..., description="Focus topic of the day")
    activities: List[ActivityItem] = Field(..., description="Timed itinerary activities")

class PhraseItem(BaseModel):
    phrase: str = Field(..., description="English phrase")
    translation: str = Field(..., description="Translated phrase")
    pronunciation: str = Field(..., description="Pronunciation help")

class EtiquetteGuide(BaseModel):
    greetings: str = Field(..., description="Greetings etiquette")
    dress_code: str = Field(..., description="Dress code guidelines")
    photography_rules: str = Field(..., description="Photography limits")
    temple_etiquette: str = Field(..., description="Religious site guidelines")
    dining_etiquette: str = Field(..., description="Table manners")
    tipping: str = Field(..., description="Tipping expectations")
    local_customs: str = Field(..., description="General social norms")
    common_mistakes: List[str] = Field(..., description="Mistakes to avoid")

class SustainabilityTips(BaseModel):
    public_transport: str = Field(..., description="Public transport suggestions")
    walking_routes: str = Field(..., description="Eco-friendly routes")
    local_businesses: str = Field(..., description="Ethical local business suggestions")
    plastic_reduction: str = Field(..., description="Anti-waste details")
    responsible_tourism: str = Field(..., description="Respectful traveling habits")

class SafetyGuide(BaseModel):
    emergency_number: str = Field(..., description="Local police/ambulance number")
    common_scams: List[str] = Field(..., description="Scams targeting tourists")
    safe_neighborhoods: List[str] = Field(..., description="Safe districts")
    health_tips: List[str] = Field(..., description="Hydration/hygiene tips")

class PackingChecklist(BaseModel):
    essentials: List[str] = Field(..., description="Universal must-pack items")
    seasonal_items: List[str] = Field(..., description="Items for current climate")
    cultural_items: List[str] = Field(..., description="Modest wear, adapters, etc.")


# Main Response Model
class CultureLensResponse(BaseModel):
    destination: DestinationInfo = Field(..., description="Factual destination details")
    summary: str = Field(..., description="High-level culture-oriented summary")
    top_attractions: List[AttractionItem] = Field(..., description="Curated landmark sites")
    hidden_gems: List[HiddenGemItem] = Field(..., description="Lesser-known spots")
    heritage: List[HeritageItem] = Field(..., description="Historic sites and monuments")
    stories: List[StoryItem] = Field(..., description="Tales and legends of the town")
    food: List[FoodItem] = Field(..., description="Culinary recommendations")
    events: List[EventItem] = Field(..., description="Festivals and seasonal activities")
    weather: WeatherOverview = Field(..., description="Factual weather information")
    budget: BudgetOverview = Field(..., description="Budget recommendations")
    itinerary: List[DayPlan] = Field(..., description="Personalized daily itineraries")
    local_phrases: List[PhraseItem] = Field(..., description="Phrasebook entries")
    etiquette: EtiquetteGuide = Field(..., description="Etiquette guide")
    sustainability: SustainabilityTips = Field(..., description="Sustainability tips")
    safety: SafetyGuide = Field(..., description="Safety and emergency rules")
    packing: PackingChecklist = Field(..., description="Customized packing helper checklist")


# Chat Models
class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's new message")
    history: List[ChatMessage] = Field(default=[], description="Chat log history")
    itinerary_context: Optional[CultureLensResponse] = Field(None, description="Current itinerary context")
