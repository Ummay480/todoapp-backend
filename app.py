"""
Hugging Face Space Compatibility Entry Point

This file serves as a compatibility layer for Hugging Face Spaces
to recognize and run the FastAPI application.
"""

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")

    # Run with uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False  # Disable reload in production
    )