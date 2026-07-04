import { TravelRequest, CultureLensResponse, ChatMessage, ChatRequest } from "../types/travel";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function generateTravelPlan(request: TravelRequest): Promise<CultureLensResponse> {
  const response = await fetch(`${API_BASE_URL}/api/travel/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `Server returned error status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  itineraryContext: CultureLensResponse | null
): Promise<string> {
  const payload: ChatRequest = {
    message,
    history,
    itinerary_context: itineraryContext,
  };

  const response = await fetch(`${API_BASE_URL}/api/travel/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `Server returned error status ${response.status}`;
    throw new Error(message);
  }

  const data = await response.json();
  return data.reply;
}
