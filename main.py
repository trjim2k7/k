import time
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Record the application start time globally.
# This ensures uptime calculation starts from when the application process begins.
_app_start_time: float = time.time()

class HealthResponse(BaseModel):
    """
    Pydantic model for the health check response.
    """
    status: str = Field(..., description="Overall status of the application. 'UP' or 'DOWN'.")
    version: str = Field(..., description="Version of the application.")
    uptime: float = Field(..., description="Application uptime in seconds.")
    db_connection_status: str = Field(..., description="Status of the database connection. 'UP' or 'DOWN'.")

app = FastAPI(
    title="Health Check Service",
    description="A simple FastAPI service with a health check endpoint.",
    version="1.0.0"
)

@app.get("/health", response_model=HealthResponse, summary="Application health check", tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Returns the current health status of the application, including uptime
    and the status of its dependencies.
    """
    current_time: float = time.time()
    uptime_seconds: float = current_time - _app_start_time

    # Placeholder logic for database connection status.
    # In a real application, this would involve attempting a connection or pinging the database.
    db_status: str = "UP"

    # The overall status is "UP" if all sub-components are "UP".
    # If any critical component were "DOWN", the overall status would be "DOWN".
    overall_status: str = "UP" if db_status == "UP" else "DOWN"

    return HealthResponse(
        status=overall_status,
        version="1.0.0",  # Hardcoded as per requirement
        uptime=uptime_seconds,
        db_connection_status=db_status
    )

# To run this application:
# 1. Save it as a Python file (e.g., main.py).
# 2. Install uvicorn: pip install uvicorn fastapi pydantic
# 3. Run from your terminal: uvicorn main:app --reload
# 4. Access the health endpoint: http://127.0.0.1:8000/health
# 5. Access the FastAPI documentation: http://127.0.0.1:8000/docs