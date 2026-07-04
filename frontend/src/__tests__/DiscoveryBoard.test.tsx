import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DiscoveryBoard } from "../components/DiscoveryBoard";
import { AttractionItem, HiddenGemItem, FoodItem, EtiquetteGuide, PhraseItem, SustainabilityTips, SafetyGuide, PackingChecklist, HeritageItem, EventItem } from "../types/travel";

const mockAttractions: AttractionItem[] = [
  {
    name: "Kinkaku-ji",
    hero_image: "https://example.com/gold.jpg",
    location: "Northern Kyoto",
    latitude: 35.0394,
    longitude: 135.7292,
    historical_summary: "A gold covered pavilion.",
    ai_story: "A beautiful gold tower in Kyoto.",
    architecture: "Muromachi Zen style",
    interesting_facts: ["Fact 1", "Fact 2"],
    best_visiting_time: "Morning",
    estimated_cost: "400 JPY",
    travel_duration: "1 hour",
    crowd_level: "High",
    photography_tips: "Shoot from across the pond",
    nearby_hidden_gem: "Daitoku-ji",
    accessibility: "Wheelchair accessible paths",
    map_link: "https://maps.google.com/?q=Kinkaku-ji"
  }
];

const mockHiddenGems: HiddenGemItem[] = [
  {
    name: "Otagi Nenbutsu-ji",
    why_locals_love_it: "1200 quirky stone statues.",
    interesting_story: "Statues carved by local citizens.",
    best_time: "Evening",
    nearby_food: "Traditional Soba",
    estimated_budget: "300 JPY",
    photography_spot: "Statue row"
  }
];

const mockHeritage: HeritageItem[] = [];

const mockFood: FoodItem[] = [
  {
    dish: "Yudofu",
    history: "Buddhist temple origins.",
    ingredients: ["Tofu", "Kombu dashi"],
    vegetarian_status: "Yes",
    average_cost: "2000 JPY",
    nearby_area: "Arashiyama",
    dining_etiquette: "Eat warm with green onions."
  }
];

const mockEtiquette: EtiquetteGuide = {
  greetings: "Bow politely",
  dress_code: "Modest wear",
  photography_rules: "Respect signposts",
  temple_etiquette: "Take off shoes",
  dining_etiquette: "Do not pass chopsticks",
  tipping: "No tipping",
  local_customs: "Keep voice down",
  common_mistakes: ["Eating on the go"]
};

const mockPhrases: PhraseItem[] = [
  {
    phrase: "Thank you",
    translation: "Arigatou",
    pronunciation: "Ah-ree-gah-toe"
  }
];

const mockSustainability: SustainabilityTips = {
  public_transport: "Take City Bus 205",
  walking_routes: "Walk along temples path",
  local_businesses: "Buy Nishiki street food",
  plastic_reduction: "Carry water flasks",
  responsible_tourism: "Do not touch Maiko sleeves"
};

const mockSafety: SafetyGuide = {
  emergency_number: "119",
  common_scams: ["Fake taxi charges"],
  safe_neighborhoods: ["Kamigyo"],
  health_tips: ["Drink tea"]
};

const mockPacking: PackingChecklist = {
  essentials: ["Passport"],
  seasonal_items: ["Rain poncho"],
  cultural_items: ["Easy slip-on shoes"]
};

const mockEvents: EventItem[] = [
  {
    name: "Gion Matsuri",
    timing: "July 1-31",
    description: "A month-long festival featuring massive wooden floats passing through downtown Kyoto."
  }
];

describe("DiscoveryBoard Component", () => {
  it("renders tabs correctly and defaults to sights section", () => {
    render(
      <DiscoveryBoard
        attractions={mockAttractions}
        hiddenGems={mockHiddenGems}
        heritage={mockHeritage}
        food={mockFood}
        etiquette={mockEtiquette}
        phrases={mockPhrases}
        sustainability={mockSustainability}
        safety={mockSafety}
        packing={mockPacking}
        events={mockEvents}
      />
    );

    expect(screen.getByText("🏛️ Sights & Gems")).toBeInTheDocument();
    expect(screen.getByText("🍜 Food & Culture")).toBeInTheDocument();
    expect(screen.getByText("💼 Practical Guide")).toBeInTheDocument();
    
    // Default sights view checks
    expect(screen.getByText("Kinkaku-ji")).toBeInTheDocument();
    expect(screen.getByText("Otagi Nenbutsu-ji")).toBeInTheDocument();
    expect(screen.getByText("A gold covered pavilion.")).toBeInTheDocument();
  });

  it("switches to Food & Culture tab when clicked", () => {
    render(
      <DiscoveryBoard
        attractions={mockAttractions}
        hiddenGems={mockHiddenGems}
        heritage={mockHeritage}
        food={mockFood}
        etiquette={mockEtiquette}
        phrases={mockPhrases}
        sustainability={mockSustainability}
        safety={mockSafety}
        packing={mockPacking}
        events={mockEvents}
      />
    );

    const foodTab = screen.getByText("🍜 Food & Culture");
    fireEvent.click(foodTab);

    expect(screen.getByText("Yudofu")).toBeInTheDocument();
    expect(screen.getByText(/Religious Sites/i)).toBeInTheDocument();
    expect(screen.getByText("Eating on the go")).toBeInTheDocument();
  });

  it("switches to Practical Guide tab when clicked", () => {
    render(
      <DiscoveryBoard
        attractions={mockAttractions}
        hiddenGems={mockHiddenGems}
        heritage={mockHeritage}
        food={mockFood}
        etiquette={mockEtiquette}
        phrases={mockPhrases}
        sustainability={mockSustainability}
        safety={mockSafety}
        packing={mockPacking}
        events={mockEvents}
      />
    );

    const practicalTab = screen.getByText("💼 Practical Guide");
    fireEvent.click(practicalTab);

    // Phrases check
    expect(screen.getByText("Arigatou")).toBeInTheDocument();
    // Sustainability check
    expect(screen.getByText("Take City Bus 205")).toBeInTheDocument();
    // Safety check
    expect(screen.getByText("119")).toBeInTheDocument();
    // Packing checklist
    expect(screen.getByText("✓ Passport")).toBeInTheDocument();
    // Events check
    expect(screen.getByText("Gion Matsuri")).toBeInTheDocument();
    expect(screen.getByText(/A month-long festival featuring massive wooden floats/i)).toBeInTheDocument();
  });
});
