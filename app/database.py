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
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # Default to development if not specified
DATABASE_URL = ""

if ENVIRONMENT == "production":
    # Production database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL or DATABASE_URL.strip() == "":
        # If no DATABASE_URL is provided in production, fall back to SQLite
        # This is useful for demo purposes on platforms like Hugging Face Spaces
        DATABASE_URL = "sqlite:///./todo_app_hf.db"
        logger.warning("No DATABASE_URL provided, falling back to SQLite for demo purposes")

    if DATABASE_URL.startswith("postgresql"):
        # For PostgreSQL, SQLAlchemy will automatically use psycopg2 if available
        engine = create_engine(DATABASE_URL, echo=False)
    else:
        # For SQLite, use the appropriate engine
        engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    # Development database configuration
    temp_db_url = os.getenv("DATABASE_URL", "")
    if not temp_db_url or temp_db_url.strip() == "":
        # If DATABASE_URL is not set or is empty, try DEV_DATABASE_URL, then default to SQLite
        temp_db_url = os.getenv("DEV_DATABASE_URL", "sqlite:///./todo_app.db")

    DATABASE_URL = temp_db_url

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
