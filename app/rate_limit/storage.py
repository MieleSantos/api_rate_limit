from typing import Protocol, Optional
from app.rate_limit.models import RateLimitState

class RateLimitStorage(Protocol):
    async def get(self, user_id: str) -> Optional[RateLimitState]:
        ...

    async def save(self, user_id: str, state: RateLimitState) -> None:
        ...

class InMemoryRateLimitStorage:
    def __init__(self) -> None:
        self._storage: dict[str, RateLimitState] = {}

    async def get(self, user_id: str) -> Optional[RateLimitState]:
        return self._storage.get(user_id)

    async def save(self, user_id: str, state: RateLimitState) -> None:
        self._storage[user_id] = state
