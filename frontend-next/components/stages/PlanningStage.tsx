"use client";

import { Brain, Loader2 } from "lucide-react";

export function PlanningStage() {
  return (
    <div className="glass-strong rounded-3xl p-12 text-center space-y-6 animate-slide-up shadow-2xl">
      <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full animate-pulse-slow">
        <Brain className="w-12 h-12 text-white" />
      </div>
      
      <div className="space-y-3">
        <h2 className="text-3xl font-bold text-gray-800">
          AI is Planning Your Animation
        </h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Our AI is analyzing your description and creating a detailed animation plan with objects, timeline, and visual flow...
        </p>
      </div>

      <div className="flex items-center justify-center gap-2 text-primary-600">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="font-medium">Generating plan...</span>
      </div>
    </div>
  );
}
