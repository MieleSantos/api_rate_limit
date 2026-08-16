"""
Rate Limit Exceptions module.

Defines custom HTTP exceptions for rate limiting.
"""
from fastapi import HTTPException, status

class RateLimitExceeded(HTTPException):
    """
    Exception raised when a user exceeds their allowed rate limit.
    Includes custom headers to inform the client about their current limits.
    """
    def __init__(self, retry_after: int, limit: int, remaining: int, reset: int):
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset = reset
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset),
            }
        )
