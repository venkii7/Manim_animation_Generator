"use client";

import { Code2, Loader2 } from "lucide-react";

export function CodeGenerationStage() {
  return (
    <div className="glass-strong rounded-3xl p-12 text-center space-y-6 animate-slide-up shadow-2xl">
      <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full animate-pulse-slow">
        <Code2 className="w-12 h-12 text-white" />
      </div>
      
      <div className="space-y-3">
        <h2 className="text-3xl font-bold text-gray-800">
          Generating Manim Code
        </h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Converting your animation plan into executable Manim Python code with proper imports, scene structure, and animations...
        </p>
      </div>

      <div className="flex items-center justify-center gap-2 text-blue-600">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="font-medium">Writing code...</span>
      </div>
    </div>
  );
}
