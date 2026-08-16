from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RateLimitState(BaseModel):
    user_id: str
    request_count: int
    window_started_at: datetime

class RateLimitResult(BaseModel):
    allowed: bool
    limit: int
    remaining: int
    reset_at: datetime
    retry_after: Optional[int] = None
