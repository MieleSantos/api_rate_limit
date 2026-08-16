"""
Rate Limit Storage module.

Defines the storage interface for the rate limiter and provides
an in-memory implementation.
"""
from typing import Protocol, Optional
from app.rate_limit.models import RateLimitState

class RateLimitStorage(Protocol):
    """
    Protocol defining the required interface for rate limit storage backends.
    """
    async def get(self, user_id: str) -> Optional[RateLimitState]:
        """Retrieve the rate limit state for a given user."""
        ...

    async def save(self, user_id: str, state: RateLimitState) -> None:
        """Save the updated rate limit state for a given user."""
        ...

class InMemoryRateLimitStorage:
    """
    In-memory implementation of the RateLimitStorage protocol.
    Stores user states in a local dictionary.
    """
    def __init__(self) -> None:
        self._storage: dict[str, RateLimitState] = {}

    async def get(self, user_id: str) -> Optional[RateLimitState]:
        """Retrieve the user's rate limit state from memory."""
        return self._storage.get(user_id)

    async def save(self, user_id: str, state: RateLimitState) -> None:
        """Save the user's rate limit state to memory."""
        self._storage[user_id] = state
