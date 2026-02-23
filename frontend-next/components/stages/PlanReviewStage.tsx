"use client";

import { useState } from "react";
import { useAnimationStore } from "@/store/animation";
import { apiService } from "@/lib/api";
import { CheckCircle, RefreshCw, Clock, Layers } from "lucide-react";

export function PlanReviewStage() {
  const { sessionId, plan, setPlan, setLoading, setError, isLoading } =
    useAnimationStore();
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState("");

  if (!plan || !sessionId) return null;

  const handleApprove = async () => {
    try {
      setLoading(true);
      setError(null);
      await apiService.generateCode(sessionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate code");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!feedback.trim()) return;

    try {
      setLoading(true);
      setError(null);
      setPlan(null);
      await apiService.regeneratePlan(sessionId, feedback.trim());
      setFeedback("");
      setShowFeedback(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to regenerate plan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Header */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800">
                Animation Plan Ready
              </h2>
            </div>
            <h3 className="text-xl font-semibold text-primary-600">
              {plan.scene_title}
            </h3>
            <p className="text-gray-600">{plan.description}</p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{plan.duration}s duration</span>
              </div>
              <div className="flex items-center gap-1">
                <Layers className="w-4 h-4" />
                <span>{plan.objects.length} objects</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Description */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          📝 Visual Flow
        </h3>
        <p className="text-gray-700 leading-relaxed">{plan.visual_description}</p>
      </div>

      {/* Objects */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          🎨 Objects ({plan.objects.length})
        </h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {plan.objects.map((obj) => (
            <div
              key={obj.id}
              className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-primary-600">{obj.type}</span>
                <span className="text-xs text-gray-500">{obj.id}</span>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <div>Position: [{obj.initial_state.position.join(", ")}]</div>
                <div>Color: {obj.initial_state.color}</div>
                <div>
                  Scale: {obj.initial_state.scale} | Opacity:{" "}
                  {obj.initial_state.opacity}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          🎬 Animation Timeline ({plan.timeline.length} events)
        </h3>
        <div className="space-y-3">
          {plan.timeline.map((event, index) => (
            <div
              key={index}
              className="flex gap-4 p-4 bg-gradient-to-r from-primary-50 to-purple-50 rounded-xl border-l-4 border-primary-500"
            >
              <div className="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
                {index + 1}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-800">
                    {event.animation}
                  </span>
                  <span className="text-sm text-gray-500">
                    {event.start_time}s - {event.start_time + event.duration}s
                  </span>
                </div>
                <p className="text-gray-700 text-sm">{event.description}</p>
                <p className="text-xs text-gray-500">Target: {event.target}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        {!showFeedback ? (
          <div className="flex gap-4">
            <button
              onClick={handleApprove}
              disabled={isLoading}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              Approve & Generate Code
            </button>
            <button
              onClick={() => setShowFeedback(true)}
              disabled={isLoading}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Request Changes
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="What would you like to change about this plan?"
              rows={4}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-100 outline-none transition-all resize-none"
            />
            <div className="flex gap-4">
              <button
                onClick={handleRegenerate}
                disabled={!feedback.trim() || isLoading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-semibold hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Regenerate Plan
              </button>
              <button
                onClick={() => setShowFeedback(false)}
                disabled={isLoading}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
