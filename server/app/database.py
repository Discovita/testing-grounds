"""
Database connection module for the State Machine Demo application.

This module sets up the SQLAlchemy database engine and session management for SQLite.
It provides functions for initializing the database and creating sessions.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite path
# Database URL in format: sqlite:///./state_machine_demo.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./state_machine_demo.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for SQLAlchemy models
Base = declarative_base()

def get_db():
    """
    Get a database session.
    
    This function creates a new database session for each request and
    ensures it's closed when the request is complete.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    
    This function should be called once when the application starts.
    It creates all tables defined in SQLAlchemy models.
    """
    # Import all models here to ensure they are registered with the Base metadata
    import app.schemas
    
    # Create tables
    Base.metadata.create_all(bind=engine) 