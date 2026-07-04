import json
import google.generativeai as genai
from app.config import settings
from app.schemas.travel import TravelResponse

class GeminiService:
    """Service to interact with Google Gemini API and validate structured JSON output for Travel Guides."""

    def __init__(self):
        # Configure Gemini API client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-3.5-flash")

    def get_travel_plan(self, prompt: str) -> TravelResponse:
        """Fetches the travel plan from Gemini using response_schema constraint."""
        try:
            # We enforce the TravelResponse Pydantic schema using response_schema
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": TravelResponse
            }
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            raw_text = response.text.strip() if response.text else ""
            
            # Since the API guarantees compliance, we can safely load it
            data = json.loads(raw_text)
            return TravelResponse(**data)
        except Exception as e:
            # Fallback retry with raw JSON prompt instruction
            try:
                generation_config = {"response_mime_type": "application/json"}
                response = self.model.generate_content(
                    f"{prompt}\n\nIMPORTANT: Return a JSON conforming to the TravelResponse schema structure.",
                    generation_config=generation_config
                )
                raw_text = response.text.strip() if response.text else ""
                
                # Clean markdown blocks if any
                if raw_text.startswith("```"):
                    lines = raw_text.split("\n")
                    if lines[0].startswith("```json") or lines[0].startswith("```"):
                        raw_text = "\n".join(lines[1:-1])
                
                data = json.loads(raw_text.strip())
                return TravelResponse(**data)
            except Exception as retry_error:
                raise ValueError(
                    f"Gemini travel plan generation failed: {str(retry_error)}"
                ) from e

    def get_chat_response(self, prompt: str) -> str:
        """Gets a conversational response from Gemini for the interactive guide."""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip() if response.text else ""
        except Exception as e:
            raise ValueError(f"Gemini chat response failed: {str(e)}")
