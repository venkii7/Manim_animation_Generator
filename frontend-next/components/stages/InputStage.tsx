"use client";

import { useState } from "react";
import { useAnimationStore } from "@/store/animation";
import { apiService } from "@/lib/api";
import { Sparkles, Send } from "lucide-react";

export function InputStage() {
  const [description, setDescription] = useState("");
  const { setSessionId, setLoading, setError, isLoading } = useAnimationStore();

  const examples = [
    "Visualize the Pythagorean theorem with animated squares",
    "Show matrix transformation rotating and scaling a square",
    "Animate the Fibonacci sequence with growing squares",
    "Demonstrate Fourier series by adding sine waves",
    "Create a 3D visualization of the unit sphere",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const response = await apiService.createAnimation(description.trim());
      setSessionId(response.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create animation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-strong rounded-3xl p-8 md:p-12 space-y-8 animate-slide-up shadow-2xl">
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 rounded-full">
          <Sparkles className="w-5 h-5 text-primary-600" />
          <span className="text-sm font-semibold text-primary-700">
            AI-Powered Animation
          </span>
        </div>
        <h2 className="text-3xl md:text-4xl font-bold text-gray-800">
          Describe Your Animation
        </h2>
        <p className="text-gray-600 text-lg">
          Tell us what mathematical concept or animation you want to visualize
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Example: Create an animation showing the derivative concept. Start with a curve, then show a tangent line moving along it, highlighting how the slope changes at different points..."
            rows={8}
            className="w-full px-6 py-4 rounded-2xl border-2 border-gray-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-100 outline-none transition-all resize-none text-gray-700 placeholder:text-gray-400"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={!description.trim() || isLoading}
          className="w-full px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-bold text-lg hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-3"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
              Creating Animation...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Generate Animation
            </>
          )}
        </button>
      </form>

      {/* Examples */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          Try These Examples:
        </h3>
        <div className="grid gap-3">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => setDescription(example)}
              disabled={isLoading}
              className="text-left px-5 py-3 bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-xl transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-start gap-3">
                <span className="text-primary-500 font-bold text-sm mt-0.5 group-hover:scale-110 transition-transform">
                  {index + 1}.
                </span>
                <span className="text-gray-700 text-sm group-hover:text-primary-700 transition-colors">
                  {example}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
