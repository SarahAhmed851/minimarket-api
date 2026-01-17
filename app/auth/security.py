"""
Security utilities for authentication.

This file contains:
1. Password hashing (bcrypt) - encrypts passwords so they're safe to store
2. JWT token creation - creates login tokens for users

WHY WE HASH PASSWORDS:
- Never store plain text passwords ("password123")
- Instead, we store a hash ("$2b$12$abc...xyz")
- Even if database is hacked, passwords are safe
- bcrypt is industry standard (same as assignment requires)
"""

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt

from app.config import settings

# Password hashing context using bcrypt
# "bcrypt" is the algorithm, "deprecated='auto'" handles old hashes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    
    Example:
        hash_password("mypassword123") 
        → "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4...."
    
    The hash is different every time (due to "salt"), but
    verify_password() can still check if they match.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain password matches a hashed password.
    
    Example:
        verify_password("mypassword123", "$2b$12$LQv3c1y...") → True
        verify_password("wrongpassword", "$2b$12$LQv3c1y...") → False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT (JSON Web Token) for authentication.
    
    What is a JWT?
    - A token is like a temporary "badge" that proves who you are
    - It contains encoded data (like user ID) and an expiration time
    - The server can verify it's real using the SECRET_KEY
    
    Example:
        create_access_token({"sub": "user@email.com"})
        → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi..."
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Create the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt
