import { TravelRequest, CultureLensResponse, ChatMessage, ChatRequest } from "../types/travel";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/** Must match MAX_CHAT_HISTORY in backend/app/schemas/travel.py. */
export const MAX_CHAT_HISTORY = 20;

async function errorMessage(response: Response): Promise<string> {
  if (response.status === 429) {
    return "You're sending requests too quickly. Please wait a minute and try again.";
  }
  const errorData = await response.json().catch(() => ({}));
  // FastAPI returns a string for HTTPException and a list for validation errors.
  if (typeof errorData.detail === "string") return errorData.detail;
  if (Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
    return `Invalid input: ${errorData.detail[0].msg}`;
  }
  return `Server returned error status ${response.status}`;
}

export async function generateTravelPlan(request: TravelRequest): Promise<CultureLensResponse> {
  const response = await fetch(`${API_BASE_URL}/api/travel/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(await errorMessage(response));
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
    history: history.slice(-MAX_CHAT_HISTORY),
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
    throw new Error(await errorMessage(response));
  }

  const data = await response.json();
  return data.reply;
}
