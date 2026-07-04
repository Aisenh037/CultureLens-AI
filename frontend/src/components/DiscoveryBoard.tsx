import React, { useState } from "react";
import { 
  AttractionItem, HiddenGemItem, FoodItem, EtiquetteGuide, 
  PhraseItem, SustainabilityTips, SafetyGuide, PackingChecklist, HeritageItem 
} from "../types/travel";
import { 
  Compass, HeartHandshake, Utensils, AlertTriangle, 
  Languages, Volume2, ShieldAlert, Leaf, CheckSquare, Camera, Sparkles, Accessibility 
} from "lucide-react";

interface DiscoveryBoardProps {
  attractions: AttractionItem[];
  hiddenGems: HiddenGemItem[];
  heritage: HeritageItem[];
  food: FoodItem[];
  etiquette: EtiquetteGuide;
  phrases: PhraseItem[];
  sustainability: SustainabilityTips;
  safety: SafetyGuide;
  packing: PackingChecklist;
}

export const DiscoveryBoard: React.FC<DiscoveryBoardProps> = ({
  attractions,
  hiddenGems,
  heritage,
  food,
  etiquette,
  phrases,
  sustainability,
  safety,
  packing,
}) => {
  const [activeTab, setActiveTab] = useState<"sights" | "cuisine" | "practical">("sights");
  const [expandedAttraction, setExpandedAttraction] = useState<number | null>(null);

  return (
    <div className="backdrop-blur-xl bg-white/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 rounded-3xl p-5 shadow-md dark:shadow-xl text-slate-800 dark:text-slate-100 flex flex-col gap-6">
      
      {/* Header */}
      <div className="flex flex-col gap-1 border-b border-slate-200 dark:border-slate-800/60 pb-3">
        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Compass className="w-5 h-5 text-emerald-600 dark:text-emerald-450" />
          AI Local Discovery Board
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Explore attractions, local foods, cultural customs, phrases, and safety parameters.
        </p>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-3 bg-slate-100 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-850 p-1.5 rounded-2xl">
        <button
          onClick={() => setActiveTab("sights")}
          aria-pressed={activeTab === "sights"}
          className={`py-2 px-1 rounded-xl text-xs font-bold transition-all ${
            activeTab === "sights"
              ? "bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 border border-slate-200 dark:border-slate-800 shadow-sm"
              : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-350"
          }`}
        >
          🏛️ Sights & Gems
        </button>
        <button
          onClick={() => setActiveTab("cuisine")}
          aria-pressed={activeTab === "cuisine"}
          className={`py-2 px-1 rounded-xl text-xs font-bold transition-all ${
            activeTab === "cuisine"
              ? "bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 border border-slate-200 dark:border-slate-800 shadow-sm"
              : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-350"
          }`}
        >
          🍜 Food & Culture
        </button>
        <button
          onClick={() => setActiveTab("practical")}
          aria-pressed={activeTab === "practical"}
          className={`py-2 px-1 rounded-xl text-xs font-bold transition-all ${
            activeTab === "practical"
              ? "bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 border border-slate-200 dark:border-slate-800 shadow-sm"
              : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-350"
          }`}
        >
          💼 Practical Guide
        </button>
      </div>

      {/* Tab 1: Sights & Gems */}
      {activeTab === "sights" && (
        <div className="flex flex-col gap-6 animate-fade-in">
          {/* Heritage Explorer */}
          {heritage && heritage.length > 0 && (
            <div className="bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl flex flex-col gap-3">
              <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-455 uppercase tracking-widest flex items-center gap-1.5">
                📜 Heritage Explorer
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {heritage.map((h, i) => (
                  <div key={i} className="bg-white/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-850 p-3 rounded-xl">
                    <h4 className="text-xs font-bold text-amber-600 dark:text-amber-400">{h.name}</h4>
                    <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">{h.description}</p>
                    <p className="text-[10px] italic text-slate-500 mt-1 border-t border-slate-200 dark:border-slate-850/30 pt-1.5">
                      Sig: {h.significance}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Attractions Grid */}
          <div className="flex flex-col gap-4">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">Top Recommended Attractions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {attractions.map((attr, idx) => {
                const isExpanded = expandedAttraction === idx;
                return (
                  <div key={idx} className="bg-white/60 dark:bg-slate-955/40 border border-slate-200 dark:border-slate-850 rounded-2xl overflow-hidden transition-all duration-200 hover:border-slate-350 dark:hover:border-slate-800 flex flex-col shadow-sm">
                    {/* Hero Image */}
                    <div className="h-32 w-full relative overflow-hidden bg-slate-900">
                      <img 
                        src={attr.hero_image} 
                        alt={attr.name}
                        className="w-full h-full object-cover opacity-80"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800";
                        }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950 to-transparent" />
                      <div className="absolute bottom-2.5 left-3.5 right-3.5 flex items-end justify-between">
                        <span className="text-xs font-bold text-white drop-shadow-md">{attr.name}</span>
                        <span className="text-[9px] font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-350 px-2 py-0.5 rounded drop-shadow">
                          {attr.location}
                        </span>
                      </div>
                    </div>

                    {/* Quick Specs */}
                    <div className="p-4 flex flex-col gap-2.5 flex-1">
                      <p className="text-xs text-slate-650 dark:text-slate-350 leading-relaxed">
                        {attr.historical_summary}
                      </p>

                      <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 dark:text-slate-550 mt-1">
                        <div>🕒 Stay: {attr.travel_duration}</div>
                        <div>💰 Cost: {attr.estimated_cost}</div>
                        <div>👥 Crowd: {attr.crowd_level}</div>
                        <div>☀️ Best Time: {attr.best_visiting_time}</div>
                      </div>

                      {/* Expand details */}
                      <button
                        onClick={() => setExpandedAttraction(isExpanded ? null : idx)}
                        className="mt-2 text-left text-[10px] font-bold text-emerald-600 dark:text-emerald-450 hover:underline flex items-center gap-1 self-start"
                      >
                        {isExpanded ? "Show Less" : "Show Full Description & Architecture Details"}
                      </button>

                      {isExpanded && (
                        <div className="flex flex-col gap-2 mt-3 pt-3 border-t border-slate-200 dark:border-slate-850/50 animate-slide-down">
                          <div className="bg-emerald-50/50 dark:bg-emerald-950/10 border border-emerald-550/15 p-2.5 rounded-lg">
                            <span className="text-[9px] uppercase font-bold text-emerald-650 dark:text-emerald-450 flex items-center gap-1">
                              <Sparkles className="w-3 h-3" /> Immersive Story
                            </span>
                            <p className="text-[11px] text-slate-700 dark:text-slate-300 italic mt-1 leading-relaxed">"{attr.ai_story}"</p>
                          </div>
                          <div>
                            <span className="text-[9px] uppercase font-bold text-slate-500 dark:text-slate-400">🏛️ Architectural Details</span>
                            <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5">{attr.architecture}</p>
                          </div>
                          <div>
                            <span className="text-[9px] uppercase font-bold text-slate-550 dark:text-slate-400 flex items-center gap-1">
                              <Camera className="w-3 h-3 text-emerald-600 dark:text-emerald-400" /> Photography Tip
                            </span>
                            <p className="text-[11px] text-slate-605 dark:text-slate-400 mt-0.5">{attr.photography_tips}</p>
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1 pt-1.5 border-t border-slate-200 dark:border-slate-850/20">
                            <span className="flex items-center gap-1"><Accessibility className="w-3 h-3" /> {attr.accessibility}</span>
                            <a href={attr.map_link} target="_blank" rel="noopener noreferrer" className="text-emerald-600 dark:text-emerald-400 hover:underline">View Map</a>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Hidden Gems List */}
          <div className="bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl flex flex-col gap-4">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-emerald-650 dark:text-emerald-455 animate-spin-slow" />
              Off-the-Beaten-Path Hidden Gems
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {hiddenGems.map((gem, idx) => (
                <div key={idx} className="bg-white/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-850 p-4 rounded-xl flex flex-col gap-2 shadow-sm">
                  <h4 className="text-xs font-bold text-emerald-650 dark:text-emerald-400">{gem.name}</h4>
                  <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">{gem.why_locals_love_it}</p>
                  
                  <div className="bg-slate-50 dark:bg-slate-950/60 p-2.5 rounded-lg mt-1 text-[10px] border border-slate-200 dark:border-slate-850">
                    <span className="font-bold text-emerald-650 dark:text-emerald-450">Story & Myth:</span>
                    <p className="italic text-slate-600 dark:text-slate-400 mt-0.5">"{gem.interesting_story}"</p>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 dark:text-slate-550 mt-1.5 pt-2 border-t border-slate-200 dark:border-slate-850/30">
                    <div>🕒 Best time: {gem.best_time}</div>
                    <div>💰 Budget: {gem.estimated_budget}</div>
                    <div>📸 Photospot: {gem.photography_spot}</div>
                    <div>🍜 Nearby Food: {gem.nearby_food}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Food & Culture */}
      {activeTab === "cuisine" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
          {/* Foods list */}
          <div className="flex flex-col gap-4 bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-855/60">
              <Utensils className="w-4 h-4 text-rose-500 dark:text-rose-450" />
              Authentic Local Cuisine
            </h3>
            {food.map((item, idx) => (
              <div key={idx} className="bg-white/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-850 p-3.5 rounded-xl flex flex-col gap-2 shadow-sm">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-rose-600 dark:text-rose-400">{item.dish}</h4>
                  <span className="text-[9px] font-bold bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 px-2 py-0.5 rounded">
                    {item.vegetarian_status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">{item.history}</p>
                <div className="text-[10px] text-slate-500 mt-1 border-t border-slate-200 dark:border-slate-850/30 pt-2 flex flex-col gap-1.5">
                  <div>🛒 <span className="font-bold text-slate-700 dark:text-slate-400">Ingredients:</span> {item.ingredients.join(", ")}</div>
                  <div>💰 <span className="font-bold text-slate-700 dark:text-slate-400">Estimated Cost:</span> {item.average_cost} (Find near: {item.nearby_area})</div>
                  <div className="bg-rose-50 dark:bg-rose-955/10 border border-rose-200 dark:border-rose-500/15 p-2 rounded text-slate-700 dark:text-slate-350">
                    🥢 <span className="font-bold text-rose-700 dark:text-rose-400">Etiquette:</span> {item.dining_etiquette}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Social Etiquette Guide */}
          <div className="flex flex-col gap-4 bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-850/60">
              <HeartHandshake className="w-4 h-4 text-emerald-650 dark:text-emerald-450" />
              Social Customs & Etiquette
            </h3>
            
            <div className="flex flex-col gap-3.5 text-xs text-slate-650 dark:text-slate-350">
              <div>
                <span className="font-bold text-emerald-700 dark:text-emerald-400 uppercase text-[10px] tracking-wider block mb-0.5">Greetings:</span>
                <p className="leading-relaxed">{etiquette.greetings}</p>
              </div>
              <div>
                <span className="font-bold text-emerald-700 dark:text-emerald-400 uppercase text-[10px] tracking-wider block mb-0.5">Dress Code:</span>
                <p className="leading-relaxed">{etiquette.dress_code}</p>
              </div>
              <div>
                <span className="font-bold text-emerald-700 dark:text-emerald-400 uppercase text-[10px] tracking-wider block mb-0.5">Religious Sites (Temples/Shrines):</span>
                <p className="leading-relaxed">{etiquette.temple_etiquette}</p>
              </div>
              <div>
                <span className="font-bold text-emerald-700 dark:text-emerald-400 uppercase text-[10px] tracking-wider block mb-0.5">Tipping Norms:</span>
                <p className="leading-relaxed">{etiquette.tipping}</p>
              </div>
              
              <div className="bg-rose-50 dark:bg-rose-950/10 border border-rose-200 dark:border-rose-500/15 p-3 rounded-xl flex flex-col gap-2 mt-1 shadow-sm">
                <span className="text-[10px] font-bold text-rose-650 dark:text-rose-400 uppercase flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-500" /> Common Tourist Mistakes
                </span>
                <ul className="list-disc list-inside text-[11px] text-slate-600 dark:text-slate-400 flex flex-col gap-1.5">
                  {etiquette.common_mistakes.map((m, i) => (
                    <li key={i} className="leading-relaxed">{m}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Practical Guide */}
      {activeTab === "practical" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
          
          {/* Phrases, Vocab & Packing */}
          <div className="flex flex-col gap-6">
            
            {/* Phrasebook */}
            <div className="bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-850/60">
                <Languages className="w-4 h-4 text-violet-650 dark:text-violet-400" /> Useful Vocabulary
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-[220px] overflow-y-auto pr-1">
                {phrases.map((phrase, idx) => (
                  <div key={idx} className="bg-white/80 dark:bg-slate-955/50 border border-slate-200 dark:border-slate-850 p-2.5 rounded-lg flex items-center justify-between gap-3 group shadow-sm">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-slate-500 dark:text-slate-405">{phrase.phrase}</span>
                      <span className="text-xs font-bold text-emerald-650 dark:text-emerald-450">{phrase.translation}</span>
                    </div>
                    <span className="text-[9px] text-slate-500 italic bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-1.5 py-0.5 rounded flex items-center gap-1">
                      <Volume2 className="w-3 h-3 text-emerald-600 dark:text-emerald-450" />
                      "{phrase.pronunciation}"
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Packing Checklist */}
            <div className="bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-850/60">
                <CheckSquare className="w-4 h-4 text-emerald-600 dark:text-emerald-450" /> Customized Packing Checklist
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[11px]">
                <div className="bg-white/60 dark:bg-slate-955/40 border border-slate-200 dark:border-slate-850 p-2.5 rounded-lg shadow-sm">
                  <span className="font-bold text-emerald-650 dark:text-emerald-450 block mb-1">💼 Essentials</span>
                  {packing.essentials.map((item, i) => <div key={i} className="text-slate-600 dark:text-slate-400 py-0.5">✓ {item}</div>)}
                </div>
                <div className="bg-white/60 dark:bg-slate-955/40 border border-slate-200 dark:border-slate-850 p-2.5 rounded-lg shadow-sm">
                  <span className="font-bold text-emerald-650 dark:text-emerald-450 block mb-1">🌤️ Seasonal</span>
                  {packing.seasonal_items.map((item, i) => <div key={i} className="text-slate-600 dark:text-slate-400 py-0.5">✓ {item}</div>)}
                </div>
                <div className="bg-white/60 dark:bg-slate-955/40 border border-slate-200 dark:border-slate-850 p-2.5 rounded-lg shadow-sm">
                  <span className="font-bold text-emerald-650 dark:text-emerald-455 block mb-1">🕌 Cultural</span>
                  {packing.cultural_items.map((item, i) => <div key={i} className="text-slate-600 dark:text-slate-400 py-0.5">✓ {item}</div>)}
                </div>
              </div>
            </div>

          </div>

          {/* Sustainability & Safety */}
          <div className="flex flex-col gap-6">
            
            {/* Sustainability Tips */}
            <div className="bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-850/60">
                <Leaf className="w-4 h-4 text-emerald-655 dark:text-emerald-450" /> Sustainable Tourism Tips
              </h3>
              <div className="flex flex-col gap-3 text-[11px] text-slate-650 dark:text-slate-350">
                <div>
                  <span className="font-bold text-emerald-700 dark:text-emerald-400 block mb-0.5">🚌 Public Transit:</span>
                  <p>{sustainability.public_transport}</p>
                </div>
                <div>
                  <span className="font-bold text-emerald-700 dark:text-emerald-400 block mb-0.5">🚶 Walk & Cycle:</span>
                  <p>{sustainability.walking_routes}</p>
                </div>
                <div>
                  <span className="font-bold text-emerald-700 dark:text-emerald-400 block mb-0.5">🛍️ Support Local Businesses:</span>
                  <p>{sustainability.local_businesses}</p>
                </div>
                <div>
                  <span className="font-bold text-emerald-700 dark:text-emerald-400 block mb-0.5">🥤 Reduce Plastics & Waste:</span>
                  <p>{sustainability.plastic_reduction}</p>
                </div>
              </div>
            </div>

            {/* Safety & Emergency */}
            <div className="bg-slate-100/30 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 p-4 rounded-2xl flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-850/60">
                <ShieldAlert className="w-4 h-4 text-rose-500" /> Safety Manual & Contacts
              </h3>
              <div className="flex flex-col gap-2 text-[11px]">
                <div className="flex justify-between items-center bg-rose-50 dark:bg-rose-950/15 border border-rose-100 dark:border-rose-900/30 p-2.5 rounded-lg shadow-sm">
                  <span className="font-bold text-rose-700 dark:text-rose-455">🚨 Local Emergency Contact:</span>
                  <span className="font-bold text-rose-600 dark:text-rose-400 px-2 py-0.5 bg-rose-100 dark:bg-rose-500/10 rounded">{safety.emergency_number}</span>
                </div>
                <div className="mt-1">
                  <span className="font-bold text-slate-600 dark:text-slate-400">🚫 Common Tourist Scams:</span>
                  <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 mt-1 pl-1 flex flex-col gap-1">
                    {safety.common_scams.map((scam, i) => <li key={i}>{scam}</li>)}
                  </ul>
                </div>
              </div>
            </div>

          </div>

        </div>
      )}
    </div>
  );
};
export default DiscoveryBoard;
