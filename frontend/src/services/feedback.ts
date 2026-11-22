import { campaignSource, visitorId } from "../landing/tracking";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface FeedbackInput {
  helpful: boolean;
  comment?: string;
  destination?: string;
  name?: string;
  email?: string;
  can_quote: boolean;
}

export async function sendFeedback(input: FeedbackInput): Promise<void> {
  const blank = (v?: string) => (v && v.trim() ? v.trim() : undefined);
  const res = await fetch(`${API_BASE_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      kind: "itinerary",
      helpful: input.helpful,
      comment: blank(input.comment),
      destination: blank(input.destination),
      name: blank(input.name),
      email: blank(input.email),
      can_quote: input.can_quote,
      visitor_id: visitorId(),
      source: campaignSource(),
    }),
  });
  if (res.ok) return;
  if (res.status === 422) throw new Error("Please check your email address and try again.");
  if (res.status === 429) throw new Error("Thanks! You've sent a lot of feedback already; please try again later.");
  throw new Error("Couldn't send that right now. Please try again in a minute.");
}
