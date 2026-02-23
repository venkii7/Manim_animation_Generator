from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class ObjectState(BaseModel):
    position: List[float] = Field(description="[x, y, z] coordinates")
    color: str = Field(description="Color name or hex")
    scale: float = Field(default=1.0, description="Scale factor")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)

class ManimObject(BaseModel):
    id: str = Field(description="Unique identifier for the object")
    type: str = Field(description="Manim object type (Circle, Square, Text, etc.)")
    properties: Optional[str] = Field(default=None, description="JSON string of object-specific properties")
    initial_state: ObjectState

class TimelineEvent(BaseModel):
    start_time: float = Field(ge=0, description="Start time in seconds")
    duration: float = Field(default=1.0, ge=0.1, description="Duration in seconds")
    animation: str = Field(description="Animation type (Create, FadeIn, Transform, etc.)")
    target: str = Field(description="Target object ID")
    params: Optional[str] = Field(default=None, description="JSON string of animation parameters")
    description: str = Field(description="Natural language description of what happens in this animation step")

class AnimationPlan(BaseModel):
    scene_title: str = Field(description="Title of the scene")
    description: str = Field(description="Brief description of the animation")
    duration: float = Field(ge=1, le=300, description="Total duration in seconds")
    objects: List[ManimObject] = Field(description="List of Manim objects")
    timeline: List[TimelineEvent] = Field(description="Animation timeline")
    visual_description: str = Field(description="Detailed natural language explanation of how the entire animation will look, describing each visual step")

class ManimCode(BaseModel):
    code: str = Field(description="Complete Manim Python code")
    scene_class_name: str = Field(description="Name of the Scene class")
    imports: List[str] = Field(description="Required import statements")
    explanation: Optional[str] = Field(default=None, description="Code explanation")

class SessionStatus(BaseModel):
    session_id: str
    stage: Literal["input", "planning", "plan_ready", "code_generating", 
                   "code_ready", "rendering", "completed", "failed"]
    progress: float = Field(ge=0, le=100)
    message: str
    plan: Optional[AnimationPlan] = None
    code: Optional[ManimCode] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
