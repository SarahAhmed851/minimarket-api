"""
Product Service - Business logic for products

This handles all the product operations:
- Creating products
- Getting products (all or by user)
- Updating products
- Deleting products
- Access control (users can only edit/delete their own products)
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional


class ProductService:
    """Service class for product operations."""
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate, user_id: int) -> Product:
        """
        Create a new product.
        
        Args:
            db: Database session
            product_data: Product information (name, description, price)
            user_id: ID of the user creating the product
            
        Returns:
            The created Product object
        """
        # Create new product instance
        new_product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            user_id=user_id
        )
        
        # Add to database
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return new_product
    
    @staticmethod
    def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get all products from all users.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Product objects
        """
        return db.query(Product).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        Get a specific product by ID.
        
        Args:
            db: Database session
            product_id: ID of the product to retrieve
            
        Returns:
            Product object or None if not found
        """
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_user_products(db: Session, user_id: int) -> List[Product]:
        """
        Get all products created by a specific user.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            List of Product objects created by the user
        """
        return db.query(Product).filter(Product.user_id == user_id).all()
    
    @staticmethod
    def update_product(
        db: Session, 
        product_id: int, 
        product_data: ProductUpdate, 
        current_user_id: int
    ) -> Product:
        """
        Update a product.
        SECURITY: Only the owner can update their product!
        
        Args:
            db: Database session
            product_id: ID of the product to update
            product_data: New product information
            current_user_id: ID of the user making the request
            
        Returns:
            Updated Product object
            
        Raises:
            HTTPException: If product not found or user is not the owner
        """
        # Get the product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # SECURITY CHECK: Only owner can update
        if product.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own products"
            )
        
        # Update only provided fields
        if product_data.name is not None:
            product.name = product_data.name
        if product_data.description is not None:
            product.description = product_data.description
        if product_data.price is not None:
            product.price = product_data.price
        
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int, current_user_id: int) -> None:
        """
        Delete a product.
        SECURITY: Only the owner can delete their product!
        
        Args:
            db: Database session
            product_id: ID of the product to delete
            current_user_id: ID of the user making the request
            
        Raises:
            HTTPException: If product not found or user is not the owner
        """
        # Get the product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # SECURITY CHECK: Only owner can delete
        if product.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own products"
            )
        
        db.delete(product)
        db.commit()
