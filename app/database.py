import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Determine database URL based on environment
if os.getenv("ENVIRONMENT") == "production":
    # Production database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required in production")

    # For production, we typically want to disable echo (SQL logging) for performance and security
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # Development database configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        os.getenv("DEV_DATABASE_URL", "sqlite:///./todo_app.db")  # Use SQLite for local dev if no DEV_DATABASE_URL
    )
    # Enable echo in development for debugging
    if DATABASE_URL.startswith("postgresql"):
        # For PostgreSQL, SQLAlchemy will automatically use psycopg2 if available
        engine = create_engine(DATABASE_URL, echo=True)
    else:
        # For SQLite, use the appropriate engine
        engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create database tables based on SQLModel metadata"""
    logger.info("Initializing database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized successfully")

def get_session():
    """Dependency for providing database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
