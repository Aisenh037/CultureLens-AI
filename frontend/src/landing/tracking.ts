import type { WedgeId } from "./wedges";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const VISITOR_KEY = "cl_visitor_id";

/** Anonymous, random, per-browser id. Lets us count unique visitors without cookies or IPs. */
export function visitorId(): string {
  try {
    const existing = localStorage.getItem(VISITOR_KEY);
    if (existing && /^[A-Za-z0-9_-]{8,64}$/.test(existing)) return existing;
    const fresh = crypto.randomUUID().replace(/-/g, "");
    localStorage.setItem(VISITOR_KEY, fresh);
    return fresh;
  } catch {
    // Storage blocked (private mode, embedded view): fall back to a per-page id.
    return crypto.randomUUID().replace(/-/g, "");
  }
}

/** Campaign source from ?utm_source= or ?ref=, limited to the characters the API accepts. */
export function campaignSource(search: string = window.location.search): string | undefined {
  const params = new URLSearchParams(search);
  const raw = params.get("utm_source") || params.get("ref");
  if (!raw) return undefined;
  const clean = raw.replace(/[^A-Za-z0-9_.-]/g, "").slice(0, 100);
  return clean || undefined;
}

export function track(wedge: WedgeId, event: "view" | "pay_click"): void {
  // Fire and forget: analytics must never break the page.
  fetch(`${API_BASE_URL}/api/experiments/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wedge, event, visitor_id: visitorId(), source: campaignSource() }),
    keepalive: true,
  }).catch(() => undefined);
}

export interface SignupInput {
  email: string;
  name?: string;
  role?: string;
  note?: string;
  wants_interview: boolean;
  consent: boolean;
}

export async function joinWaitlist(wedge: WedgeId, input: SignupInput): Promise<void> {
  const blank = (v?: string) => (v && v.trim() ? v.trim() : undefined);
  const res = await fetch(`${API_BASE_URL}/api/experiments/waitlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      wedge,
      email: input.email.trim(),
      name: blank(input.name),
      role: blank(input.role),
      note: blank(input.note),
      wants_interview: input.wants_interview,
      consent: input.consent,
      visitor_id: visitorId(),
      source: campaignSource(),
    }),
  });
  if (res.ok) return;
  if (res.status === 422) throw new Error("Please check your email address and try again.");
  if (res.status === 429) throw new Error("Too many attempts. Please wait a minute and try again.");
  throw new Error("Something went wrong on our side. Please try again later.");
}
