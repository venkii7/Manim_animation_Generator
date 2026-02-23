import { create } from "zustand";
import type { SessionStatus, AnimationPlan, ManimCode } from "@/types/api";

interface AnimationStore {
  sessionId: string | null;
  status: SessionStatus | null;
  plan: AnimationPlan | null;
  code: ManimCode | null;
  error: string | null;
  isLoading: boolean;
  
  setSessionId: (id: string) => void;
  setStatus: (status: SessionStatus) => void;
  setPlan: (plan: AnimationPlan | null) => void;
  setCode: (code: ManimCode | null) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;
}

export const useAnimationStore = create<AnimationStore>((set) => ({
  sessionId: null,
  status: null,
  plan: null,
  code: null,
  error: null,
  isLoading: false,
  
  setSessionId: (id) => set({ sessionId: id }),
  setStatus: (status) => set({ status }),
  setPlan: (plan) => set({ plan }),
  setCode: (code) => set({ code }),
  setError: (error) => set({ error }),
  setLoading: (loading) => set({ isLoading: loading }),
  reset: () => set({
    sessionId: null,
    status: null,
    plan: null,
    code: null,
    error: null,
    isLoading: false,
  }),
}));
