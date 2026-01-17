"""
User Service - Business logic for user operations.

This is where the "thinking" happens:
- Creating users (with validation)
- Authenticating users (checking login)

Services sit between Controllers and Database:
    Controller → Service → Database
    (HTTP)      (Logic)   (Data)
"""

from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.security import hash_password, verify_password


class UserService:
    """
    Service class for user-related operations.
    
    Why use a service class?
    - Keeps business logic separate from HTTP handling
    - Makes code easier to test
    - Can be reused by different controllers
    """
    
    def __init__(self, db: Session):
        """Initialize with a database session."""
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address.
        
        Returns None if not found.
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by their username.
        
        Returns None if not found.
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by their ID.
        
        Returns None if not found.
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user in the database.
        
        Steps:
        1. Hash the password (NEVER store plain text!)
        2. Create User object
        3. Save to database
        4. Return the created user
        
        Raises:
            ValueError: If email or username already exists
        """
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if self.get_user_by_username(user_data.username):
            raise ValueError("Username already taken")
        
        # Create new user with hashed password
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )
        
        # Save to database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)  # Refresh to get the generated ID
        
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user (check login credentials).
        
        Steps:
        1. Find user by email
        2. If not found, return None (wrong email)
        3. Check if password matches the hash
        4. If matches, return user; otherwise return None
        
        Returns:
            User object if credentials are valid, None otherwise
        """
        # Find user by email
        user = self.get_user_by_email(email)
        
        # If user doesn't exist, authentication fails
        if not user:
            return None
        
        # Check if password matches
        if not verify_password(password, user.hashed_password):
            return None
        
        # Success! Return the user
        return user