import json
import logging
import google.generativeai as genai
from app.config import settings
from app.schemas.travel import CultureLensResponse

logger = logging.getLogger("app.services.gemini")

class GeminiService:
    """Wrapper to interact with the Google Gemini API using native schemas."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate_structured_itinerary(self, prompt: str) -> CultureLensResponse:
        """Invokes Gemini using response_schema to guarantee validation."""
        try:
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": CultureLensResponse
            }
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            raw_text = response.text.strip() if response.text else ""
            
            # Load and parse JSON
            data = json.loads(raw_text)
            return CultureLensResponse(**data)
        except Exception as e:
            logger.exception("Failed to generate structured travel plan using response_schema.")
            
            # Fallback parsing retry
            try:
                generation_config = {"response_mime_type": "application/json"}
                response = self.model.generate_content(
                    f"{prompt}\n\nIMPORTANT: Return a JSON object matching the CultureLensResponse schema perfectly.",
                    generation_config=generation_config
                )
                raw_text = response.text.strip() if response.text else ""
                
                # Clean markdown format blocks if any
                if raw_text.startswith("```"):
                    lines = raw_text.split("\n")
                    if lines[0].startswith("```json") or lines[0].startswith("```"):
                        raw_text = "\n".join(lines[1:-1])
                
                data = json.loads(raw_text.strip())
                return CultureLensResponse(**data)
            except Exception as retry_error:
                raise ValueError(
                    f"Gemini structured response generation failed: {str(retry_error)}"
                ) from e

    def generate_chat_response(self, prompt: str) -> str:
        """Generates standard conversational text for the interactive tour guide."""
        try:
            response = self.model.generate_content(prompt)
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
