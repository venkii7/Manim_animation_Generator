"use client";

import { useAnimationStore } from "@/store/animation";
import { XCircle } from "lucide-react";

export function ErrorDisplay() {
  const { error, setError } = useAnimationStore();

  if (!error) return null;

  return (
    <div className="glass-strong rounded-2xl p-6 border-l-4 border-red-500 flex items-start gap-4 animate-slide-up">
      <XCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
      <div className="flex-1">
        <h3 className="font-semibold text-red-800 mb-1">Error</h3>
        <p className="text-red-600">{error}</p>
      </div>
      <button
        onClick={() => setError(null)}
        className="text-red-500 hover:text-red-700 transition-colors"
      >
        <XCircle className="w-5 h-5" />
      </button>
    </div>
  );
}
