"""
User model - represents the 'users' table in your database.

Think of a model as a blueprint that tells Python:
- What columns the table has
- What type of data each column holds
- Any rules (like "email must be unique")
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    User model - each row in the 'users' table becomes a User object.
    
    Columns:
    - id: Unique number for each user (auto-generated)
    - username: Display name (must be unique)
    - email: Email address (must be unique)
    - hashed_password: Encrypted password (NEVER store plain passwords!)
    - created_at: When the account was created
    - updated_at: When the account was last modified
    """
    
    # This is the actual table name in the database
    __tablename__ = "users"
    
    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)
    
    # Username - must be unique, can't be empty
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # Email - must be unique, can't be empty
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    # Password - stored as a hash (encrypted), can't be empty
    hashed_password = Column(String(255), nullable=False)
    
    # Timestamps - automatically set when row is created/updated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship - a user can have many products
    products = relationship("Product", back_populates="owner")

