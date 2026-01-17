"""
Product Router - API endpoints for products

These are the URLs users can access:
- POST   /products          → Create a new product (auth required)
- GET    /products          → Get all products (public)
- GET    /products/my       → Get my products (auth required)
- GET    /products/{id}     → Get specific product (public)
- PUT    /products/{id}     → Update product (auth required, owner only)
- DELETE /products/{id}     → Delete product (auth required, owner only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse,
    ProductListResponse
)
from app.services.product_service import ProductService
from app.auth.security import get_current_user
from app.models.user import User

# Create router
router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    
    **Authentication Required**: You must be logged in.
    
    The product will be automatically assigned to you (the logged-in user).
    """
    new_product = ProductService.create_product(
        db=db,
        product_data=product,
        user_id=current_user.id
    )
    
    # Add owner username for response
    response_data = ProductResponse.model_validate(new_product)
    response_data.owner_username = current_user.username
    
    return response_data


@router.get("/", response_model=ProductListResponse)
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all products from all users.
    
    **Public endpoint** - No authentication required.
    
    Supports pagination:
    - skip: Number of products to skip
    - limit: Maximum number of products to return
    """
    products = ProductService.get_all_products(db=db, skip=skip, limit=limit)
    
    # Add owner usernames
    products_with_owners = []
    for product in products:
        product_data = ProductResponse.model_validate(product)
        product_data.owner_username = product.owner.username if product.owner else None
        products_with_owners.append(product_data)
    
    return ProductListResponse(
        total=len(products_with_owners),
        products=products_with_owners
    )


@router.get("/my", response_model=ProductListResponse)
async def get_my_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all YOUR products.
    
    **Authentication Required**: Shows only products you created.
    """
    products = ProductService.get_user_products(db=db, user_id=current_user.id)
    
    # Add owner username (which is the current user)
    products_with_owners = []
    for product in products:
        product_data = ProductResponse.model_validate(product)
        product_data.owner_username = current_user.username
        products_with_owners.append(product_data)
    
    return ProductListResponse(
        total=len(products_with_owners),
        products=products_with_owners
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID.
    
    **Public endpoint** - No authentication required.
    """
    product = ProductService.get_product_by_id(db=db, product_id=product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Add owner username
    product_data = ProductResponse.model_validate(product)
    product_data.owner_username = product.owner.username if product.owner else None
    
    return product_data


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a product.
    
    **Authentication Required**: You can only update YOUR OWN products.
    
    If you try to update someone else's product, you'll get a 403 Forbidden error.
    """
    updated_product = ProductService.update_product(
        db=db,
        product_id=product_id,
        product_data=product_update,
        current_user_id=current_user.id
    )
    
    # Add owner username
    product_data = ProductResponse.model_validate(updated_product)
    product_data.owner_username = current_user.username
    
    return product_data


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a product.
    
    **Authentication Required**: You can only delete YOUR OWN products.
    
    If you try to delete someone else's product, you'll get a 403 Forbidden error.
    """
    ProductService.delete_product(
        db=db,
        product_id=product_id,
        current_user_id=current_user.id
    )
    
    return None  # 204 No Content response