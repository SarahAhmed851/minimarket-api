"""
Health check router - Simple endpoints to verify the API is running.

This satisfies Lab 10 Task 5: "Create a simple GET endpoint"

These endpoints are useful for:
- Checking if the server is running
- Health checks (monitoring systems)
- Testing your setup works
"""

from fastapi import APIRouter

# Create a router (groups related endpoints together)
router = APIRouter(
    prefix="",  # No prefix, these are root-level endpoints
    tags=["Health"]  # Groups these in the API docs
)


@router.get("/")
def root():
    """
    Root endpoint - just says hello.
    
    HTTP: GET /
    Returns: {"message": "Welcome to MiniMarket API"}
    """
    return {"message": "Welcome to MiniMarket API"}


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    
    HTTP: GET /health
    Returns: {"status": "healthy"}
    
    Use this to check if the API is running.
    """
    return {"status": "healthy"}


@router.get("/hello")
def hello():
    """
    Simple hello endpoint (matches the Spring Boot example in the assignment).
    
    HTTP: GET /hello
    Returns: "Hello, user!"
    """
    return "Hello, user!"