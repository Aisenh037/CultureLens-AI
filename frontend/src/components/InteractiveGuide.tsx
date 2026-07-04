import React, { useState, useRef, useEffect } from "react";
import { ChatMessage, CultureLensResponse } from "../types/travel";
import { MessageSquare, Send, Bot, User, Sparkles } from "lucide-react";

interface InteractiveGuideProps {
  chatHistory: ChatMessage[];
  itineraryContext: CultureLensResponse | null;
  onSendMessage: (message: string) => Promise<void>;
  chatLoading: boolean;
}

export const InteractiveGuide: React.FC<InteractiveGuideProps> = ({
  chatHistory,
  itineraryContext,
  onSendMessage,
  chatLoading,
}) => {
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const quickActions = [
    { label: "🌧️ Rainy backup plan", prompt: "It's raining today. What indoor activities do you recommend as a backup?" },
    { label: "🍜 Traditional food spot", prompt: "Recommend a specific hidden spot or street food stall nearby to eat traditional food." },
    { label: "📜 Tell a local myth", prompt: "Tell me a fascinating local legend or myth related to our destination." },
    { label: "🚌 Travel/Transit tips", prompt: "What is the best way to get around the city? Tell me about public transit and tickets." },
  ];

  // Auto-scroll to bottom of conversation
  useEffect(() => {
    if (messagesEndRef.current?.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory, chatLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || chatLoading) return;
    onSendMessage(inputValue.trim());
    setInputValue("");
  };

  const handleQuickAction = (prompt: string) => {
    if (chatLoading) return;
    onSendMessage(prompt);
  };

  return (
    <div className="backdrop-blur-xl bg-white/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 rounded-3xl p-5 shadow-md dark:shadow-xl flex flex-col h-[650px] text-slate-850 dark:text-slate-100 relative">
      
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800/60 pb-3 mb-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-500 text-slate-950 font-bold">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
            Interactive AI Guide
            <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 animate-pulse" />
          </h3>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">
            {itineraryContext 
              ? `Live local assistant for ${itineraryContext.destination.name}`
              : "Chat with your AI Tour Companion"}
          </p>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-3.5 mb-4 scrollbar-thin">
        {chatHistory.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 gap-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-400 dark:text-slate-500">
              <MessageSquare className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-700 dark:text-slate-350">Your Local Companion is Ready</p>
              <p className="text-xs text-slate-500 dark:text-slate-500 mt-1 max-w-[240px] leading-relaxed">
                Ask questions about heritage spots, get translations, or update your schedule!
              </p>
            </div>
          </div>
        ) : (
          chatHistory.map((msg, idx) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={idx}
                className={`flex gap-3 items-start max-w-[85%] ${
                  isUser ? "self-end flex-row-reverse" : "self-start"
                }`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-lg border flex items-center justify-center flex-shrink-0 ${
                  isUser 
                    ? "bg-emerald-600 border-emerald-500 text-slate-950" 
                    : "bg-slate-100 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-450"
                }`}>
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className={`rounded-2xl p-3.5 text-xs leading-relaxed border transition-all ${
                  isUser
                    ? "bg-emerald-500/10 border-emerald-350 dark:border-emerald-500/35 text-emerald-950 dark:text-emerald-100 rounded-tr-none shadow-sm"
                    : "bg-slate-100/80 dark:bg-slate-950/60 border-slate-200 dark:border-slate-855 text-slate-700 dark:text-slate-300 rounded-tl-none shadow-sm"
                }`}>
                  <div className="space-y-1.5 whitespace-pre-wrap">
                    {msg.content}
                  </div>
                </div>
              </div>
            );
          })
        )}

        {/* Chat loading state */}
        {chatLoading && (
          <div className="flex gap-3 items-start self-start max-w-[80%]">
            <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-slate-100/80 dark:bg-slate-955/60 border border-slate-200 dark:border-slate-850 rounded-2xl rounded-tl-none p-4 flex items-center gap-1.5 shadow-sm">
              <span className="w-1.5 h-1.5 bg-emerald-600 dark:bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-1.5 h-1.5 bg-emerald-600 dark:bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-1.5 h-1.5 bg-emerald-600 dark:bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Floating Quick Action Suggestion Pills */}
      {itineraryContext && (
        <div className="flex gap-1.5 overflow-x-auto pb-3 scrollbar-none flex-shrink-0">
          {quickActions.map((qa, idx) => (
            <button
              key={idx}
              type="button"
              disabled={chatLoading}
              onClick={() => handleQuickAction(qa.prompt)}
              className="py-2 px-3 text-[10px] font-bold bg-slate-100/60 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 hover:border-slate-350 dark:hover:border-slate-700 hover:text-slate-800 dark:hover:text-slate-200 text-slate-600 dark:text-slate-455 rounded-xl whitespace-nowrap active:scale-95 transition-all disabled:opacity-50"
            >
              {qa.label}
            </button>
          ))}
        </div>
      )}

      {/* Message input form */}
      <form onSubmit={handleSubmit} className="flex gap-2 items-center flex-shrink-0">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={chatLoading ? "Assistant is typing..." : "Ask your local guide anything..."}
          disabled={chatLoading}
          className="flex-1 py-3.5 px-4 bg-slate-100 dark:bg-slate-955/60 border border-slate-200 dark:border-slate-850 rounded-xl outline-none focus:ring-1 focus:ring-emerald-500/40 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-550 transition-all disabled:opacity-55"
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || chatLoading}
          className="p-3.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded-xl active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg shadow-emerald-600/10"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
export default InteractiveGuide;
