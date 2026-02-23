"use client";

import { useAnimationStore } from "@/store/animation";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const stages = [
  { key: "input", label: "Input", emoji: "✏️" },
  { key: "planning", label: "Planning", emoji: "🧠" },
  { key: "plan_ready", label: "Plan Review", emoji: "📋" },
  { key: "code_generating", label: "Code Generation", emoji: "⚙️" },
  { key: "code_ready", label: "Code Review", emoji: "💻" },
  { key: "rendering", label: "Rendering", emoji: "🎬" },
  { key: "completed", label: "Complete", emoji: "🎉" },
];

export function ProgressIndicator() {
  const { status } = useAnimationStore();

  if (!status) return null;

  const currentStageIndex = stages.findIndex((s) => s.key === status.stage);

  return (
    <div className="glass-strong rounded-2xl p-6 space-y-4">
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm font-medium">
          <span className="text-gray-700">{status.message}</span>
          <span className="text-primary-600">{status.progress}%</span>
        </div>
        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 transition-all duration-500 ease-out"
            style={{ width: `${status.progress}%` }}
          />
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="flex items-center justify-between">
        {stages.map((stage, index) => {
          const isCompleted = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;
          const isPending = index > currentStageIndex;

          return (
            <div key={stage.key} className="flex flex-col items-center flex-1">
              <div
                className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-xl mb-2 transition-all duration-300
                  ${
                    isCompleted
                      ? "bg-green-500 text-white scale-100"
                      : isCurrent
                      ? "bg-primary-500 text-white scale-110 animate-pulse-slow"
                      : "bg-gray-300 text-gray-500 scale-90"
                  }
                `}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-6 h-6" />
                ) : isCurrent ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  <Circle className="w-6 h-6" />
                )}
              </div>
              <span
                className={`text-xs font-medium text-center hidden md:block ${
                  isCurrent ? "text-primary-700" : "text-gray-600"
                }`}
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
