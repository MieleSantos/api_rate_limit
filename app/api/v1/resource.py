"""
API Resource module.

Contains the protected endpoints that demonstrate rate limiting.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.rate_limit.dependency import rate_limit_dependency

router = APIRouter()

class ResourceResponse(BaseModel):
    """
    Response model for the resource endpoint.
    """
    message: str
    user_id: str

@router.get("/resource", response_model=ResourceResponse)
async def get_resource(user_id: str = Depends(rate_limit_dependency)) -> ResourceResponse:
    """
    Protected resource endpoint.
    
    This endpoint is protected by a user-based rate limit dependency.
    If the limit is exceeded, a 429 Too Many Requests response is returned.
    """
    return ResourceResponse(message="Request accepted", user_id=user_id)
