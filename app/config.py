"""
Configuration settings for the application.

This file reads values from the .env file and makes them available
throughout the app. Think of it as a central place for all settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class that automatically reads from .env file.
    
    How it works:
    - Each variable here matches a variable in .env
    - Pydantic automatically loads them when the app starts
    """
    
    # Database URL - where your data lives
    DATABASE_URL: str = "sqlite:///./database.db"
    
    # JWT (login token) settings
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        # This tells Pydantic to read from .env file
        env_file = ".env"


# Create one instance of settings to use everywhere
settings = Settings()