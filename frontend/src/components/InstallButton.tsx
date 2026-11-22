import { useEffect, useState } from "react";
import { Smartphone } from "lucide-react";
import type { BeforeInstallPromptEvent } from "../pwa";

/**
 * "Install app" button. Appears only when the browser says the app can be
 * installed (Chrome, Edge, Android), and disappears once it is installed.
 * Safari has no install prompt, so iPhone users add it via Share → Add to Home Screen.
 */
export function InstallButton() {
  const [prompt, setPrompt] = useState<BeforeInstallPromptEvent | null>(null);

  useEffect(() => {
    const onPrompt = (e: Event) => {
      e.preventDefault(); // keep the browser's mini-infobar from showing; we show our button instead
      setPrompt(e as BeforeInstallPromptEvent);
    };
    const onInstalled = () => setPrompt(null);
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  if (!prompt) return null;

  const install = async () => {
    await prompt.prompt();
    await prompt.userChoice.catch(() => undefined);
    setPrompt(null); // the event can be used only once
  };

  return (
    <button
      type="button"
      onClick={install}
      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-slate-950 bg-emerald-500 hover:bg-emerald-600 text-xs font-bold transition-all active:scale-95 print:hidden"
    >
      <Smartphone className="w-4 h-4" />
      Install app
    </button>
  );
}
