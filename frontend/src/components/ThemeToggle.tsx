import React, { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import { initializeTheme, toggleTheme } from "../utils/theme";

export const ThemeToggle: React.FC = () => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(initializeTheme());
  }, []);

  const handleToggle = () => {
    setIsDark(toggleTheme());
  };

  return (
    <button
      onClick={handleToggle}
      className="p-2.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-amber-400 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors shadow-xs focus:outline-hidden focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
      aria-label={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
      title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
    >
      {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>
  );
};
export default ThemeToggle;
