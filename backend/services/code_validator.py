import ast
from typing import Tuple, Optional

class CodeValidator:
    """Validate Python/Manim code."""
    
    def validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check if code has valid Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_manim_structure(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check if code has proper Manim structure."""
        try:
            tree = ast.parse(code)
            
            # Check for Scene class
            has_scene_class = False
            has_construct = False
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from Scene
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in ['Scene', 'ThreeDScene', 'MovingCameraScene']:
                            has_scene_class = True
                            # Check for construct method
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef) and item.name == 'construct':
                                    has_construct = True
            
            if not has_scene_class:
                return False, "No class inheriting from Scene found"
            
            if not has_construct:
                return False, "No construct() method found in Scene class"
            
            return True, None
        
        except Exception as e:
            return False, f"Structure validation failed: {str(e)}"
