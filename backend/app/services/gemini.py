import json
import logging
import google.generativeai as genai
from app.config import settings
from app.schemas.travel import CultureLensResponse

logger = logging.getLogger("app.services.gemini")

class GeminiService:
    """Wrapper to interact with the Google Gemini API using structured JSON formats."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Build strict Schema dictionary mapping to bypass Pydantic allOf SDK parser bug
        self.response_schema_dict = {
            "type": "OBJECT",
            "properties": {
                "destination": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING"},
                        "latitude": {"type": "NUMBER"},
                        "longitude": {"type": "NUMBER"},
                        "country": {"type": "STRING"},
                        "currency_code": {"type": "STRING"},
                        "timezone": {"type": "STRING"},
                    },
                    "required": ["name", "latitude", "longitude", "country", "currency_code", "timezone"]
                },
                "summary": {"type": "STRING"},
                "top_attractions": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING"},
                            "hero_image": {"type": "STRING"},
                            "location": {"type": "STRING"},
                            "latitude": {"type": "NUMBER"},
                            "longitude": {"type": "NUMBER"},
                            "historical_summary": {"type": "STRING"},
                            "ai_story": {"type": "STRING"},
                            "architecture": {"type": "STRING"},
                            "interesting_facts": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "best_visiting_time": {"type": "STRING"},
                            "estimated_cost": {"type": "STRING"},
                            "travel_duration": {"type": "STRING"},
                            "crowd_level": {"type": "STRING"},
                            "photography_tips": {"type": "STRING"},
                            "nearby_hidden_gem": {"type": "STRING"},
                            "accessibility": {"type": "STRING"},
                            "map_link": {"type": "STRING"},
                        },
                        "required": [
                            "name", "hero_image", "location", "latitude", "longitude", 
                            "historical_summary", "ai_story", "architecture", "interesting_facts", 
                            "best_visiting_time", "estimated_cost", "travel_duration", "crowd_level", 
                            "photography_tips", "nearby_hidden_gem", "accessibility", "map_link"
                        ]
                    }
                },
                "hidden_gems": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING"},
                            "why_locals_love_it": {"type": "STRING"},
                            "interesting_story": {"type": "STRING"},
                            "best_time": {"type": "STRING"},
                            "nearby_food": {"type": "STRING"},
                            "estimated_budget": {"type": "STRING"},
                            "photography_spot": {"type": "STRING"},
                        },
                        "required": ["name", "why_locals_love_it", "interesting_story", "best_time", "nearby_food", "estimated_budget", "photography_spot"]
                    }
                },
                "heritage": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING"},
                            "description": {"type": "STRING"},
                            "significance": {"type": "STRING"},
                        },
                        "required": ["name", "description", "significance"]
                    }
                },
                "stories": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "title": {"type": "STRING"},
                            "narration": {"type": "STRING"},
                            "associated_attraction": {"type": "STRING"},
                        },
                        "required": ["title", "narration", "associated_attraction"]
                    }
                },
                "food": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "dish": {"type": "STRING"},
                            "history": {"type": "STRING"},
                            "ingredients": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "vegetarian_status": {"type": "STRING"},
                            "average_cost": {"type": "STRING"},
                            "nearby_area": {"type": "STRING"},
                            "dining_etiquette": {"type": "STRING"},
                        },
                        "required": ["dish", "history", "ingredients", "vegetarian_status", "average_cost", "nearby_area", "dining_etiquette"]
                    }
                },
                "events": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING"},
                            "timing": {"type": "STRING"},
                            "description": {"type": "STRING"},
                        },
                        "required": ["name", "timing", "description"]
                    }
                },
                "weather": {
                    "type": "OBJECT",
                    "properties": {
                        "current_temp": {"type": "STRING"},
                        "conditions": {"type": "STRING"},
                        "weekly_forecast": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["current_temp", "conditions", "weekly_forecast"]
                },
                "budget": {
                    "type": "OBJECT",
                    "properties": {
                        "currency": {"type": "STRING"},
                        "estimated_daily_cost": {"type": "STRING"},
                        "saving_tips": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["currency", "estimated_daily_cost", "saving_tips"]
                },
                "itinerary": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "day_number": {"type": "INTEGER"},
                            "theme": {"type": "STRING"},
                            "activities": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "time_slot": {"type": "STRING"},
                                        "activity_name": {"type": "STRING"},
                                        "description": {"type": "STRING"},
                                        "duration": {"type": "STRING"},
                                        "cost": {"type": "STRING"},
                                        "category": {"type": "STRING"},
                                    },
                                    "required": ["time_slot", "activity_name", "description", "duration", "cost", "category"]
                                }
                            }
                        },
                        "required": ["day_number", "theme", "activities"]
                    }
                },
                "local_phrases": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "phrase": {"type": "STRING"},
                            "translation": {"type": "STRING"},
                            "pronunciation": {"type": "STRING"},
                        },
                        "required": ["phrase", "translation", "pronunciation"]
                    }
                },
                "etiquette": {
                    "type": "OBJECT",
                    "properties": {
                        "greetings": {"type": "STRING"},
                        "dress_code": {"type": "STRING"},
                        "photography_rules": {"type": "STRING"},
                        "temple_etiquette": {"type": "STRING"},
                        "dining_etiquette": {"type": "STRING"},
                        "tipping": {"type": "STRING"},
                        "local_customs": {"type": "STRING"},
                        "common_mistakes": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["greetings", "dress_code", "photography_rules", "temple_etiquette", "dining_etiquette", "tipping", "local_customs", "common_mistakes"]
                },
                "sustainability": {
                    "type": "OBJECT",
                    "properties": {
                        "public_transport": {"type": "STRING"},
                        "walking_routes": {"type": "STRING"},
                        "local_businesses": {"type": "STRING"},
                        "plastic_reduction": {"type": "STRING"},
                        "responsible_tourism": {"type": "STRING"},
                    },
                    "required": ["public_transport", "walking_routes", "local_businesses", "plastic_reduction", "responsible_tourism"]
                },
                "safety": {
                    "type": "OBJECT",
                    "properties": {
                        "emergency_number": {"type": "STRING"},
                        "common_scams": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "safe_neighborhoods": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "health_tips": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["emergency_number", "common_scams", "safe_neighborhoods", "health_tips"]
                },
                "packing": {
                    "type": "OBJECT",
                    "properties": {
                        "essentials": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "seasonal_items": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "cultural_items": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["essentials", "seasonal_items", "cultural_items"]
                }
            },
            "required": [
                "destination", "summary", "top_attractions", "hidden_gems", "heritage", 
                "stories", "food", "events", "weather", "budget", "itinerary", 
                "local_phrases", "etiquette", "sustainability", "safety", "packing"
            ]
        }

    async def generate_structured_itinerary(self, prompt: str) -> CultureLensResponse:
        """Invokes Gemini using strict JSON Schema formatting to guarantee keys mapping."""
        try:
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": self.response_schema_dict
            }
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            raw_text = response.text.strip() if response.text else ""
            
            # Clean markdown code blocks if present
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_text = "\n".join(lines[1:-1])
            
            # Load and parse into Pydantic model
            data = json.loads(raw_text.strip())
            return CultureLensResponse(**data)
        except Exception as e:
            logger.exception("Failed to generate structured travel plan JSON.")
            raise ValueError(
                f"Gemini structured response generation failed: {str(e)}"
            ) from e

    async def generate_chat_response(self, prompt: str) -> str:
        """Generates standard conversational text for the interactive tour guide."""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip() if response.text else ""
        except Exception as e:
            logger.exception("Chat response generation failed.")
            raise ValueError(f"Gemini chat failed: {str(e)}")
            
    def list_supported_models(self) -> list:
        """Debugging aid to verify model access."""
        try:
            return [m.name for m in genai.list_models()]
        except Exception:
            return []

