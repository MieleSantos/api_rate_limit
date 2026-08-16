from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.rate_limit.dependency import rate_limit_dependency

router = APIRouter()

class ResourceResponse(BaseModel):
    message: str
    user_id: str

@router.get("/resource", response_model=ResourceResponse)
async def get_resource(user_id: str = Depends(rate_limit_dependency)) -> ResourceResponse:
    return ResourceResponse(message="Request accepted", user_id=user_id)
