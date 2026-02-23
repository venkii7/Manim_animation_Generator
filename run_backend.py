#!/usr/bin/env python3
"""Run the FastAPI backend server."""

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled to prevent interrupting background tasks
        log_level="info"
    )
