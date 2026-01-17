"""
User schemas (DTOs - Data Transfer Objects).

Schemas define:
1. What data the API ACCEPTS (input validation)
2. What data the API RETURNS (output formatting)

Think of schemas as "contracts" - they guarantee the data shape.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    """
    Schema for creating a new user (registration).
    
    Validations:
    - username: 3-50 characters, alphanumeric + underscore only
    - email: Must be valid email format
    - password: Minimum 8 characters, must have letter + number
    """
    
    username: str = Field(
        ...,  # ... means required
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscore only)"
    )
    
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )
    
    # Custom validator for username format
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        """Username must be alphanumeric with underscores only."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v
    
    # Custom validator for password strength
    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Password must contain at least one letter and one number."""
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    """
    Schema for user login.
    
    User logs in with email and password.
    """
    
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    
    IMPORTANT: This does NOT include the password!
    Never send password back to the client.
    """
    
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    
    class Config:
        # This allows the schema to read data from ORM objects (database models)
        from_attributes = True