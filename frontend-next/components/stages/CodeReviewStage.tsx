"use client";

import { useState } from "react";
import { useAnimationStore } from "@/store/animation";
import { apiService } from "@/lib/api";
import { Play, Edit3, Save, X, Code2 } from "lucide-react";

export function CodeReviewStage() {
  const { sessionId, code, setCode, setLoading, setError, isLoading } =
    useAnimationStore();
  const [isEditing, setIsEditing] = useState(false);
  const [editedCode, setEditedCode] = useState(code?.code || "");
  const [validationError, setValidationError] = useState<string | null>(null);

  if (!code || !sessionId) return null;

  const handleSave = async () => {
    try {
      setValidationError(null);
      await apiService.updateCode(sessionId, editedCode);
      setCode({ ...code, code: editedCode });
      setIsEditing(false);
    } catch (err) {
      setValidationError(err instanceof Error ? err.message : "Failed to update code");
    }
  };

  const handleCancel = () => {
    setEditedCode(code.code);
    setIsEditing(false);
    setValidationError(null);
  };

  const handleRender = async () => {
    try {
      setLoading(true);
      setError(null);
      await apiService.renderAnimation(sessionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to render animation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Header */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
              <Code2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Generated Code</h2>
              <p className="text-sm text-gray-600">Scene: {code.scene_class_name}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Explanation */}
      {code.explanation && (
        <div className="glass-strong rounded-2xl p-6 shadow-xl bg-blue-50">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            💡 Code Explanation
          </h3>
          <p className="text-gray-700 leading-relaxed">{code.explanation}</p>
        </div>
      )}

      {/* Imports */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          📦 Required Imports
        </h3>
        <div className="flex flex-wrap gap-2">
          {code.imports.map((imp, idx) => (
            <code
              key={idx}
              className="px-3 py-1.5 bg-gray-800 text-green-400 rounded-lg text-sm font-mono"
            >
              {imp}
            </code>
          ))}
        </div>
      </div>

      {/* Validation Error */}
      {validationError && (
        <div className="glass-strong rounded-2xl p-4 border-l-4 border-red-500">
          <p className="text-red-600 font-medium">{validationError}</p>
        </div>
      )}

      {/* Code Display/Editor */}
      <div className="glass-strong rounded-2xl overflow-hidden shadow-xl">
        <div className="bg-gray-800 px-6 py-3 flex items-center justify-between">
          <span className="text-gray-300 font-mono text-sm">animation.py</span>
          {!isEditing && (
            <button
              onClick={() => {
                setIsEditing(true);
                setEditedCode(code.code);
              }}
              disabled={isLoading}
              className="flex items-center gap-2 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              <Edit3 className="w-4 h-4" />
              Edit Code
            </button>
          )}
        </div>

        {isEditing ? (
          <textarea
            value={editedCode}
            onChange={(e) => setEditedCode(e.target.value)}
            className="w-full h-96 px-6 py-4 bg-gray-900 text-gray-100 font-mono text-sm focus:outline-none resize-none"
            spellCheck={false}
          />
        ) : (
          <pre className="px-6 py-4 bg-gray-900 overflow-x-auto">
            <code className="text-gray-100 font-mono text-sm leading-relaxed">
              {code.code}
            </code>
          </pre>
        )}
      </div>

      {/* Actions */}
      <div className="glass-strong rounded-2xl p-6 shadow-xl">
        {isEditing ? (
          <div className="flex gap-4">
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-5 h-5" />
              Save Changes
            </button>
            <button
              onClick={handleCancel}
              disabled={isLoading}
              className="px-6 py-4 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <X className="w-5 h-5" />
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={handleRender}
            disabled={isLoading}
            className="w-full px-6 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Play className="w-5 h-5" />
            Render Animation
          </button>
        )}
      </div>
    </div>
  );
}
