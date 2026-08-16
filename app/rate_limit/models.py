"""
Rate Limit Models module.

Defines the data structures used by the rate limiter to store state
and return results.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RateLimitState(BaseModel):
    """
    Represents the current state of a user's rate limit.
    """
    user_id: str
    request_count: int
    window_started_at: datetime

class RateLimitResult(BaseModel):
    """
    Represents the outcome of a rate limit check.
    """
    allowed: bool
    limit: int
    remaining: int
    reset_at: datetime
    retry_after: Optional[int] = None
