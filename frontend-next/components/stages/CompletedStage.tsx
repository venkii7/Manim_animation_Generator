"use client";

import { useAnimationStore } from "@/store/animation";
import { apiService } from "@/lib/api";
import { Download, RotateCcw, Sparkles } from "lucide-react";

export function CompletedStage() {
  const { sessionId, reset } = useAnimationStore();

  if (!sessionId) return null;

  const videoUrl = apiService.getVideoUrl(sessionId);

  const handleDownload = () => {
    const link = document.createElement("a");
    link.href = videoUrl;
    link.download = `animation_${sessionId}.mp4`;
    link.click();
  };

  const handleNewAnimation = () => {
    reset();
  };

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Success Header */}
      <div className="glass-strong rounded-2xl p-8 text-center shadow-xl">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mb-4">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-4xl font-bold text-gray-800 mb-2">
          🎉 Animation Complete!
        </h2>
        <p className="text-gray-600 text-lg">
          Your mathematical animation has been successfully generated
        </p>
      </div>

      {/* Video Player */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <div className="bg-black rounded-xl overflow-hidden shadow-2xl">
          <video
            controls
            autoPlay
            loop
            className="w-full h-auto"
            src={videoUrl}
          >
            Your browser does not support the video tag.
          </video>
        </div>
      </div>

      {/* Actions */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <div className="flex gap-4">
          <button
            onClick={handleDownload}
            className="flex-1 px-6 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-5 h-5" />
            Download Video
          </button>
          <button
            onClick={handleNewAnimation}
            className="flex-1 px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-5 h-5" />
            Create New Animation
          </button>
        </div>
      </div>
    </div>
  );
}
