"""
Rate Limit Dependency module.

Provides a FastAPI dependency for injecting rate limits into endpoints.
"""
from fastapi import Header, HTTPException, Response
from app.core.config import settings
from app.rate_limit.storage import InMemoryRateLimitStorage
from app.rate_limit.limiter import RateLimiter
from app.rate_limit.exceptions import RateLimitExceeded

# Global instance
_storage = InMemoryRateLimitStorage()
_limiter = RateLimiter(
    storage=_storage,
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds
)

async def rate_limit_dependency(response: Response, x_user_id: str = Header(default=None, alias="X-User-Id")) -> str:
    """
    FastAPI dependency that enforces the rate limit per user.
    
    Reads the user identifier from the X-User-Id header. If the limit is
    exceeded, it raises a RateLimitExceeded exception. Otherwise, it
    injects rate limit headers into the HTTP response.
    
    Args:
        response: The FastAPI response object used to inject headers.
        x_user_id: The user ID extracted from the request headers.
        
    Returns:
        The validated user ID.
    """
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header is required")
        
    result = await _limiter.allow(x_user_id)
    
    if not result.allowed:
        raise RateLimitExceeded(
            retry_after=result.retry_after or 0,
            limit=result.limit,
            remaining=result.remaining,
            reset=int(result.reset_at.timestamp())
        )
        
    response.headers["X-RateLimit-Limit"] = str(result.limit)
    response.headers["X-RateLimit-Remaining"] = str(result.remaining)
    response.headers["X-RateLimit-Reset"] = str(int(result.reset_at.timestamp()))
    
    return x_user_id
