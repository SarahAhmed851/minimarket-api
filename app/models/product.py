"""
Product Model
This represents a product in the marketplace.
Each product belongs to a user (the one who created it).
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    """
    Product database model.
    
    Attributes:
        id: Unique identifier for the product
        name: Product name (max 100 characters)
        description: Detailed description of the product (optional)
        price: Product price (must be positive)
        user_id: ID of the user who created this product (foreign key)
        created_at: Timestamp when product was created
        updated_at: Timestamp when product was last updated
        
    Relationships:
        owner: The User who created this product
    """
    __tablename__ = "products"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    
    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship: Product belongs to a User
    # This allows us to access: product.owner.username
    owner = relationship("User", back_populates="products")
    
    def __repr__(self):
        """String representation of Product for debugging."""
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, owner_id={self.user_id})>"