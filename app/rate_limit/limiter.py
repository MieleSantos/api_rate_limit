import asyncio
from datetime import datetime, timezone
import logging
from app.rate_limit.models import RateLimitResult, RateLimitState
from app.rate_limit.storage import RateLimitStorage

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, storage: RateLimitStorage, max_requests: int, window_seconds: int):
        self.storage = storage
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def _get_lock(self, user_id: str) -> asyncio.Lock:
        async with self._global_lock:
            if user_id not in self._locks:
                self._locks[user_id] = asyncio.Lock()
            return self._locks[user_id]

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    async def allow(self, user_id: str) -> RateLimitResult:
        lock = await self._get_lock(user_id)
        
        async with lock:
            now = self._now()
            state = await self.storage.get(user_id)
            
            if state is None:
                state = RateLimitState(
                    user_id=user_id,
                    request_count=1,
                    window_started_at=now
                )
                logger.info(f"rate_limit.window_reset user_id={user_id} request_count=1 limit={self.max_requests} remaining={self.max_requests - 1}")
            else:
                window_elapsed = (now - state.window_started_at).total_seconds()
                if window_elapsed >= self.window_seconds:
                    state.request_count = 1
                    state.window_started_at = now
                    logger.info(f"rate_limit.window_reset user_id={user_id} request_count=1 limit={self.max_requests} remaining={self.max_requests - 1}")
                else:
                    if state.request_count < self.max_requests:
                        state.request_count += 1
                        logger.info(f"rate_limit.allowed user_id={user_id} request_count={state.request_count} limit={self.max_requests} remaining={self.max_requests - state.request_count}")
                    else:
                        reset_at = state.window_started_at.timestamp() + self.window_seconds
                        retry_after = int(reset_at - now.timestamp())
                        retry_after = max(0, retry_after)
                        
                        logger.info(f"rate_limit.exceeded user_id={user_id} request_count={state.request_count} limit={self.max_requests} remaining=0")
                        return RateLimitResult(
                            allowed=False,
                            limit=self.max_requests,
                            remaining=0,
                            reset_at=datetime.fromtimestamp(reset_at, tz=timezone.utc),
                            retry_after=retry_after
                        )

            await self.storage.save(user_id, state)
            
            reset_at_ts = state.window_started_at.timestamp() + self.window_seconds
            
            return RateLimitResult(
                allowed=True,
                limit=self.max_requests,
                remaining=self.max_requests - state.request_count,
                reset_at=datetime.fromtimestamp(reset_at_ts, tz=timezone.utc),
                retry_after=None
            )
