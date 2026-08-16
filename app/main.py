"""
Main application module.

Initializes the FastAPI application and includes the API routers.
"""
from typing import Dict
from fastapi import FastAPI
from app.api.v1.resource import router as resource_router

app = FastAPI(title="Rate Limit Simulation API")

app.include_router(resource_router, prefix="/api/v1")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns a simple status indicator to verify the API is running.
    """
    return {"status": "healthy"}
