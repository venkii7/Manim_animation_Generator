# Manim Animation Generator

AI-powered tool to generate Manim animations using Gemini Flash 2.5.

## Features

- 🎬 Generate animation plans from natural language descriptions
- ✏️ Edit and refine plans with AI feedback
- 💻 Automatic Manim code generation with validation
- 🎥 Video rendering with high-quality output
- 🔄 Multi-stage workflow with real-time status updates

## Setup

### Backend

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Manim:**
```bash
# macOS
brew install py3cairo ffmpeg
pip install manim

# Or follow official docs: https://docs.manim.community/en/stable/installation.html
```

3. **Set up environment:**
```bash
# .env file already contains API key
cp .env.example .env  # if needed
```

4. **Run backend:**
```bash
python run_backend.py
```

Backend will run on: http://localhost:8000

### Frontend

(Coming next - React + TypeScript + Vite)

## API Endpoints

### Create Animation
```bash
POST /api/v1/animations
{
  "description": "Show matrix multiplication with two 2x2 matrices"
}
```

### Get Status
```bash
GET /api/v1/animations/{session_id}/status
```

### Get/Update Plan
```bash
GET /api/v1/animations/{session_id}/plan
PUT /api/v1/animations/{session_id}/plan
```

### Regenerate Plan with Feedback
```bash
POST /api/v1/animations/{session_id}/regenerate-plan
{
  "feedback": "Make circles bigger and use blue color"
}
```

### Generate Code
```bash
POST /api/v1/animations/{session_id}/generate-code
```

### Get/Update Code
```bash
GET /api/v1/animations/{session_id}/code
PUT /api/v1/animations/{session_id}/code
{
  "code": "from manim import *\n..."
}
```

### Render Video
```bash
POST /api/v1/animations/{session_id}/render
```

### Download Video
```bash
GET /api/v1/animations/{session_id}/video
```

## Project Structure

```
backend/
├── api/
│   └── main.py              # FastAPI endpoints
├── agents/
│   ├── planning_agent.py    # AI planning agent
│   └── code_generator.py    # Code generation agent
├── services/
│   ├── gemini_client.py     # Gemini API client
│   ├── session_manager.py   # Session management
│   ├── code_validator.py    # Code validation
│   └── manim_executor.py    # Manim rendering
└── models/
    └── schemas.py           # Pydantic models

storage/
└── sessions/                # Session files
    └── {session_id}/
        ├── metadata.json
        ├── plan.json
        ├── code.json
        ├── animation.py
        └── output/
            └── animation.mp4
```

## Workflow Stages

1. **Input** - User provides animation description
2. **Planning** - AI generates structured plan (JSON)
3. **Plan Ready** - User can review/edit/regenerate plan
4. **Code Generating** - AI generates Manim Python code
5. **Code Ready** - User can review/edit code
6. **Rendering** - Manim renders video
7. **Completed** - Video ready for download

## Technologies

- **Backend:** FastAPI + Python 3.11+
- **AI:** Google Gemini Flash 2.5
- **Animation:** Manim Community Edition v0.18
- **Validation:** Pydantic + AST parsing
- **Frontend:** React + TypeScript + Vite (coming soon)

## License

MIT
# manim-autogen-animation
