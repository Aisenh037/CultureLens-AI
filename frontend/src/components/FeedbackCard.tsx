import { FormEvent, useState } from "react";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { sendFeedback } from "../services/feedback";

type Step = "ask" | "details" | "sending" | "done";

/** "Was this useful?" under a generated itinerary. Thumb first, details optional. */
export function FeedbackCard({ destination }: { destination: string }) {
  const [step, setStep] = useState<Step>("ask");
  const [helpful, setHelpful] = useState<boolean | null>(null);
  const [comment, setComment] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [canQuote, setCanQuote] = useState(false);
  const [error, setError] = useState("");

  const choose = (value: boolean) => {
    setHelpful(value);
    setStep("details");
  };

  const submit = async (e?: FormEvent) => {
    e?.preventDefault();
    if (helpful === null) return;
    setStep("sending");
    setError("");
    try {
      await sendFeedback({ helpful, comment, destination, name, email, can_quote: canQuote });
      setStep("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStep("details");
    }
  };

  const box =
    "p-5 rounded-3xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 flex flex-col gap-3 print:hidden";
  const input =
    "w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/40";

  if (step === "done") {
    return (
      <div className={box} role="status">
        <p className="text-sm font-bold text-slate-900 dark:text-white">Thank you! This goes straight to the person building CultureLens.</p>
      </div>
    );
  }

  return (
    <div className={box}>
      <p className="text-sm font-black text-slate-900 dark:text-white">Was this itinerary useful?</p>
      <div className="flex gap-2">
        <button type="button" onClick={() => choose(true)} aria-pressed={helpful === true}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold border transition-all active:scale-95 ${helpful === true ? "bg-emerald-600 text-slate-950 border-emerald-600" : "border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"}`}>
          <ThumbsUp className="w-3.5 h-3.5" /> Yes
        </button>
        <button type="button" onClick={() => choose(false)} aria-pressed={helpful === false}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold border transition-all active:scale-95 ${helpful === false ? "bg-rose-500 text-white border-rose-500" : "border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"}`}>
          <ThumbsDown className="w-3.5 h-3.5" /> Not really
        </button>
      </div>

      {(step === "details" || step === "sending") && helpful !== null && (
        <form onSubmit={submit} className="flex flex-col gap-2.5" noValidate>
          <label className="flex flex-col gap-1 text-xs font-semibold text-slate-600 dark:text-slate-400">
            {helpful ? "What was most useful?" : "What was missing or wrong?"} (optional)
            <textarea rows={3} maxLength={1000} value={comment} onChange={(e) => setComment(e.target.value)} className={input}
              placeholder={helpful ? "e.g. the food tips, the day plan, the costs in rupees" : "e.g. wrong places, too rushed, no veg options"} />
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <label className="flex flex-col gap-1 text-xs font-semibold text-slate-600 dark:text-slate-400">
              First name (optional)
              <input type="text" maxLength={100} value={name} onChange={(e) => setName(e.target.value)} className={input} autoComplete="given-name" />
            </label>
            <label className="flex flex-col gap-1 text-xs font-semibold text-slate-600 dark:text-slate-400">
              Email, if we may reply (optional)
              <input type="email" maxLength={254} value={email} onChange={(e) => setEmail(e.target.value)} className={input} autoComplete="email" />
            </label>
          </div>
          <label className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-400">
            <input type="checkbox" checked={canQuote} onChange={(e) => setCanQuote(e.target.checked)} className="mt-0.5" />
            <span>You can quote my comment with my first name on the CultureLens website.</span>
          </label>
          {error && <p role="alert" className="text-xs text-rose-600">{error}</p>}
          <div className="flex gap-2">
            <button type="submit" disabled={step === "sending"}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-slate-950 text-xs font-black disabled:opacity-60 active:scale-95">
              {step === "sending" ? "Sending…" : "Send feedback"}
            </button>
          </div>
          <p className="text-[10px] text-slate-500">We store only what you type here. Nothing is published unless you tick the box above.</p>
        </form>
      )}
    </div>
  );
}
