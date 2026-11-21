import { FormEvent, useEffect, useRef, useState } from "react";
import { joinWaitlist, track } from "./tracking";
import type { WedgeConfig } from "./wedges";

type Status = "idle" | "sending" | "done" | "error";

export default function WedgeLanding({ wedge }: { wedge: WedgeConfig }) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [note, setNote] = useState("");
  const [wantsInterview, setWantsInterview] = useState(false);
  const [consent, setConsent] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");
  const [paywallNotice, setPaywallNotice] = useState(false);
  const formRef = useRef<HTMLElement>(null);
  const viewed = useRef(false);

  useEffect(() => {
    // StrictMode runs effects twice in development; count one view per page load.
    if (viewed.current) return;
    viewed.current = true;
    track(wedge.id, "view");
  }, [wedge.id]);

  const onPay = () => {
    track(wedge.id, "pay_click");
    setPaywallNotice(true);
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!consent) {
      setError("Please tick the box so we're allowed to email you.");
      setStatus("error");
      return;
    }
    setStatus("sending");
    setError("");
    try {
      await joinWaitlist(wedge.id, { email, name, role, note, wants_interview: wantsInterview, consent });
      setStatus("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  };

  const input =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50";

  return (
    <div className="min-h-full">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <a href="/" className="text-lg font-bold tracking-tight">
          CultureLens<span className="text-indigo-600"> AI</span>
        </a>
        <a href="/" className="text-sm text-slate-500 hover:text-slate-900 dark:hover:text-slate-200">
          Try the free planner →
        </a>
      </header>

      <main className="mx-auto max-w-5xl px-6 pb-20">
        <section className="py-12 md:py-20">
          <p className="text-sm font-semibold uppercase tracking-wider text-indigo-600">{wedge.eyebrow}</p>
          <h1 className="mt-3 max-w-3xl text-4xl font-bold leading-tight tracking-tight md:text-5xl">{wedge.headline}</h1>
          <p className="mt-5 max-w-2xl text-lg text-slate-600 dark:text-slate-300">{wedge.sub}</p>
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              type="button"
              onClick={onPay}
              className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              {wedge.price.button}
            </button>
            <span className="text-sm text-slate-500">
              {wedge.price.amount} {wedge.price.unit}
            </span>
          </div>
        </section>

        <section className="grid gap-8 border-t border-slate-200 py-12 dark:border-slate-800 md:grid-cols-2">
          <div>
            <h2 className="text-xl font-semibold">Sound familiar?</h2>
            <ul className="mt-4 space-y-3 text-slate-600 dark:text-slate-300">
              {wedge.pains.map((p) => (
                <li key={p} className="flex gap-3">
                  <span aria-hidden className="text-indigo-600">—</span>
                  {p}
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-5">
            {wedge.features.map((f) => (
              <div key={f.title}>
                <h3 className="font-semibold">{f.title}</h3>
                <p className="text-slate-600 dark:text-slate-300">{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section ref={formRef} id="waitlist" className="scroll-mt-6 border-t border-slate-200 py-12 dark:border-slate-800">
          {paywallNotice && status !== "done" && (
            <div role="status" className="mb-6 rounded-lg border border-amber-300 bg-amber-50 p-4 text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200">
              <strong>We're not taking payments yet.</strong> This is still being built, and you haven't been charged.
              Join the waitlist below and you'll be first to know when it opens.
            </div>
          )}

          {status === "done" ? (
            <div role="status" className="rounded-lg border border-emerald-300 bg-emerald-50 p-6 text-emerald-900 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
              <h2 className="text-xl font-semibold">You're on the list.</h2>
              <p className="mt-2">
                We'll email you when it's ready{wantsInterview ? ", and reach out to set up a short chat" : ""}. Thank you!
              </p>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="max-w-xl space-y-4" noValidate>
              <h2 className="text-2xl font-semibold">Join the waitlist</h2>
              <p className="text-slate-600 dark:text-slate-300">Early members get the launch price locked in.</p>

              <label className="block">
                <span className="text-sm font-medium">Email *</span>
                <input type="email" required maxLength={254} autoComplete="email" value={email}
                  onChange={(e) => setEmail(e.target.value)} className={`${input} mt-1`} />
              </label>
              <label className="block">
                <span className="text-sm font-medium">Name</span>
                <input type="text" maxLength={100} autoComplete="name" value={name}
                  onChange={(e) => setName(e.target.value)} className={`${input} mt-1`} />
              </label>
              <label className="block">
                <span className="text-sm font-medium">{wedge.roleLabel}</span>
                <input type="text" maxLength={100} placeholder={wedge.rolePlaceholder} value={role}
                  onChange={(e) => setRole(e.target.value)} className={`${input} mt-1`} />
              </label>
              <label className="block">
                <span className="text-sm font-medium">Anything else?</span>
                <textarea maxLength={500} rows={3} placeholder={wedge.notePlaceholder} value={note}
                  onChange={(e) => setNote(e.target.value)} className={`${input} mt-1`} />
              </label>

              <label className="flex items-start gap-3 text-sm">
                <input type="checkbox" checked={wantsInterview} onChange={(e) => setWantsInterview(e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600" />
                <span>I'm happy to do a 15-minute call to help shape this.</span>
              </label>
              <label className="flex items-start gap-3 text-sm">
                <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600" />
                <span>
                  Email me about the launch. I can unsubscribe any time by replying. *
                </span>
              </label>

              {status === "error" && <p role="alert" className="text-sm text-red-600">{error}</p>}

              <button type="submit" disabled={status === "sending"}
                className="rounded-lg bg-slate-900 px-6 py-3 font-semibold text-white hover:bg-slate-800 disabled:opacity-60 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200">
                {status === "sending" ? "Joining…" : "Join the waitlist"}
              </button>

              <p className="text-xs text-slate-500">
                We store only what you type here, plus an anonymous visit counter. No tracking cookies, no selling your
                details, and we'll delete your entry if you ask.
              </p>
            </form>
          )}
        </section>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 dark:border-slate-800">
        CultureLens AI · <a className="underline" href="/">Free trip planner</a>
      </footer>
    </div>
  );
}
