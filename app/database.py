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

# Use DATABASE_URL if set and not empty, otherwise default to local SQLite
temp_db_url = os.getenv("DATABASE_URL", "")
if not temp_db_url or temp_db_url.strip() == "":
    DATABASE_URL = "sqlite:///./todo.db"
else:
    DATABASE_URL = temp_db_url

# SQLite requires this argument; other DBs don't
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine and session
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)
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
