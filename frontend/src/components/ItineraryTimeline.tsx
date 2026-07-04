import React, { useState } from "react";
import { DayPlan, StoryItem } from "../types/travel";
import { Clock, DollarSign, BookOpen, MapPin, Compass, Utensils, Star, Sunrise, Sun, Sunset } from "lucide-react";

interface ItineraryTimelineProps {
  itinerary: DayPlan[];
  stories: StoryItem[];
}

export const ItineraryTimeline: React.FC<ItineraryTimelineProps> = ({
  itinerary,
  stories,
}) => {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [expandedStoryIndex, setExpandedStoryIndex] = useState<string | null>(null);

  if (!itinerary || itinerary.length === 0) return null;

  const currentDay = itinerary[selectedDayIndex];

  const findStoryForActivity = (activityName: string): StoryItem | undefined => {
    if (!stories) return undefined;
    return stories.find(
      (s) =>
        s.associated_attraction.toLowerCase().includes(activityName.toLowerCase()) ||
        activityName.toLowerCase().includes(s.associated_attraction.toLowerCase())
    );
  };

  const getSlotIcon = (slot: string) => {
    switch (slot.toLowerCase()) {
      case "morning":
        return <Sunrise className="w-4 h-4 text-amber-500 dark:text-amber-400" />;
      case "afternoon":
        return <Sun className="w-4 h-4 text-orange-500 dark:text-orange-400" />;
      case "evening":
        return <Sunset className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-500 dark:text-slate-400" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case "heritage":
        return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30";
      case "hidden gem":
        return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-450 border-emerald-500/30";
      case "food":
        return "bg-rose-500/10 text-rose-600 dark:text-rose-450 border-rose-500/30";
      default:
        return "bg-teal-500/10 text-teal-600 dark:text-teal-400 border-teal-500/30";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case "heritage":
        return <BookOpen className="w-3 h-3" />;
      case "hidden gem":
        return <Compass className="w-3 h-3" />;
      case "food":
        return <Utensils className="w-3 h-3" />;
      default:
        return <Star className="w-3 h-3" />;
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 rounded-3xl p-5 shadow-md dark:shadow-xl flex flex-col gap-6 text-slate-800 dark:text-slate-100">
      
      {/* Header */}
      <div className="flex flex-col gap-1 border-b border-slate-200 dark:border-slate-800/60 pb-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-650 dark:text-emerald-400" />
            Personalized Daily Route
          </h2>
          <span className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-950 px-2 py-0.5 rounded-full border border-slate-250 dark:border-slate-850">
            {itinerary.length} {itinerary.length === 1 ? "Day" : "Days"}
          </span>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Your daily schedule matched to interests and pace constraints.
        </p>
      </div>

      {/* Day Toggles */}
      <div role="tablist" aria-label="Day selection" className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
        {itinerary.map((day, idx) => (
          <button
            role="tab"
            id={`day-tab-${day.day_number}`}
            aria-selected={selectedDayIndex === idx}
            aria-controls={`day-panel-${day.day_number}`}
            key={day.day_number}
            onClick={() => {
              setSelectedDayIndex(idx);
              setExpandedStoryIndex(null);
            }}
            className={`px-3.5 py-2 rounded-lg border text-xs font-bold whitespace-nowrap transition-all ${
              selectedDayIndex === idx
                ? "bg-emerald-600 text-slate-950 dark:text-slate-955 border-emerald-500 shadow-md shadow-emerald-500/10"
                : "bg-slate-100 dark:bg-slate-950/40 border-slate-200 dark:border-slate-850 text-slate-650 dark:text-slate-450 hover:border-slate-350 dark:hover:border-slate-800 hover:text-slate-900 dark:hover:text-slate-200"
            }`}
          >
            Day {day.day_number}
          </button>
        ))}
      </div>

      {/* Daily theme & Timeline Panel */}
      <div 
        id={`day-panel-${currentDay.day_number}`} 
        role="tabpanel" 
        aria-labelledby={`day-tab-${currentDay.day_number}`}
        className="flex flex-col gap-6"
      >
        {/* Daily theme */}
        <div className="bg-slate-100 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-855 p-3 rounded-xl">
          <span className="text-[9px] font-bold tracking-widest text-emerald-600 dark:text-emerald-450 uppercase">Focus Theme</span>
          <h3 className="text-xs font-bold text-slate-700 dark:text-slate-300 mt-0.5">{currentDay.theme}</h3>
        </div>

        {/* Vertical Timeline */}
        <div className="flex flex-col relative before:absolute before:top-2 before:bottom-2 before:left-[14px] before:w-[1px] before:bg-slate-250 dark:before:bg-slate-850 gap-6 mt-1">
        {currentDay.activities.map((act, idx) => {
          const matchStory = findStoryForActivity(act.activity_name);
          const isStoryExpanded = expandedStoryIndex === `${selectedDayIndex}-${idx}`;

          return (
            <div key={idx} className="flex gap-4 items-start relative group">
              
              {/* Timeline slot indicator */}
              <div className="w-7 h-7 rounded-lg bg-white dark:bg-slate-950 border border-slate-250 dark:border-slate-850 flex items-center justify-center z-10 group-hover:border-emerald-500/40 transition-colors">
                {getSlotIcon(act.time_slot)}
              </div>

              {/* Card Container */}
              <div className="flex-1 bg-white/80 dark:bg-slate-950/15 border border-slate-200 dark:border-slate-850 rounded-xl p-4 hover:border-slate-300 dark:hover:border-slate-800 transition-all duration-200 shadow-sm">
                
                {/* Top Row */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-850/60 pb-2 mb-2">
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500">
                      {act.time_slot}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                      {act.activity_name}
                    </h4>
                  </div>
                  <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase tracking-wider ${getCategoryColor(act.category)}`}>
                    {getCategoryIcon(act.category)}
                    {act.category}
                  </span>
                </div>

                {/* Description */}
                <p className="text-xs text-slate-650 dark:text-slate-400 leading-relaxed mb-3">
                  {act.description}
                </p>

                {/* Specs Row */}
                <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500 dark:text-slate-500 font-medium pt-2 border-t border-slate-200 dark:border-slate-850/30">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-450" />
                      {act.duration}
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-450" />
                      {act.cost}
                    </span>
                  </div>

                  {/* Story button */}
                  {matchStory && (
                    <button
                      onClick={() =>
                        setExpandedStoryIndex(
                          isStoryExpanded ? null : `${selectedDayIndex}-${idx}`
                        )
                      }
                      className="flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-500/5 hover:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 active:scale-95 transition-all font-semibold"
                    >
                      <BookOpen className="w-3 h-3" />
                      {isStoryExpanded ? "Hide Story" : "Tell me the Story"}
                    </button>
                  )}
                </div>

                {/* Accordion Story Mode */}
                {matchStory && isStoryExpanded && (
                  <div className="mt-3 p-3.5 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/10 border border-emerald-500/25 text-slate-800 dark:text-slate-300 animate-slide-down">
                    <h5 className="text-[10px] uppercase font-bold tracking-widest text-emerald-700 dark:text-emerald-450 mb-1">
                      📖 {matchStory.title}
                    </h5>
                    <p className="text-xs italic leading-relaxed text-slate-700 dark:text-slate-350">
                      "{matchStory.narration}"
                    </p>
                  </div>
                )}
              </div>

            </div>
          );
        })}
      </div>
    </div>
    </div>
  );
};
export default ItineraryTimeline;
