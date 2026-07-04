export interface TravelRequest {
  destination: string;
  budget: string;
  duration_days: number;
  travel_style: string;
  companions: string;
  interests: string[];
  languages: string[];
  accessibility_needs: string[];
  food_preference: string;
}

export interface DestinationInfo {
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  currency_code: string;
  timezone: string;
}

export interface AttractionItem {
  name: string;
  hero_image: string;
  location: string;
  latitude: number;
  longitude: number;
  historical_summary: string;
  ai_story: string;
  architecture: string;
  interesting_facts: string[];
  best_visiting_time: string;
  estimated_cost: string;
  travel_duration: string;
  crowd_level: string;
  photography_tips: string;
  nearby_hidden_gem: string;
  accessibility: string;
  map_link: string;
}

export interface HiddenGemItem {
  name: string;
  why_locals_love_it: string;
  interesting_story: string;
  best_time: string;
  nearby_food: string;
  estimated_budget: string;
  photography_spot: string;
}

export interface HeritageItem {
  name: string;
  description: string;
  significance: string;
}

export interface StoryItem {
  title: string;
  narration: string;
  associated_attraction: string;
}

export interface FoodItem {
  dish: string;
  history: string;
  ingredients: string[];
  vegetarian_status: string;
  average_cost: string;
  nearby_area: string;
  dining_etiquette: string;
}

export interface EventItem {
  name: string;
  timing: string;
  description: string;
}

export interface WeatherOverview {
  current_temp: string;
  conditions: string;
  weekly_forecast: string[];
}

export interface BudgetOverview {
  currency: string;
  estimated_daily_cost: string;
  saving_tips: string[];
}

export interface ActivityItem {
  time_slot: string;
  activity_name: string;
  description: string;
  duration: string;
  cost: string;
  category: string;
}

export interface DayPlan {
  day_number: number;
  theme: string;
  activities: ActivityItem[];
}

export interface PhraseItem {
  phrase: string;
  translation: string;
  pronunciation: string;
}

export interface EtiquetteGuide {
  greetings: string;
  dress_code: string;
  photography_rules: string;
  temple_etiquette: string;
  dining_etiquette: string;
  tipping: string;
  local_customs: string;
  common_mistakes: string[];
}

export interface SustainabilityTips {
  public_transport: string;
  walking_routes: string;
  local_businesses: string;
  plastic_reduction: string;
  responsible_tourism: string;
}

export interface SafetyGuide {
  emergency_number: string;
  common_scams: string[];
  safe_neighborhoods: string[];
  health_tips: string[];
}

export interface PackingChecklist {
  essentials: string[];
  seasonal_items: string[];
  cultural_items: string[];
}

export interface CultureLensResponse {
  destination: DestinationInfo;
  summary: string;
  top_attractions: AttractionItem[];
  hidden_gems: HiddenGemItem[];
  heritage: HeritageItem[];
  stories: StoryItem[];
  food: FoodItem[];
  events: EventItem[];
  weather: WeatherOverview;
  budget: BudgetOverview;
  itinerary: DayPlan[];
  local_phrases: PhraseItem[];
  etiquette: EtiquetteGuide;
  sustainability: SustainabilityTips;
  safety: SafetyGuide;
  packing: PackingChecklist;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
  itinerary_context: CultureLensResponse | null;
}
