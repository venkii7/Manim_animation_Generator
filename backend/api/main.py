from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

from backend.services.gemini_client import GeminiClient
from backend.services.session_manager import SessionManager
from backend.services.code_validator import CodeValidator
from backend.services.manim_executor import ManimExecutor
from backend.agents.planning_agent import PlanningAgent
from backend.agents.code_generator import CodeGenerator
from backend.models.schemas import AnimationPlan, ManimCode

app = FastAPI(title="Manim Animation Generator")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173"
    ],  # Next.js and Vite ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
gemini_client = GeminiClient()
session_manager = SessionManager()
code_validator = CodeValidator()
manim_executor = ManimExecutor()
planning_agent = PlanningAgent(gemini_client)
code_generator = CodeGenerator(gemini_client)

# Request/Response models
class CreateAnimationRequest(BaseModel):
    description: str

class RegeneratePlanRequest(BaseModel):
    feedback: str

class UpdatePlanRequest(BaseModel):
    plan: AnimationPlan

class UpdateCodeRequest(BaseModel):
    code: str

# Background task for planning
async def generate_plan_task(session_id: str, description: str):
    try:
        session_manager.update_stage(session_id, "planning", 30, "Generating animation plan...")
        
        plan = await planning_agent.generate_plan(description)
        
        session_manager.save_plan(session_id, plan)
        session_manager.update_stage(session_id, "plan_ready", 50, "Plan generated successfully")
    
    except Exception as e:
        session_manager.set_error(session_id, str(e))

# Background task for code generation
async def generate_code_task(session_id: str):
    try:
        session_manager.update_stage(session_id, "code_generating", 60, "Generating Manim code...")
        
        plan = session_manager.load_plan(session_id)
        code = await code_generator.generate_code(plan)
        
        # Validate syntax
        is_valid, error = code_validator.validate_syntax(code.code)
        if not is_valid:
            raise Exception(f"Generated code has syntax errors: {error}")
        
        # Validate Manim structure
        is_valid, error = code_validator.validate_manim_structure(code.code)
        if not is_valid:
            raise Exception(f"Code structure invalid: {error}")
        
        session_manager.save_code(session_id, code)
        session_manager.update_stage(session_id, "code_ready", 75, "Code generated successfully")
    
    except Exception as e:
        session_manager.set_error(session_id, str(e))

# Background task for rendering
async def render_video_task(session_id: str, scene_name: str):
    try:
        session_manager.update_stage(session_id, "rendering", 80, "Rendering video...")
        
        session_dir = session_manager.get_session_dir(session_id)
        code_file = session_dir / "animation.py"
        output_dir = session_dir / "output"
        
        # Render
        success, error, video_path = await asyncio.to_thread(
            manim_executor.render,
            code_file,
            scene_name,
            output_dir
        )
        
        if not success:
            raise Exception(error)
        
        session_manager.update_stage(session_id, "completed", 100, "Animation completed!")
    
    except Exception as e:
        session_manager.set_error(session_id, str(e))

# Endpoints

@app.post("/api/v1/animations")
async def create_animation(request: CreateAnimationRequest, background_tasks: BackgroundTasks):
    """Create new animation session and start planning."""
    
    session_id = session_manager.create_session(request.description)
    
    # Start planning in background
    background_tasks.add_task(generate_plan_task, session_id, request.description)
    
    return {"session_id": session_id, "message": "Animation creation started"}

@app.get("/api/v1/animations/{session_id}/status")
async def get_status(session_id: str):
    """Get animation session status."""
    
    try:
        status = session_manager.get_session_status(session_id)
        return status
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/v1/animations/{session_id}/plan")
async def get_plan(session_id: str):
    """Get animation plan."""
    
    try:
        plan = session_manager.load_plan(session_id)
        return plan
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan not found")

@app.put("/api/v1/animations/{session_id}/plan")
async def update_plan(session_id: str, request: UpdatePlanRequest):
    """Update animation plan (user edited)."""
    
    try:
        session_manager.save_plan(session_id, request.plan)
        session_manager.update_stage(session_id, "plan_ready", 50, "Plan updated by user")
        return {"message": "Plan updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/animations/{session_id}/regenerate-plan")
async def regenerate_plan(session_id: str, request: RegeneratePlanRequest, background_tasks: BackgroundTasks):
    """Regenerate plan with user feedback."""
    
    try:
        current_plan = session_manager.load_plan(session_id)
        
        async def regenerate_task():
            try:
                session_manager.update_stage(session_id, "planning", 30, "Regenerating plan with feedback...")
                
                new_plan = await planning_agent.regenerate_with_feedback(current_plan, request.feedback)
                
                session_manager.save_plan(session_id, new_plan)
                session_manager.update_stage(session_id, "plan_ready", 50, "Plan regenerated successfully")
            except Exception as e:
                session_manager.set_error(session_id, str(e))
        
        background_tasks.add_task(regenerate_task)
        return {"message": "Plan regeneration started"}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan not found")

@app.post("/api/v1/animations/{session_id}/generate-code")
async def generate_code_endpoint(session_id: str, background_tasks: BackgroundTasks):
    """Generate Manim code from approved plan."""
    
    background_tasks.add_task(generate_code_task, session_id)
    return {"message": "Code generation started"}

@app.get("/api/v1/animations/{session_id}/code")
async def get_code(session_id: str):
    """Get generated Manim code."""
    
    try:
        code = session_manager.load_code(session_id)
        return code
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Code not found")

@app.put("/api/v1/animations/{session_id}/code")
async def update_code(session_id: str, request: UpdateCodeRequest):
    """Update code (user edited) with validation."""
    
    # Validate syntax
    is_valid, error = code_validator.validate_syntax(request.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Syntax error: {error}")
    
    # Validate Manim structure
    is_valid, error = code_validator.validate_manim_structure(request.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Structure error: {error}")
    
    try:
        # Load existing code to preserve metadata
        existing_code = session_manager.load_code(session_id)
        existing_code.code = request.code
        
        session_manager.save_code(session_id, existing_code)
        return {"message": "Code updated and validated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/animations/{session_id}/render")
async def render_animation(session_id: str, background_tasks: BackgroundTasks):
    """Render animation video."""
    
    try:
        code = session_manager.load_code(session_id)
        background_tasks.add_task(render_video_task, session_id, code.scene_class_name)
        return {"message": "Rendering started"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Code not found")

@app.get("/api/v1/animations/{session_id}/video")
async def get_video(session_id: str):
    """Download animation video."""
    
    session_dir = session_manager.get_session_dir(session_id)
    video_file = session_dir / "output" / "animation.mp4"
    
    if not video_file.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_file,
        media_type="video/mp4",
        filename=f"animation_{session_id}.mp4"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
