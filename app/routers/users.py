"""
Users router - Handles user registration and authentication endpoints.

Endpoints:
- POST /users/register - Create a new user account
- POST /users/login - Authenticate and get a token

These map to HTTP concepts:
- POST = Create something new
- Request body = JSON data sent by client
- Response = JSON data + status code sent back
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import UserService
from app.auth.security import create_access_token

# Create a router for user-related endpoints
router = APIRouter(
    prefix="/users",  # All routes here start with /users
    tags=["Users"]    # Groups these in the API docs
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED  # 201 = Created (success)
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    HTTP: POST /users/register
    Body: {"username": "john", "email": "john@example.com", "password": "secret123"}
    
    Returns:
        201 Created - User was created successfully
        400 Bad Request - Validation error or email/username taken
    
    How it works:
    1. FastAPI automatically validates the request body using UserCreate schema
    2. If validation fails, returns 400 with error details
    3. UserService creates the user (hashes password, saves to DB)
    4. Returns the created user (without password!)
    """
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        # Email or username already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT token.
    
    HTTP: POST /users/login
    Body: {"email": "john@example.com", "password": "secret123"}
    
    Returns:
        200 OK - {"access_token": "...", "token_type": "bearer"}
        401 Unauthorized - Invalid credentials
    
    How it works:
    1. Check if email exists and password matches
    2. If valid, create a JWT token containing the user's email
    3. Return the token (client stores this and sends with future requests)
    """
    user_service = UserService(db)
    
    # Try to authenticate
    user = user_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }