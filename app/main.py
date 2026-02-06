import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.tasks import router as tasks_router
from app.api.auth import router as auth_router
from app.api.chatbot import router as chatbot_router
from app.database import init_db
import uvicorn
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Configure CORS based on environment
allow_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allow_origins_str:
    allow_origins = [origin.strip() for origin in allow_origins_str.split(",")]
else:
    allow_origins = ["*"]  # Default to allow all in development

if "*" in allow_origins:
    # If wildcard is used, allow credentials is not allowed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Set to False when allowing all origins
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex=os.getenv("ALLOW_ORIGIN_REGEX"),
    )

# Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": os.getenv("ENVIRONMENT", "development")}

# Debug endpoint to test functionality (only available in non-production environments)
if os.getenv("ENVIRONMENT") != "production":
    @app.post("/api/debug/signup")
    def debug_signup(full_name: str, email: str, password: str):
        from app.auth.signup_service import signup_user
        from app.database import get_session
        try:
            gen = get_session()
            db = next(gen)
            result = signup_user(db, full_name, email, password)
            next(gen, None)  # Close the session
            return result
        except Exception as e:
            next(gen, None)  # Close the session
            print(f"Debug signup error: {e}")
            traceback.print_exc()
            return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("ENVIRONMENT") != "production"
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)