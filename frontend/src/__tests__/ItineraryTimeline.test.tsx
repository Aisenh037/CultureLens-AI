import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ItineraryTimeline } from "../components/ItineraryTimeline";
import { DayPlan, StoryItem } from "../types/travel";

const mockItinerary: DayPlan[] = [
  {
    day_number: 1,
    theme: "Historic Shrines",
    activities: [
      {
        time_slot: "Morning",
        activity_name: "Kinkaku-ji",
        description: "Explore the golden temple structures.",
        duration: "2 hours",
        cost: "400 JPY",
        category: "Heritage"
      },
      {
        time_slot: "Afternoon",
        activity_name: "Nishiki Market",
        description: "Eat local snacks.",
        duration: "1.5 hours",
        cost: "Free entrance",
        category: "Food"
      }
    ]
  },
  {
    day_number: 2,
    theme: "Bamboo Groves",
    activities: [
      {
        time_slot: "Morning",
        activity_name: "Arashiyama",
        description: "Walk the bamboo forest pathways.",
        duration: "3 hours",
        cost: "Free",
        category: "Hidden Gem"
      }
    ]
  }
];

const mockStories: StoryItem[] = [
  {
    title: "Golden Foil Legend",
    narration: "The temple was covered in real gold to ward off bad energy.",
    associated_attraction: "Kinkaku-ji"
  }
];

describe("ItineraryTimeline Component", () => {
  it("renders day tabs and defaults to day 1 content", () => {
    render(<ItineraryTimeline itinerary={mockItinerary} stories={mockStories} />);
    
    expect(screen.getByText("Day 1")).toBeInTheDocument();
    expect(screen.getByText("Day 2")).toBeInTheDocument();
    expect(screen.getByText("Historic Shrines")).toBeInTheDocument();
    expect(screen.getByText("Kinkaku-ji")).toBeInTheDocument();
    expect(screen.getByText("Nishiki Market")).toBeInTheDocument();
  });

  it("switches day content when clicking day tabs", () => {
    render(<ItineraryTimeline itinerary={mockItinerary} stories={mockStories} />);
    
    const day2Button = screen.getByText("Day 2");
    fireEvent.click(day2Button);
    
    expect(screen.getByText("Bamboo Groves")).toBeInTheDocument();
    expect(screen.getByText("Arashiyama")).toBeInTheDocument();
    expect(screen.queryByText("Kinkaku-ji")).not.toBeInTheDocument();
  });

  it("toggles inline secret stories when clicking the Tell me the Story button", () => {
    render(<ItineraryTimeline itinerary={mockItinerary} stories={mockStories} />);
    
    const storyBtn = screen.getByRole("button", { name: /Tell me the Story/i });
    expect(storyBtn).toBeInTheDocument();
    
    // Story should not be visible initially
    expect(screen.queryByText(/Golden Foil Legend/i)).not.toBeInTheDocument();
    
    // Open story
    fireEvent.click(storyBtn);
    expect(screen.getByText(/Golden Foil Legend/i)).toBeInTheDocument();
    expect(screen.getByText(/"The temple was covered in real gold to ward off bad energy."/i)).toBeInTheDocument();
    
    // Close story
    fireEvent.click(storyBtn);
    expect(screen.queryByText(/Golden Foil Legend/i)).not.toBeInTheDocument();
  });
});
