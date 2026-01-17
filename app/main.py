"""
MiniMarket API - Main Application

This is the entry point of your FastAPI application.
It creates the app, connects all the routers, and sets up the database.

To run the app:
    uvicorn app.main:app --reload

Then open http://localhost:8000/docs to see your API documentation!
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import health, users, products

# Create all database tables
# This creates the tables defined in your models if they don't exist
Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title="MiniMarket API",
    description="A simple marketplace API for the Web Security course",
    version="1.0.0"
)

# Add CORS middleware (allows requests from web browsers)
# This is important if you ever add a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (connect all the endpoints)
app.include_router(health.router)
app.include_router(users.router)
app.include_router(products.router)


# You can also add a startup event for any initialization
@app.on_event("startup")
async def startup_event():
    """Runs when the application starts."""
    print("🚀 MiniMarket API is starting up!")
    print("📚 Visit http://localhost:8000/docs for API documentation")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the application shuts down."""
    print("👋 MiniMarket API is shutting down!")
