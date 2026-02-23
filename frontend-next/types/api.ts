// API Types matching backend schemas

export interface ObjectState {
  position: [number, number, number];
  color: string;
  scale: number;
  opacity: number;
}

export interface ManimObject {
  id: string;
  type: string;
  properties?: string;
  initial_state: ObjectState;
}

export interface TimelineEvent {
  start_time: number;
  duration: number;
  animation: string;
  target: string;
  params?: string;
  description: string;
}

export interface AnimationPlan {
  scene_title: string;
  description: string;
  duration: number;
  objects: ManimObject[];
  timeline: TimelineEvent[];
  visual_description: string;
}

export interface ManimCode {
  code: string;
  scene_class_name: string;
  imports: string[];
  explanation?: string;
}

export type SessionStage =
  | "input"
  | "planning"
  | "plan_ready"
  | "code_generating"
  | "code_ready"
  | "rendering"
  | "completed"
  | "failed";

export interface SessionStatus {
  session_id: string;
  stage: SessionStage;
  progress: number;
  message: string;
  plan?: AnimationPlan;
  code?: ManimCode;
  video_url?: string;
  error?: string;
  created_at: string;
  updated_at: string;
}
