"""
This module defines the main FastAPI application for the 'k' project.

It includes a basic root endpoint that returns a welcome message.
"""

from fastapi import FastAPI

# Initialize the FastAPI application
# You can add metadata like title, description, version for your API documentation
app = FastAPI(
    title="K Project API",
    description="A basic FastAPI application for the 'k' project.",
    version="0.1.0",
)


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