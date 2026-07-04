import asyncio
import logging
from app.clients.nominatim import NominatimClient
from app.clients.wikipedia import WikipediaClient
from app.clients.weather import WeatherClient
from app.clients.currency import CurrencyClient
from app.schemas.travel import TravelRequest, CultureLensResponse
from app.services.gemini import GeminiService

logger = logging.getLogger("app.services.orchestrator")

class TravelOrchestrator:
    """Orchestrates validation, factual data retrieval, knowledge aggregation, prompting, and formatting."""

    def __init__(
        self,
        nominatim: NominatimClient,
        wikipedia: WikipediaClient,
        weather: WeatherClient,
        currency: CurrencyClient,
        gemini: GeminiService
    ):
        # Inject dependencies via constructor (SOLID Compliance)
        self.nominatim = nominatim
        self.wikipedia = wikipedia
        self.weather = weather
        self.currency = currency
        self.gemini = gemini

    async def run_pipeline(self, request: TravelRequest) -> CultureLensResponse:
        """Executes the concurrent factual retrieval and AI prompt pipeline."""
        logger.info(f"Starting pipeline for destination: {request.destination}")

        # 1. Resolve coordinates & country (dependency for weather & currency mapping)
        geo_context = await self.nominatim.get_coordinates(request.destination)
        lat = geo_context["latitude"]
        lon = geo_context["longitude"]
        country = geo_context["country"]
        country_code = geo_context["country_code"]

        # 2. Concurrent fetches of Wikipedia summary, search snippets, weather stats, and currency rates
        # Using asyncio.gather for parallel efficiency
        wiki_summary_task = self.wikipedia.get_page_summary(request.destination)
        wiki_heritage_task = self.wikipedia.search_heritage_sites(request.destination)
        weather_task = self.weather.get_forecast(lat, lon)
        currency_rates_task = self.currency.get_usd_exchange_rates()

        wiki_summary, wiki_heritage, weather_data, exchange_rates = await asyncio.gather(
            wiki_summary_task,
            wiki_heritage_task,
            weather_task,
            currency_rates_task
        )

        # 3. Knowledge Aggregator: Merge real context
        # Translate geocoded ISO country code to local currency code
        country_code = geo_context.get("country_code", "US").upper()
        country_to_currency = {
            "US": "USD", "GB": "GBP", "JP": "JPY", "IN": "INR",
            "FR": "EUR", "DE": "EUR", "IT": "EUR", "ES": "EUR",
            "CA": "CAD", "AU": "AUD", "CN": "CNY", "NZ": "NZD",
            "CH": "CHF", "SG": "SGD", "HK": "HKD", "AE": "AED",
            "BR": "BRL", "MX": "MXN", "ZA": "ZAR", "KR": "KRW",
            "TH": "THB", "MY": "MYR", "ID": "IDR", "PH": "PHP",
            "VN": "VND", "RU": "RUB", "TR": "TRY", "SA": "SAR",
            "EG": "EGP", "SE": "SEK", "NO": "NOK", "DK": "DKK",
            "PL": "PLN"
        }
        local_currency = country_to_currency.get(country_code, "USD")
        rate = exchange_rates.get(local_currency, 1.0)
        
        # Prepare factual context block
        factual_context = f"""
FACTUAL DESTINATION DATA:
- Destination Name: {geo_context["name"]}
- Coordinates: Latitude {lat}, Longitude {lon}
- Country: {country} (Currency Code: {local_currency}, Exchange Rate to 1 USD: {rate})
- Weather Context: Temperature: {weather_data["current_temp"]}, Condition: {weather_data["conditions"]}
- Weather Weekly Forecast: {', '.join(weather_data["weekly_forecast"])}
- Wikipedia Historical Overview: {wiki_summary if wiki_summary else 'No details found.'}
- Heritage & Attractions Search Records:
"""
        for i, item in enumerate(wiki_heritage):
            factual_context += f"  * Site: {item['title']} - Summary: {item['snippet']}\n"

        # 4. Prompt Builder: Inject profiles and context constraints
        prompt = self._build_prompt(request, factual_context, geo_context, weather_data["conditions"])

        # 5. Gemini Structured Generation
        logger.info("Calling Gemini structured generation service")
        result = await self.gemini.generate_structured_itinerary(prompt)
        
        # Make sure latitude/longitude are set to real API values to prevent hallucinated markers on map
        result.destination.latitude = lat
        result.destination.longitude = lon
        result.destination.name = geo_context["name"]
        result.destination.country = country
        result.destination.currency_code = local_currency
        
        return result


    def _build_prompt(self, request: TravelRequest, factual_context: str, geo_context: dict, conditions: str) -> str:
        interests_str = ", ".join(request.interests)
        languages_str = ", ".join(request.languages)
        access_str = ", ".join(request.accessibility_needs) if request.accessibility_needs else "None"
        
        return f"""You are a professional local travel planner and cultural heritage archivist. 
Your task is to build a personalized travel guide and itinerary (CultureLens Response) grounded strictly in the provided factual context.

{factual_context}

TRAVELER PREFERENCES & PROFILE:
- Budget Profile: {request.budget}
- Trip Duration: {request.duration_days} days
- Travel Style: {request.travel_style}
- Companion Profile: {request.companions}
- User Interests: {interests_str}
- Preferred Languages: {languages_str}
- Accessibility Requirements: {access_str}
- Food Preference: {request.food_preference}

CRITICAL INSTRUCTIONS:
1. Do NOT hallucinate coordinate details, weather stats, exchange rates, country name, or core historical descriptions. Use the provided FACTUAL DESTINATION DATA.
2. For top_attractions, recommend actual landmarks that are known to exist in the destination (e.g. from the heritage list or wikipedia summary).
3. Ensure every AttractionCard contains the following fields completely filled (no placeholders):
   - name: Landmark name (e.g., Kinkaku-ji)
   - hero_image: Use a reliable image url or a placeholder unsplash search url based on attraction keywords (e.g., 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=800')
   - location: Neighborhood or road
   - latitude: Approximate latitude coordinate of the landmark (must be close to the destination center)
   - longitude: Approximate longitude coordinate of the landmark (must be close to the destination center)
   - historical_summary: Grounded in wikipedia history details
   - ai_story: Immersion story (narrating folklore or architectural legends of the spot)
   - architecture: Detailed style description (e.g., golden foil, wooden architecture)
   - interesting_facts: Bullet details
   - best_visiting_time, estimated_cost, travel_duration, crowd_level, photography_tips, accessibility, nearby_hidden_gem, map_link
4. Build the itinerary matching the traveler's preference and accessibility needs:
   - Match duration ({request.duration_days} days).
   - Divide days into Morning, Afternoon, Evening activities.
   - Ground activities around the attractions and food areas generated.
5. Create a Local Phrasebook containing: Hello, Thank You, Goodbye, Help, Where is..., How much?, Vegetarian Food, Emergency. Provide translation and phonetic pronunciation guides.
6. Provide specific Cultural Etiquette details (dress codes, customs, greetings, temple rules).
7. Suggest sustainable actions (public transport, walking routes, anti-plastic recommendations).
8. Detail local safety information, emergency numbers, and a packing checklist matching the climate ({conditions}).

You MUST return a JSON object that matches the CultureLensResponse schema perfectly. Ensure it is valid JSON and contains no markdown code blocks (like ```json). Respond with the raw JSON string only.
"""
