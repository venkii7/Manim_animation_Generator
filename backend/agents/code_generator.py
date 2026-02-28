from backend.services.claude_client import ClaudeClient
from backend.models.schemas import AnimationPlan, ManimCode

class CodeGenerator:
    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client
        self.system_instruction = """You are an expert Manim code generator that outputs valid JSON.

CRITICAL JSON OUTPUT RULES:
1. You MUST output valid JSON with properly escaped strings
2. The "code" field contains Python code as a JSON string - ALL special characters must be escaped:
   - Backslashes: \\ (use double backslash)
   - Quotes: \" (escape quotes)
   - Newlines: \\n (use newline escape)
3. Python raw strings like r"..." should be written as plain strings in JSON with proper escaping
4. Example JSON output:
   {
     "code": "from manim import *\\n\\nclass MyScene(Scene):\\n    def construct(self):\\n        formula = MathTex(r\\"\\\\\\\\frac{a}{b}\\")\\n        self.play(Create(formula))",
     "scene_class_name": "MyScene",
     "imports": ["from manim import *", "import numpy as np"],
     "explanation": "Creates a fraction animation"
   }

MANIM CODE GENERATION RULES:
1. ALL LaTeX strings in Python MUST use raw strings (r"") or properly escape backslashes
2. Example: MathTex(r"\\vec{A}") or MathTex("\\\\vec{A}")
3. NEVER use single backslash in regular strings
4. RightAngle() takes two Line objects, NOT points: RightAngle(line1, line2, length=0.3)
5. To create a right angle marker, create the two lines first, then pass them to RightAngle
6. SurroundingRectangle() needs the actual mobject, not a string reference
7. DashedLine needs proper numpy arrays: DashedLine(start=np.array([x1,y1,0]), end=np.array([x2,y2,0]))

TIMING AND ANIMATION RULES:
- Use ONLY sequential self.play() and self.wait() calls for timing
- DO NOT use .set_start_and_end_time_in_scene() - this method does NOT exist in Manim
- DO NOT try to play multiple animations with different timings in a single self.play()
- Use run_time parameter for animation duration: self.play(FadeIn(obj), run_time=2)
- Use self.wait(duration) for pauses between animations
- Animations execute in order, one self.play() call at a time

Common Manim patterns:
- Create vectors: Arrow(start=ORIGIN, end=np.array([x, y, 0]), buff=0, color=BLUE)
- Create text: Text("content", font_size=40) or MathTex(r"\\text{content}")
- Highlight formulas: rect = SurroundingRectangle(formula_obj, color=YELLOW)
- Coordinate plane: NumberPlane(x_range=[-7,7,1], y_range=[-4,4,1])
- Multiple animations together: self.play(FadeIn(obj1), FadeOut(obj2))
- Animation with timing: self.play(Create(circle), run_time=2)
- Grouped animations: self.play(AnimationGroup(anim1, anim2, lag_ratio=0.5))

Guidelines:
- Always inherit from Scene (or ThreeDScene, MovingCameraScene if needed)
- Include proper imports: from manim import * and import numpy as np
- Implement construct() method
- Use self.play() for animations - each call plays all animations simultaneously
- Use self.wait() for pauses
- Follow the animation plan exactly
- Add brief comments for clarity
- Follow PEP 8 style guidelines
- Keep code simple and readable

Example structure (do NOT wrap in code fences - output plain Python in the JSON string):
from manim import *
import numpy as np

class MyScene(Scene):
    def construct(self):
        # Create objects with raw strings for LaTeX
        formula = MathTex(r"\\frac{a}{b}")
        circle = Circle(radius=1.5, color=BLUE)
        
        # Animate sequentially
        self.play(Create(circle), run_time=2)
        self.wait(0.5)
        self.play(FadeIn(formula))
        self.wait(1)

The "code" JSON field must contain ONLY the raw Python source — never wrap it in ```python ... ``` fences."""

    async def generate_code(self, plan: AnimationPlan) -> ManimCode:
        """Generate Manim code from animation plan."""
        
        prompt = f"""Generate complete, executable Manim code for this animation plan:

Scene: {plan.scene_title}
Description: {plan.description}

Objects:
{self._format_objects(plan.objects)}

Timeline:
{self._format_timeline(plan.timeline)}

IMPORTANT: Output valid JSON with these fields:
- "code": Complete Python code as a properly escaped JSON string
- "scene_class_name": Name of the main Scene class
- "imports": Array of import statements
- "explanation": Brief description of the code

Generate clean, working Manim code that:
1. Creates all objects with specified properties
2. Follows the timeline exactly
3. Uses proper Manim animations
4. Includes all necessary imports
5. Has clear comments
6. Uses raw strings for LaTeX: r"\\frac{a}{b}"

The code should be production-ready and executable."""

        code = await self.client.generate_structured(
            prompt=prompt,
            schema=ManimCode,
            system_instruction=self.system_instruction,
            temperature=self.client.code_temperature,
            max_tokens=self.client.code_max_tokens,
        )

        # Strip any markdown code fences the model may have wrapped around the code
        code.code = self._clean_code(code.code)
        return code
    
    def _clean_code(self, code: str) -> str:
        """Strip markdown code fences and leading/trailing whitespace from generated code."""
        code = code.strip()
        # Remove ```python ... ``` or ``` ... ``` wrappers
        if code.startswith("```"):
            lines = code.splitlines()
            # Drop the first line (``` or ```python)
            lines = lines[1:]
            # Drop the last closing ``` if present
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines).strip()
        return code

    def _format_objects(self, objects) -> str:
        """Format objects for prompt."""
        lines = []
        for obj in objects:
            lines.append(f"- {obj.id}: {obj.type}")
            lines.append(f"  Position: {obj.initial_state.position}")
            lines.append(f"  Color: {obj.initial_state.color}")
            if obj.properties:
                lines.append(f"  Properties: {obj.properties}")
        return "\n".join(lines)
    
    def _format_timeline(self, timeline) -> str:
        """Format timeline for prompt."""
        lines = []
        for i, event in enumerate(timeline, 1):
            lines.append(f"{i}. At {event.start_time}s: {event.animation}({event.target}) for {event.duration}s")
            if event.params:
                lines.append(f"   Params: {event.params}")
        return "\n".join(lines)
