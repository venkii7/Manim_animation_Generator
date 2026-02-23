import subprocess
from pathlib import Path
from typing import Tuple, Optional
import shutil

class ManimExecutor:
    """Execute Manim rendering."""
    
    def __init__(self):
        self.default_config = {
            "quality": "high_quality",
            "resolution": "1920,1080",
            "frame_rate": "60",
            "format": "mp4"
        }
    
    def render(
        self,
        code_file: Path,
        scene_name: str,
        output_dir: Path
    ) -> Tuple[bool, Optional[str], Optional[Path]]:
        """Render Manim animation."""
        
        try:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build manim command
            cmd = [
                "manim",
                "render",
                "-qh",  # High quality
                "--resolution", self.default_config["resolution"],
                "--frame_rate", self.default_config["frame_rate"],
                "--format", self.default_config["format"],
                "--media_dir", str(output_dir),
                str(code_file),
                scene_name
            ]
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                return False, f"Manim render failed:\n{result.stderr}", None
            
            # Find generated video
            video_files = list(output_dir.rglob("*.mp4"))
            if not video_files:
                return False, "Video file not generated", None
            
            # Move video to standard location
            video_file = video_files[0]
            target_file = output_dir / "animation.mp4"
            shutil.move(str(video_file), str(target_file))
            
            return True, None, target_file
        
        except subprocess.TimeoutExpired:
            return False, "Rendering timeout (>5 minutes)", None
        except Exception as e:
            return False, f"Execution error: {str(e)}", None
