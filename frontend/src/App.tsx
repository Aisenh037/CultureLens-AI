import React, { useState } from "react";
import { ThemeToggle } from "./components/ThemeToggle";
import { TravelForm } from "./components/TravelForm";
import { ItineraryTimeline } from "./components/ItineraryTimeline";
import { DiscoveryBoard } from "./components/DiscoveryBoard";
import { InteractiveGuide } from "./components/InteractiveGuide";
import { InteractiveMap } from "./components/InteractiveMap";
import { ErrorMessage } from "./components/ErrorMessage";
import { LoadingIndicator } from "./components/LoadingIndicator";
import { Compass, RefreshCw, ChevronLeft, MapPin, Download, Sun, DollarSign, Calendar, Users } from "lucide-react";
import { TravelRequest, CultureLensResponse, ChatMessage } from "./types/travel";
import { generateTravelPlan, sendChatMessage } from "./services/api";
import { validateTravelRequest, ValidationErrors } from "./utils/validation";

const initialRequest: TravelRequest = {
  destination: "",
  budget: "Mid-range",
  duration_days: 3,
  travel_style: "Solo",
  companions: "None",
  interests: ["Culture"],
  languages: ["English"],
  accessibility_needs: [],
  food_preference: "No Restrictions",
};

export const App: React.FC = () => {
  const [formData, setFormData] = useState<TravelRequest>(initialRequest);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [result, setResult] = useState<CultureLensResponse | null>(null);

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  const handleFieldChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    
    if (field === "destination" && errors.destination) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.destination;
        return next;
      });
    }
    if (field === "interests" && errors.interests) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.interests;
        return next;
      });
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationErrors = validateTravelRequest(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setApiError(null);
    setResult(null);
    setChatHistory([]);
    
    try {
      const data = await generateTravelPlan(formData);
      setResult(data);
    } catch (err: any) {
      setApiError(err.message || "An unexpected error occurred during generation.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || chatLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText,
    };

    const nextHistory = [...chatHistory, userMessage];
    setChatHistory(nextHistory);
    setChatLoading(true);

    try {
      const reply = await sendChatMessage(messageText, chatHistory, result);
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: reply },
      ]);
    } catch (err: any) {
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ Failed to get reply: ${err.message}` },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const triggerPDFDownload = () => {
    window.print();
  };

  const resetPlanner = () => {
    setResult(null);
    setApiError(null);
    setChatHistory([]);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-800 dark:selection:text-emerald-250 transition-colors duration-200">
      
      {/* Navigation Header */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-900 transition-colors print:hidden">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-emerald-400 text-slate-950 dark:text-slate-950 font-bold shadow-md shadow-emerald-500/5">
              <Compass className="w-5 h-5 animate-spin-slow" />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tight text-slate-900 dark:text-white">
                CultureLens AI
              </h1>
              <p className="text-[10px] text-slate-500 dark:text-slate-500 font-bold uppercase tracking-widest">
                Discover destinations like a local, not a tourist.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {result && (
              <button
                onClick={resetPlanner}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-650 dark:text-slate-400 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-bold hover:border-slate-300 dark:hover:border-slate-700 transition-all active:scale-95"
              >
                <ChevronLeft className="w-4 h-4" />
                Configure New Trip
              </button>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 w-full flex flex-col gap-8 flex-1 py-8">
        
        {/* Form Selector */}
        {!result && !loading && (
          <div className="max-w-4xl mx-auto w-full flex flex-col gap-6">
            <div className="text-center flex flex-col gap-2 max-w-xl mx-auto mb-4">
              <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white bg-gradient-to-r from-emerald-600 via-slate-800 to-teal-700 dark:from-emerald-200 dark:via-slate-100 dark:to-teal-200 bg-clip-text text-transparent">
                Discover Deeper Culture
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                CultureLens queries Wikipedia records, weather indexes, and local maps in real time to assemble an AI-enriched cultural exploration plan matching your specific preferences.
              </p>
            </div>

            <section aria-labelledby="form-heading">
              <h3 id="form-heading" className="sr-only">Travel Configuration Form</h3>
              <TravelForm
                formData={formData}
                errors={errors}
                loading={loading}
                onChange={handleFieldChange}
                onSubmit={handleFormSubmit}
              />
            </section>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex-1 flex items-center justify-center py-12">
            <LoadingIndicator />
          </div>
        )}

        {/* API Error Callout */}
        {apiError && (
          <div className="max-w-3xl mx-auto w-full">
            <ErrorMessage message={apiError} />
            <button
              onClick={() => setResult(null)}
              className="mt-4 px-4 py-2 bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-350 text-xs font-bold rounded-xl active:scale-95 transition-all flex items-center gap-1.5 mx-auto"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reset and Try Again
            </button>
          </div>
        )}

        {/* Main Dashboard view */}
        {result && !loading && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fade-in items-start">
            
            {/* Left and Center: Maps, timeline, specs */}
            <div className="lg:col-span-7 flex flex-col gap-8">
              
              {/* Destination Overview Banner */}
              <div className="p-6 rounded-3xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 backdrop-blur-xl relative overflow-hidden flex flex-col gap-3 shadow-sm dark:shadow-2xl">
                <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
                
                <div className="flex items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800/60 pb-3">
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[9px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-400">CultureLens Summary</span>
                    <h2 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-emerald-600 dark:text-emerald-450" />
                      {result.destination.name}, {result.destination.country}
                    </h2>
                  </div>

                  <button
                    onClick={triggerPDFDownload}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-slate-950 text-xs font-black rounded-lg transition-all active:scale-95 print:hidden"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download PDF
                  </button>
                </div>

                <p className="text-xs text-slate-650 dark:text-slate-355 leading-relaxed italic">
                  "{result.summary}"
                </p>

                {/* Sub Metadata parameters */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-600 dark:text-slate-400 font-semibold pt-1">
                  <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-950/40 p-2 rounded-xl border border-slate-200 dark:border-slate-850">
                    <Sun className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                    <span>{result.weather.current_temp} ({result.weather.conditions})</span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-950/40 p-2 rounded-xl border border-slate-200 dark:border-slate-850">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-450" />
                    <span>Daily: {result.budget.estimated_daily_cost}</span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-950/40 p-2 rounded-xl border border-slate-200 dark:border-slate-850">
                    <Calendar className="w-3.5 h-3.5 text-teal-600 dark:text-teal-400" />
                    <span>Duration: {formData.duration_days} Days</span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-950/40 p-2 rounded-xl border border-slate-200 dark:border-slate-850">
                    <Users className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                    <span>Style: {formData.travel_style}</span>
                  </div>
                </div>
              </div>

              {/* Factual Interactive Map */}
              <section aria-label="Factual OpenStreetMap map">
                <InteractiveMap 
                  lat={result.destination.latitude}
                  lon={result.destination.longitude}
                  destinationName={result.destination.name}
                  attractions={result.top_attractions}
                />
              </section>

              {/* Day-by-Day Personal Itinerary */}
              <section aria-label="Itinerary Timeline Planner">
                <ItineraryTimeline 
                  itinerary={result.itinerary} 
                  stories={result.stories} 
                />
              </section>

              {/* Discovery Card Board */}
              <section aria-label="Culture Discovery Board Cards">
                <DiscoveryBoard
                  attractions={result.top_attractions}
                  hiddenGems={result.hidden_gems}
                  heritage={result.heritage}
                  food={result.food}
                  etiquette={result.etiquette}
                  phrases={result.local_phrases}
                  sustainability={result.sustainability}
                  safety={result.safety}
                  packing={result.packing}
                  events={result.events}
                />
              </section>

            </div>

            {/* Right Panel: Sticky Chatbot Companion */}
            <div className="lg:col-span-5 lg:sticky lg:top-24 print:hidden">
              <section aria-label="Interactive AI Tour Companion guide chat">
                <InteractiveGuide
                  chatHistory={chatHistory}
                  itineraryContext={result}
                  onSendMessage={handleSendMessage}
                  chatLoading={chatLoading}
                />
              </section>
            </div>

          </div>
        )}
      </main>

      {/* Print-only Itinerary Summary details */}
      <div className="hidden print:block text-slate-950 p-8 font-serif text-sm">
        <h1 className="text-2xl font-bold border-b pb-2 mb-4">CultureLens AI - Travel Companion Report</h1>
        {result && (
          <div className="flex flex-col gap-6">
            <div>
              <h2 className="text-lg font-bold">Destination: {result.destination.name}, {result.destination.country}</h2>
              <p className="italic mt-1">"{result.summary}"</p>
            </div>
            
            <div>
              <h3 className="text-md font-bold border-b pb-1 mt-4">Personal Itinerary Route</h3>
              {result.itinerary.map((day) => (
                <div key={day.day_number} className="mt-3">
                  <h4 className="font-bold">Day {day.day_number}: {day.theme}</h4>
                  <ul className="list-disc list-inside pl-4 mt-1">
                    {day.activities.map((act, i) => (
                      <li key={i} className="py-1">
                        <strong>{act.time_slot} - {act.activity_name}:</strong> {act.description} (Duration: {act.duration}, Cost: {act.cost})
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div>
              <h3 className="text-md font-bold border-b pb-1 mt-4">Essential Cultural Etiquette</h3>
              <p className="mt-1"><strong>Greetings:</strong> {result.etiquette.greetings}</p>
              <p><strong>Dress Code:</strong> {result.etiquette.dress_code}</p>
              <p><strong>Tipping:</strong> {result.etiquette.tipping}</p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-200 dark:border-slate-900 text-center text-[10px] uppercase font-bold tracking-widest text-slate-500 dark:text-slate-650 bg-slate-100 dark:bg-slate-950 mt-12 print:hidden">
        CultureLens AI • Google for Developers Hackathon Project
      </footer>
    </div>
  );
};
export default App;
