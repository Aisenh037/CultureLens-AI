import React from "react";
import { AlertCircle } from "lucide-react";

interface ErrorMessageProps {
  message: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 p-4 rounded-xl border border-red-200 bg-red-50 text-red-800 dark:border-red-900/50 dark:bg-red-950/20 dark:text-red-400 shadow-xs transition-all"
    >
      <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" aria-hidden="true" />
      <div className="flex-1">
        <h3 className="text-sm font-semibold">Error Occurred</h3>
        <p className="text-xs mt-1 text-red-700 dark:text-red-400/80 leading-relaxed">
          {message}
        </p>
      </div>
    </div>
  );
};
export default ErrorMessage;
