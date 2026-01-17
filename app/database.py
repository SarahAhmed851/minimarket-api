"""
Database connection setup.

This file creates the connection to your SQLite database.
Think of it as the "bridge" between your Python code and the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create the database engine (the connection)
# For SQLite, we need connect_args to allow multiple threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# SessionLocal is a factory that creates database sessions
# A "session" is like a conversation with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models (tables)
# All models will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    
    How it works:
    1. Creates a new session (opens conversation with database)
    2. Yields it to your endpoint (lets you use it)
    3. Closes it when done (ends conversation)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()