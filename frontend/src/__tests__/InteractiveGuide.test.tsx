import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { InteractiveGuide } from "../components/InteractiveGuide";
import { ChatMessage, CultureLensResponse } from "../types/travel";

const mockChatHistory: ChatMessage[] = [
  { role: "user", content: "Tell me a local legend." },
  { role: "assistant", content: "Kyoto has a story about gold dust." }
];

const mockContext: CultureLensResponse = {
  destination: {
    name: "Kyoto",
    latitude: 35.0,
    longitude: 135.0,
    country: "Japan",
    currency_code: "JPY",
    timezone: "Asia/Tokyo"
  },
  summary: "Culture center",
  top_attractions: [],
  hidden_gems: [],
  heritage: [],
  stories: [],
  food: [],
  events: [],
  weather: {
    current_temp: "20°C",
    conditions: "Sunny",
    weekly_forecast: []
  },
  budget: {
    currency: "JPY",
    estimated_daily_cost: "10000",
    saving_tips: []
  },
  itinerary: [],
  local_phrases: [],
  etiquette: {
    greetings: "Bow",
    dress_code: "Modest",
    photography_rules: "Respect",
    temple_etiquette: "Take off shoes",
    dining_etiquette: "No crossing",
    tipping: "None",
    local_customs: "Low voice",
    common_mistakes: []
  },
  sustainability: {
    public_transport: "Bus",
    walking_routes: "Walk",
    local_businesses: "Traditional Nishiki",
    plastic_reduction: "Flask",
    responsible_tourism: "No Maiko touching"
  },
  safety: {
    emergency_number: "110",
    common_scams: [],
    safe_neighborhoods: [],
    health_tips: []
  },
  packing: {
    essentials: [],
    seasonal_items: [],
    cultural_items: []
  }
};

describe("InteractiveGuide Component", () => {
  it("renders empty state instructions when no conversation is active", () => {
    const handleSendMessage = vi.fn();
    render(
      <InteractiveGuide
        chatHistory={[]}
        itineraryContext={mockContext}
        onSendMessage={handleSendMessage}
        chatLoading={false}
      />
    );

    expect(screen.getByText("Your Local Companion is Ready")).toBeInTheDocument();
    expect(screen.getByText("🌧️ Rainy backup plan")).toBeInTheDocument();
  });

  it("renders messages list and displays bubbles for user and assistant", () => {
    const handleSendMessage = vi.fn();
    render(
      <InteractiveGuide
        chatHistory={mockChatHistory}
        itineraryContext={mockContext}
        onSendMessage={handleSendMessage}
        chatLoading={false}
      />
    );

    expect(screen.getByText("Tell me a local legend.")).toBeInTheDocument();
    expect(screen.getByText("Kyoto has a story about gold dust.")).toBeInTheDocument();
  });

  it("calls onSendMessage when submitting text in input box", () => {
    const handleSendMessage = vi.fn(() => Promise.resolve());
    const { container } = render(
      <InteractiveGuide
        chatHistory={[]}
        itineraryContext={mockContext}
        onSendMessage={handleSendMessage}
        chatLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Ask your local guide anything.../i);
    fireEvent.change(input, { target: { value: "Where is the golden temple?" } });
    
    const sendBtn = container.querySelector('button[type="submit"]')!;
    fireEvent.click(sendBtn);

    expect(handleSendMessage).toHaveBeenCalledWith("Where is the golden temple?");
  });

  it("calls onSendMessage when clicking a quick action bubble suggestion pill", () => {
    const handleSendMessage = vi.fn(() => Promise.resolve());
    render(
      <InteractiveGuide
        chatHistory={[]}
        itineraryContext={mockContext}
        onSendMessage={handleSendMessage}
        chatLoading={false}
      />
    );

    const quickPill = screen.getByText("🌧️ Rainy backup plan");
    fireEvent.click(quickPill);

    expect(handleSendMessage).toHaveBeenCalledWith("It's raining today. What indoor activities do you recommend as a backup?");
  });
});
