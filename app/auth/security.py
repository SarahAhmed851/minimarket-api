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
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for JWT token in Authorization header
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    
    Example:
        hash_password("mypassword123") 
        → "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4...."
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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the currently logged-in user from the JWT token.
    
    How it works:
    1. User sends request with: Authorization: Bearer <token>
    2. We extract and decode the token
    3. We get the user's email from the token
    4. We fetch the user from the database
    5. We return the User object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user