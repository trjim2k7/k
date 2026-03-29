"""
This module defines the main FastAPI application for the 'k' project.

It includes a basic root endpoint that returns a welcome message.
It also ensures that database tables are created on application startup.
"""

from fastapi import FastAPI

from database import create_all_tables  # Import the function to create database tables

# Initialize the FastAPI application
# You can add metadata like title, description, version for your API documentation
app = FastAPI(
    title="K Project API",
    description="A basic FastAPI application for the 'k' project.",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Handles the startup event for the FastAPI application.

    This function is called once when the application starts up.
    It's used here to ensure all necessary database tables are created.
    """
    print("Application startup event: Creating database tables...")
    create_all_tables()
    print("Database tables created successfully.")


@app.get("/", summary="Root endpoint", response_description="A welcome message")
async def read_root() -> dict[str, str]:
    """
    Handles the root endpoint of the API.

    Returns:
        A dictionary containing a welcome message for the 'k' project.
    """
    return {"message": "Welcome to the 'k' project FastAPI application!"}

# Example of how to run this application (for development):
# uvicorn main:app --reload
#
# For production, use a WSGI server like Gunicorn with Uvicorn workers:
# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
#
# Remember to install dependencies:
# pip install "fastapi[all]" uvicorn gunicorn
