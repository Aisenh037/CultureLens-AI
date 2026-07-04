import React from "react";
import { TravelRequest } from "../types/travel";
import { 
  MapPin, Calendar, Heart, User, Users, Compass, 
  Languages, Accessibility, Utensils, Award 
} from "lucide-react";

interface TravelFormProps {
  formData: TravelRequest;
  errors: { destination?: string; interests?: string };
  loading: boolean;
  onChange: (field: string, value: any) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const TravelForm: React.FC<TravelFormProps> = ({
  formData,
  errors,
  loading,
  onChange,
  onSubmit,
}) => {
  const handleFieldChange = (key: string, value: any) => {
    onChange(key, value);
  };

  const toggleInterest = (interest: string) => {
    const current = formData.interests || [];
    if (current.includes(interest)) {
      handleFieldChange("interests", current.filter((i) => i !== interest));
    } else {
      handleFieldChange("interests", [...current, interest]);
    }
  };

  const toggleLanguage = (lang: string) => {
    const current = formData.languages || [];
    if (current.includes(lang)) {
      handleFieldChange("languages", current.filter((l) => l !== lang));
    } else {
      handleFieldChange("languages", [...current, lang]);
    }
  };

  const toggleAccessibility = (need: string) => {
    const current = formData.accessibility_needs || [];
    if (current.includes(need)) {
      handleFieldChange("accessibility_needs", current.filter((n) => n !== need));
    } else {
      handleFieldChange("accessibility_needs", [...current, need]);
    }
  };

  const styles = [
    { value: "Solo", label: "Solo", icon: User },
    { value: "Couple", label: "Couple", icon: Heart },
    { value: "Family", label: "Family", icon: Users },
    { value: "Friends", label: "Friends", icon: Compass },
  ];

  const budgets = [
    { value: "Budget", label: "Budget", desc: "Backpacker style, local transit" },
    { value: "Mid-range", label: "Mid-range", desc: "Comfort and smart experiences" },
    { value: "Luxury", label: "Luxury", desc: "Premium stays, dining & guides" },
  ];

  const interestsList = [
    { value: "Culture", label: "🏛️ Culture & History" },
    { value: "Adventure", label: "🧗 Adventure & Outdoors" },
    { value: "Nature", label: "🌲 Nature & Scenic" },
    { value: "Food", label: "🍜 Culinary & Foodie" },
    { value: "Shopping", label: "🛍️ Shopping" },
    { value: "Relaxation", label: "💆 Relaxation & Spa" },
  ];

  const langList = ["English", "Japanese", "Spanish", "French", "German", "Hindi", "Mandarin"];
  const accessibilityList = ["Wheelchair Accessible", "Visual Assistance", "Hearing Assistance", "Low Sensory"];

  const foodPrefs = [
    { value: "Vegetarian", label: "🥗 Vegetarian" },
    { value: "Vegan", label: "🌱 Vegan" },
    { value: "Halal", label: "🕌 Halal" },
    { value: "Kosher", label: "🕍 Kosher" },
    { value: "Gluten-Free", label: "🌾 Gluten-Free" },
    { value: "No Restrictions", label: "🍽️ No Restrictions" },
  ];

  return (
    <form
      onSubmit={onSubmit}
      className="backdrop-blur-xl bg-white/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 rounded-3xl p-6 lg:p-8 shadow-md dark:shadow-2xl text-slate-800 dark:text-slate-100 flex flex-col gap-6 relative overflow-hidden transition-all duration-300 hover:shadow-emerald-500/5 hover:border-slate-350 dark:hover:border-slate-700/80"
    >
      <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />
      
      {/* Title */}
      <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800/60 pb-4 mb-2">
        <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400">
          <Award className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Plan Local Exploration</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">Personalize your CultureLens AI profile settings.</p>
        </div>
      </div>

      {/* Destination & Duration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex flex-col gap-2">
          <label htmlFor="destination" className="text-sm font-semibold text-slate-750 dark:text-slate-300 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Where is your destination?
          </label>
          <div className="relative">
            <input
              type="text"
              id="destination"
              value={formData.destination}
              onChange={(e) => handleFieldChange("destination", e.target.value)}
              placeholder="e.g. Kyoto, Japan or Rome, Italy"
              className={`w-full py-3.5 pl-11 pr-4 bg-slate-100/50 dark:bg-slate-950/50 border rounded-xl outline-none focus:ring-2 transition-all font-medium text-sm text-slate-900 dark:text-slate-100 ${
                errors.destination
                  ? "border-rose-500/50 focus:ring-rose-500/25"
                  : "border-slate-250 dark:border-slate-800 focus:border-emerald-500/80 focus:ring-emerald-500/20"
              }`}
            />
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          </div>
          {errors.destination && (
            <p className="text-xs text-rose-500 dark:text-rose-400 mt-1">{errors.destination}</p>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <label htmlFor="duration_days" className="text-sm font-semibold text-slate-750 dark:text-slate-300 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Trip Duration
          </label>
          <div className="flex items-center gap-4 bg-slate-100/50 dark:bg-slate-950/50 border border-slate-250 dark:border-slate-800 rounded-xl p-2">
            <input
              type="range"
              id="duration_days"
              min="1"
              max="14"
              value={formData.duration_days}
              onChange={(e) => handleFieldChange("duration_days", parseInt(e.target.value))}
              className="flex-1 accent-emerald-500 h-1.5 rounded-lg bg-slate-200 dark:bg-slate-800"
            />
            <span className="text-sm font-bold px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-600 dark:text-emerald-400 min-w-[70px] text-center">
              {formData.duration_days} {formData.duration_days === 1 ? "Day" : "Days"}
            </span>
          </div>
        </div>
      </div>

      {/* Travel Style */}
      <div className="flex flex-col gap-3">
        <span className="text-sm font-semibold text-slate-750 dark:text-slate-300">Who are you traveling with?</span>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {styles.map((item) => {
            const Icon = item.icon;
            const isSelected = formData.travel_style === item.value;
            return (
              <button
                type="button"
                key={item.value}
                onClick={() => handleFieldChange("travel_style", item.value)}
                aria-pressed={isSelected}
                className={`flex flex-col items-center justify-center gap-2.5 p-3.5 rounded-2xl border transition-all duration-200 ${
                  isSelected
                    ? "bg-emerald-500/15 border-emerald-500 text-emerald-600 dark:text-emerald-400 shadow-sm"
                    : "bg-slate-100/40 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 hover:text-slate-800 dark:hover:text-slate-200"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-xs font-semibold">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Companions Details */}
      <div className="flex flex-col gap-2">
        <label htmlFor="companions" className="text-sm font-semibold text-slate-750 dark:text-slate-300">Companions Description</label>
        <input
          type="text"
          id="companions"
          value={formData.companions}
          onChange={(e) => handleFieldChange("companions", e.target.value)}
          placeholder="e.g. traveling with spouse, kids aged 5 and 9, or old university friends"
          className="w-full py-3 px-4 bg-slate-100/50 dark:bg-slate-950/50 border border-slate-250 dark:border-slate-800 rounded-xl outline-none focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500/20 text-xs text-slate-800 dark:text-slate-200"
        />
      </div>

      {/* Budget Selector */}
      <div className="flex flex-col gap-3">
        <span className="text-sm font-semibold text-slate-755 dark:text-slate-300">Target Budget</span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {budgets.map((b) => {
            const isSelected = formData.budget === b.value;
            return (
              <button
                type="button"
                key={b.value}
                onClick={() => handleFieldChange("budget", b.value)}
                aria-pressed={isSelected}
                className={`flex flex-col text-left p-3 rounded-xl border transition-all ${
                  isSelected
                    ? "bg-emerald-500/15 border-emerald-500/80 text-emerald-600 dark:text-emerald-400"
                    : "bg-slate-100/40 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800/80 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <span className="text-xs font-bold">{b.label}</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-500 mt-0.5">{b.desc}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Interests Multi-Select */}
      <div className="flex flex-col gap-3">
        <span className="text-sm font-semibold text-slate-750 dark:text-slate-350">Your Interests</span>
        <div className="flex flex-wrap gap-2">
          {interestsList.map((item) => {
            const isSelected = formData.interests.includes(item.value);
            return (
              <button
                type="button"
                key={item.value}
                onClick={() => toggleInterest(item.value)}
                aria-pressed={isSelected}
                className={`px-3 py-2 rounded-lg border text-xs font-medium transition-all ${
                  isSelected
                    ? "bg-emerald-500/15 border-emerald-500 text-emerald-650 dark:text-emerald-400"
                    : "bg-slate-100/40 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
        {errors.interests && (
          <p className="text-xs text-rose-500 dark:text-rose-400">{errors.interests}</p>
        )}
      </div>

      {/* Languages & Accessibility (Split Row) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 border-t border-slate-200 dark:border-slate-800/60">
        
        {/* Preferred Languages */}
        <div className="flex flex-col gap-3">
          <span className="text-sm font-semibold text-slate-750 dark:text-slate-300 flex items-center gap-1.5">
            <Languages className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Preferred Languages
          </span>
          <div className="flex flex-wrap gap-1.5">
            {langList.map((lang) => {
              const isSelected = formData.languages.includes(lang);
              return (
                <button
                  type="button"
                  key={lang}
                  onClick={() => toggleLanguage(lang)}
                  aria-pressed={isSelected}
                  className={`px-2.5 py-1.5 rounded-lg border text-[11px] font-medium transition-all ${
                    isSelected
                      ? "bg-emerald-500/15 border-emerald-500 text-emerald-600 dark:text-emerald-400"
                      : "bg-slate-100/40 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-450 hover:text-slate-800 dark:hover:text-slate-300"
                  }`}
                >
                  {lang}
                </button>
              );
            })}
          </div>
        </div>

        {/* Accessibility Needs */}
        <div className="flex flex-col gap-3">
          <span className="text-sm font-semibold text-slate-750 dark:text-slate-300 flex items-center gap-1.5">
            <Accessibility className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Accessibility Needs
          </span>
          <div className="flex flex-wrap gap-1.5">
            {accessibilityList.map((need) => {
              const isSelected = formData.accessibility_needs.includes(need);
              return (
                <button
                  type="button"
                  key={need}
                  onClick={() => toggleAccessibility(need)}
                  aria-pressed={isSelected}
                  className={`px-2.5 py-1.5 rounded-lg border text-[11px] font-medium transition-all ${
                    isSelected
                      ? "bg-emerald-500/15 border-emerald-500 text-emerald-600 dark:text-emerald-400"
                      : "bg-slate-100/40 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-455 hover:text-slate-800 dark:hover:text-slate-300"
                  }`}
                >
                  {need}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Culinary/Food Preference */}
      <div className="flex flex-col gap-3 pt-2 border-t border-slate-200 dark:border-slate-800/60">
        <span className="text-sm font-semibold text-slate-750 dark:text-slate-300 flex items-center gap-1.5">
          <Utensils className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Culinary & Food Preference
        </span>
        <div className="flex flex-wrap gap-2">
          {foodPrefs.map((pref) => {
            const isSelected = formData.food_preference === pref.value;
            return (
              <button
                type="button"
                key={pref.value}
                onClick={() => handleFieldChange("food_preference", pref.value)}
                aria-pressed={isSelected}
                className={`px-3 py-2 rounded-lg border text-xs font-medium transition-all ${
                  isSelected
                    ? "bg-emerald-500/15 border-emerald-500 text-emerald-600 dark:text-emerald-400"
                    : "bg-slate-100/40 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-405 hover:border-slate-300 dark:hover:border-slate-750"
                }`}
              >
                {pref.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full mt-4 bg-gradient-to-r from-emerald-600 via-teal-500 to-emerald-500 text-slate-950 py-4 px-6 rounded-xl font-extrabold tracking-wider hover:opacity-90 active:scale-[0.99] transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/10"
      >
        {loading ? (
          <>
            <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
            AGGREGATING DATA & GENERATING CultureLens...
          </>
        ) : (
          <>
            <Compass className="w-5 h-5 animate-pulse" />
            DISCOVER LIKE A LOCAL
          </>
        )}
      </button>
    </form>
  );
};
export default TravelForm;
