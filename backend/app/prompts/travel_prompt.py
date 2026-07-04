from app.schemas.travel import TravelRequest, ChatMessage, CultureLensResponse
from typing import List, Optional

def build_chat_prompt(message: str, history: List[ChatMessage], itinerary_context: Optional[CultureLensResponse]) -> str:
    """Builds the prompt instructing Gemini on how to act as the Interactive AI Travel Guide."""
    
    context_str = ""
    if itinerary_context:
        # Compress context representation to save tokens and improve latency/efficiency
        days_str = []
        for day in itinerary_context.itinerary:
            act_names = [f"{act.time_slot}: {act.activity_name} ({act.category})" for act in day.activities]
            days_str.append(f"Day {day.day_number} ({day.theme}): " + ", ".join(act_names))
            
        gems = [g.name for g in itinerary_context.hidden_gems]
        heritage = [h.name for h in itinerary_context.heritage]
        food = [f.dish for f in itinerary_context.food]
        
        days_formatted = "\n  * ".join(days_str)
        
        context_str = f"""
CURRENT ITINERARY CONTEXT:
- Destination: {itinerary_context.destination.name}
- Major Heritage spots: {', '.join(heritage)}
- Hidden Gems: {', '.join(gems)}
- Traditional dishes: {', '.join(food)}
- Itinerary Schedule:
  * {days_formatted}
"""

    history_str = ""
    for msg in history:
        history_str += f"{msg.role.upper()}: {msg.content}\n"
        
    return f"""You are an enthusiastic, knowledgeable, and friendly interactive AI Tour Guide. 
Your goal is to help the traveler explore their destination, answering questions, giving insider recommendations, sharing folklore/stories, explaining cultural quirks, or offering real-time assistance (like rain backups or meal suggestions).

Be engaging, warm, and highly informative, using local expressions where appropriate. Keep your answers concise, structured, and easy to read on a mobile app screen (use markdown bullet points, bold text).

{context_str}

CONVERSATION HISTORY:
{history_str}
USER: {message}
ASSISTANT (Local Guide):"""
