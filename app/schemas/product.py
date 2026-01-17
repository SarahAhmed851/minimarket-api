"""
Product Schemas - Validation for Product data

These define what data we accept when creating/updating products
and what data we return to users.

Think of schemas as "contracts" that say:
- "When creating a product, you MUST provide: name, price"
- "When returning a product, we'll include: id, name, price, owner info, etc."
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    """
    Base schema - common fields for products.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    description: Optional[str] = Field(None, description="Product description (optional)")
    price: float = Field(..., gt=0, description="Product price (must be positive)")


class ProductCreate(ProductBase):
    """
    Schema for creating a new product.
    
    User provides: name, description (optional), price
    user_id is automatically set from the logged-in user
    """
    pass


class ProductUpdate(BaseModel):
    """
    Schema for updating a product.
    All fields are optional - update only what's provided.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)


class ProductResponse(ProductBase):
    """
    Schema for returning product data to users.
    
    Includes: id, timestamps, and owner's username
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    # Nested data - include owner's username
    owner_username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """
    Schema for returning a list of products.
    """
    total: int
    products: list[ProductResponse]