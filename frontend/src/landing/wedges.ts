export type WedgeId = "travellers-abroad" | "tour-operators" | "heritage-stories";

export interface WedgeConfig {
  id: WedgeId;
  eyebrow: string;
  headline: string;
  sub: string;
  pains: string[];
  features: { title: string; body: string }[];
  price: { amount: string; unit: string; button: string };
  roleLabel: string;
  rolePlaceholder: string;
  notePlaceholder: string;
}

export const WEDGES: Record<WedgeId, WedgeConfig> = {
  "travellers-abroad": {
    id: "travellers-abroad",
    eyebrow: "For Indians travelling abroad",
    headline: "Your first trip abroad, planned like a local friend would.",
    sub: "Day-by-day plans that account for veg and Jain food, rupee budgets, visa-friendly pacing and the cultural do's and don'ts nobody tells you.",
    pains: [
      "Finding vegetarian food that isn't just salad",
      "Budgeting in rupees when every price is in euros or yen",
      "Not knowing what's rude, what's a scam, what's closed on Mondays",
    ],
    features: [
      { title: "Food you can actually eat", body: "Veg, Jain and halal-friendly picks near every stop." },
      { title: "Costs in ₹", body: "Daily spend converted at live rates, so you know before you go." },
      { title: "Culture notes", body: "Tipping, dress codes, etiquette and common tourist traps." },
    ],
    price: { amount: "₹99", unit: "per trip plan", button: "Get my trip plan — ₹99" },
    roleLabel: "Who's travelling?",
    rolePlaceholder: "e.g. student, couple, family with parents",
    notePlaceholder: "Where are you going, and when?",
  },
  "tour-operators": {
    id: "tour-operators",
    eyebrow: "For tour operators and travel agents",
    headline: "Client-ready itineraries in minutes, not evenings.",
    sub: "Generate branded, day-by-day itineraries with real weather, maps and local context — then edit and send them to clients under your name.",
    pains: [
      "Hours spent rewriting the same itinerary for every client",
      "Clients asking for 'something more local' than the standard package",
      "PDFs that look dated next to online booking sites",
    ],
    features: [
      { title: "Your brand, not ours", body: "Logo, colours and contact details on every itinerary." },
      { title: "Edit before you send", body: "Swap stops, reorder days, add your own notes and prices." },
      { title: "Share as a link or PDF", body: "Clients open it on their phone; you see when they do." },
    ],
    price: { amount: "₹2,999", unit: "per month, unlimited itineraries", button: "Start for ₹2,999/month" },
    roleLabel: "Your business",
    rolePlaceholder: "e.g. agency name, city, trips per month",
    notePlaceholder: "What takes the most time when you build an itinerary?",
  },
  "heritage-stories": {
    id: "heritage-stories",
    eyebrow: "For heritage lovers and heritage sites",
    headline: "Every monument has a story. Hear it while you stand there.",
    sub: "Short audio stories for India's heritage sites — the history, the legends and the details guides skip — in English and Hindi, on your phone.",
    pains: [
      "Plaques with two lines of text for a 500-year-old building",
      "Guides who rush, or aren't available when you visit",
      "Audio guides that are dry, outdated or need a rented device",
    ],
    features: [
      { title: "Stories, not lectures", body: "Five to ten minute chapters you play as you walk." },
      { title: "English and Hindi", body: "More Indian languages as sites sign up." },
      { title: "Works offline", body: "Download before you go; no signal needed inside the fort." },
    ],
    price: { amount: "₹49", unit: "per site", button: "Get the audio tour — ₹49" },
    roleLabel: "You are a…",
    rolePlaceholder: "e.g. visitor, student, site manager, guide",
    notePlaceholder: "Which site would you want a story for first?",
  },
};
