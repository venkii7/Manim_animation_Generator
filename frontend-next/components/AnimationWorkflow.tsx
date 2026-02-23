"use client";

import { useEffect } from "react";
import { useAnimationStore } from "@/store/animation";
import { apiService } from "@/lib/api";
import { InputStage } from "./stages/InputStage";
import { PlanningStage } from "./stages/PlanningStage";
import { PlanReviewStage } from "./stages/PlanReviewStage";
import { CodeGenerationStage } from "./stages/CodeGenerationStage";
import { CodeReviewStage } from "./stages/CodeReviewStage";
import { RenderingStage } from "./stages/RenderingStage";
import { CompletedStage } from "./stages/CompletedStage";
import { ErrorDisplay } from "./ErrorDisplay";
import { ProgressIndicator } from "./ProgressIndicator";

export function AnimationWorkflow() {
  const { sessionId, status, plan, code, error, setStatus, setPlan, setCode } =
    useAnimationStore();

  // Poll status when session is active
  useEffect(() => {
    if (!sessionId) return;

    const pollStatus = async () => {
      try {
        const newStatus = await apiService.getStatus(sessionId);
        setStatus(newStatus);

        // Load plan when ready
        if (newStatus.stage === "plan_ready" && !plan) {
          const planData = await apiService.getPlan(sessionId);
          setPlan(planData);
        }

        // Load code when ready
        if (
          (newStatus.stage === "code_ready" || newStatus.stage === "rendering") &&
          !code
        ) {
          const codeData = await apiService.getCode(sessionId);
          setCode(codeData);
        }
      } catch (err) {
        console.error("Failed to fetch status:", err);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [sessionId, plan, code, setStatus, setPlan, setCode]);

  const getStageInfo = () => {
    if (!status && !sessionId) return { emoji: "✏️", title: "Input", description: "Describe your animation", show: true };
    if (!status) return { emoji: "⏳", title: "Starting", description: "Initializing your animation", show: true };
    
    const stageMap: Record<string, { emoji: string; title: string; description: string; show: boolean }> = {
      input: { emoji: "✏️", title: "Input", description: "Describe your animation", show: true },
      planning: { emoji: "🧠", title: "Planning", description: "AI is creating your animation plan", show: true },
      plan_ready: { emoji: "📋", title: "Plan Review", description: "Review and approve the animation plan", show: true },
      code_generating: { emoji: "⚙️", title: "Code Generation", description: "AI is writing Manim code", show: true },
      code_ready: { emoji: "💻", title: "Code Review", description: "Review and edit the generated code", show: true },
      rendering: { emoji: "🎬", title: "Rendering", description: "Creating your animation video", show: true },
      completed: { emoji: "🎉", title: "Completed", description: "Your animation is ready!", show: true },
      failed: { emoji: "❌", title: "Failed", description: "Something went wrong", show: true },
    };
    
    return stageMap[status.stage] || stageMap.input;
  };

  const currentStage = getStageInfo();

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-5xl md:text-6xl font-bold text-white drop-shadow-2xl">
          🎬 Manim Animation Generator
        </h1>
        <p className="text-xl text-white/90 drop-shadow-lg">
          Transform your ideas into stunning mathematical animations
        </p>
      </div>

      {/* Current Stage Badge - Always show when we have a session or status */}
      {(sessionId || status) && currentStage.show && (
        <div className="glass-strong rounded-2xl p-6 shadow-2xl border-2 border-primary-300 animate-slide-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-5xl animate-bounce">{currentStage.emoji}</div>
              <div>
                <div className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-1">
                  Current Stage
                </div>
                <h2 className="text-3xl font-bold text-gray-800">
                  {currentStage.title}
                </h2>
                <p className="text-gray-600 mt-1">{currentStage.description}</p>
              </div>
            </div>
            {status && (
              <div className="text-right">
                <div className="text-4xl font-bold text-gradient">
                  {status.progress}%
                </div>
                <div className="text-sm text-gray-500 mt-1">Progress</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && <ErrorDisplay />}

      {/* Progress Indicator */}
      {status && <ProgressIndicator />}

      {/* Stage-based Rendering */}
      <div className="animate-fade-in">
        {!sessionId && <InputStage />}
        
        {status?.stage === "planning" && <PlanningStage />}
        
        {status?.stage === "plan_ready" && plan && <PlanReviewStage />}
        
        {status?.stage === "code_generating" && <CodeGenerationStage />}
        
        {status?.stage === "code_ready" && code && <CodeReviewStage />}
        
        {status?.stage === "rendering" && code && <RenderingStage />}
        
        {status?.stage === "completed" && <CompletedStage />}
        
        {status?.stage === "failed" && (
          <div className="glass-strong rounded-2xl p-8 text-center">
            <div className="text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold text-red-600 mb-2">
              Animation Failed
            </h2>
            <p className="text-gray-600 mb-6">{status.error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-semibold hover:shadow-xl transition-all"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
