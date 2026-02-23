import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid
from backend.models.schemas import SessionStatus, AnimationPlan, ManimCode

class SessionManager:
    def __init__(self, storage_path: str = "./storage/sessions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def create_session(self, user_input: str) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session_dir = self.storage_path / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = {
            "session_id": session_id,
            "user_input": user_input,
            "stage": "input",
            "progress": 0,
            "message": "Session created",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self._save_metadata(session_id, metadata)
        return session_id
    
    def get_session_status(self, session_id: str) -> SessionStatus:
        """Get session status."""
        metadata = self._load_metadata(session_id)
        
        # Load plan if exists
        plan = None
        plan_file = self.storage_path / session_id / "plan.json"
        if plan_file.exists():
            plan = AnimationPlan.model_validate_json(plan_file.read_text())
        
        # Load code if exists
        code = None
        code_file = self.storage_path / session_id / "code.json"
        if code_file.exists():
            code = ManimCode.model_validate_json(code_file.read_text())
        
        # Check for video
        video_url = None
        video_file = self.storage_path / session_id / "output" / "animation.mp4"
        if video_file.exists():
            video_url = f"/api/v1/animations/{session_id}/video"
        
        return SessionStatus(
            session_id=session_id,
            stage=metadata["stage"],
            progress=metadata["progress"],
            message=metadata["message"],
            plan=plan,
            code=code,
            video_url=video_url,
            error=metadata.get("error"),
            created_at=datetime.fromisoformat(metadata["created_at"]),
            updated_at=datetime.fromisoformat(metadata["updated_at"])
        )
    
    def update_stage(self, session_id: str, stage: str, progress: float, message: str):
        """Update session stage."""
        metadata = self._load_metadata(session_id)
        metadata["stage"] = stage
        metadata["progress"] = progress
        metadata["message"] = message
        metadata["updated_at"] = datetime.utcnow().isoformat()
        self._save_metadata(session_id, metadata)
    
    def save_plan(self, session_id: str, plan: AnimationPlan):
        """Save animation plan."""
        plan_file = self.storage_path / session_id / "plan.json"
        plan_file.write_text(plan.model_dump_json(indent=2))
    
    def load_plan(self, session_id: str) -> AnimationPlan:
        """Load animation plan."""
        plan_file = self.storage_path / session_id / "plan.json"
        return AnimationPlan.model_validate_json(plan_file.read_text())
    
    def save_code(self, session_id: str, code: ManimCode):
        """Save generated code."""
        # Save as JSON for metadata
        code_file = self.storage_path / session_id / "code.json"
        code_file.write_text(code.model_dump_json(indent=2))
        
        # Save as .py file for execution
        py_file = self.storage_path / session_id / "animation.py"
        py_file.write_text(code.code)
    
    def load_code(self, session_id: str) -> ManimCode:
        """Load generated code."""
        code_file = self.storage_path / session_id / "code.json"
        return ManimCode.model_validate_json(code_file.read_text())
    
    def set_error(self, session_id: str, error: str):
        """Set error state."""
        metadata = self._load_metadata(session_id)
        metadata["stage"] = "failed"
        metadata["error"] = error
        metadata["updated_at"] = datetime.utcnow().isoformat()
        self._save_metadata(session_id, metadata)
    
    def get_session_dir(self, session_id: str) -> Path:
        """Get session directory path."""
        return self.storage_path / session_id
    
    def _save_metadata(self, session_id: str, metadata: dict):
        """Save session metadata."""
        metadata_file = self.storage_path / session_id / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
    
    def _load_metadata(self, session_id: str) -> dict:
        """Load session metadata."""
        metadata_file = self.storage_path / session_id / "metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        return json.loads(metadata_file.read_text())
