from backend.services.gemini_client import GeminiClient
from backend.models.schemas import AnimationPlan, ManimCode

class CodeGenerator:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.system_instruction = """You are an expert Manim code generator.

Generate clean, executable Python code using Manim Community Edition v0.18+.

CRITICAL RULES:
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

Example structure:
```python
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
```"""

    async def generate_code(self, plan: AnimationPlan) -> ManimCode:
        """Generate Manim code from animation plan."""
        
        prompt = f"""Generate complete, executable Manim code for this animation plan:

Scene: {plan.scene_title}
Description: {plan.description}

Objects:
{self._format_objects(plan.objects)}

Timeline:
{self._format_timeline(plan.timeline)}

Generate clean, working Manim code that:
1. Creates all objects with specified properties
2. Follows the timeline exactly
3. Uses proper Manim animations
4. Includes all necessary imports
5. Has clear comments

The code should be production-ready and executable."""

        code = await self.client.generate_structured(
            prompt=prompt,
            schema=ManimCode,
            system_instruction=self.system_instruction,
            temperature=0.7  # Slightly lower for code generation
        )
        
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
