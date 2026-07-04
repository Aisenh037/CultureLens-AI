import React from "react";
import { Compass } from "lucide-react";

export const LoadingIndicator: React.FC = () => {
  return (
    <div
      className="flex flex-col gap-6 w-full max-w-6xl mx-auto p-6 rounded-3xl bg-slate-900/60 border border-slate-800/80 shadow-2xl text-slate-100 transition-all animate-pulse"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="flex items-center gap-4 border-b border-slate-800/60 pb-4">
        <div className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400 animate-spin-slow">
          <Compass className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">
            AI Travel Guide is mapping your journey...
          </h3>
          <p className="text-xs text-slate-400">
            Consulting heritage records, discovery databases, seasonal events, and local menus to craft your custom experience.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left column skeleton */}
        <div className="flex flex-col gap-4">
          <div className="h-6 bg-slate-850 rounded-lg w-1/3" />
          <div className="flex gap-2">
            <div className="h-10 bg-slate-850 rounded-xl w-16" />
            <div className="h-10 bg-slate-850 rounded-xl w-16" />
            <div className="h-10 bg-slate-850 rounded-xl w-16" />
          </div>
          <div className="p-5 rounded-2xl bg-slate-950/20 border border-slate-850 flex flex-col gap-3">
            <div className="h-5 bg-slate-850 rounded-lg w-1/2" />
            <div className="h-3 bg-slate-850 rounded-lg w-full" />
            <div className="h-3 bg-slate-850 rounded-lg w-5/6" />
          </div>
          <div className="p-5 rounded-2xl bg-slate-950/20 border border-slate-850 flex flex-col gap-3">
            <div className="h-5 bg-slate-850 rounded-lg w-1/2" />
            <div className="h-3 bg-slate-850 rounded-lg w-full" />
            <div className="h-3 bg-slate-850 rounded-lg w-5/6" />
          </div>
        </div>

        {/* Right column skeleton */}
        <div className="flex flex-col gap-4">
          <div className="h-10 bg-slate-850 rounded-2xl w-full" />
          <div className="p-5 rounded-2xl bg-slate-950/20 border border-slate-850 flex flex-col gap-4">
            <div className="h-5 bg-slate-850 rounded-lg w-1/3" />
            <div className="h-3 bg-slate-850 rounded-lg w-full" />
            <div className="h-3 bg-slate-850 rounded-lg w-full" />
            <div className="h-3 bg-slate-850 rounded-lg w-3/4" />
          </div>
        </div>
      </div>
    </div>
  );
};
export default LoadingIndicator;
