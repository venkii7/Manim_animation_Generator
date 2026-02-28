from backend.services.claude_client import ClaudeClient
from backend.models.schemas import AnimationPlan

class PlanningAgent:
    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client
        self.system_instruction = """You are an expert Manim animation planner.

Your job is to create detailed, structured plans for mathematical and educational animations.

Guidelines:
- Break down animations into clear objects and timeline events
- Use standard Manim object types: Circle, Square, Rectangle, Text, MathTex, Tex, Arrow, Line, Dot, NumberPlane, Axes, Graph, etc.
- Position coordinates: [x, y, z] where center is [0, 0, 0], LEFT is [-7, 0, 0], RIGHT is [7, 0, 0], UP is [0, 4, 0], DOWN is [0, -4, 0]
- Common colors: BLUE, RED, GREEN, YELLOW, WHITE, BLACK, ORANGE, PURPLE, PINK
- Animation types: Create, Write, FadeIn, FadeOut, Transform, MoveToTarget, Rotate, Scale, Indicate, GrowArrow
- Keep timings realistic and well-paced
- Ensure timeline references existing object IDs

Example object positions:
- Center: [0, 0, 0]
- Top-left: [-4, 2, 0]
- Bottom-right: [4, -2, 0]"""

    async def generate_plan(self, user_description: str) -> AnimationPlan:
        """Generate animation plan from user description."""
        
        prompt = f"""Create a detailed Manim animation plan for the following concept:

"{user_description}"

Create a complete plan with:
1. Clear scene title
2. Brief description of what will be animated
3. List of all Manim objects needed (with types, positions, colors)
4. Timeline of animations in chronological order with detailed natural language descriptions
5. A comprehensive visual_description field that explains how the entire animation will look step-by-step

IMPORTANT: For each timeline event, provide a detailed "description" field that explains in natural language exactly what the viewer will see. 
For example:
- "A green arrow appears pointing towards the first matrix, drawing attention to it for 2 seconds"
- "The blue circle smoothly transforms into a red square over 1.5 seconds"
- "Text saying 'Matrix A' fades in at the top left corner with a yellow color"

The visual_description should be a paragraph explaining the complete animation flow in natural, vivid language.

Make it educational, visually appealing, and well-paced."""

        plan = await self.client.generate_structured(
            prompt=prompt,
            schema=AnimationPlan,
            system_instruction=self.system_instruction,
            temperature=self.client.planning_temperature,
            max_tokens=self.client.planning_max_tokens,
        )
        
        return plan
    
    async def regenerate_with_feedback(
        self,
        original_plan: AnimationPlan,
        feedback: str
    ) -> AnimationPlan:
        """Regenerate plan based on user feedback."""
        
        messages = [
            {
                "role": "user",
                "content": f"""Here's the current animation plan:

{original_plan.model_dump_json(indent=2)}

Please modify it based on this feedback: "{feedback}"

Return the updated complete plan."""
            }
        ]
        
        updated_plan = await self.client.chat_multi_turn(
            messages=messages,
            system_instruction=self.system_instruction,
            schema=AnimationPlan,
            max_tokens=self.client.chat_max_tokens,
        )
        
        return updated_plan
