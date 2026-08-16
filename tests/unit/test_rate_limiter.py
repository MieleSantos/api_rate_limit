import pytest
from datetime import datetime, timezone
import asyncio
from unittest.mock import patch
from app.rate_limit.storage import InMemoryRateLimitStorage
from app.rate_limit.limiter import RateLimiter

@pytest.fixture
def storage():
    return InMemoryRateLimitStorage()

@pytest.fixture
def limiter(storage):
    return RateLimiter(storage=storage, max_requests=100, window_seconds=60)

@pytest.mark.asyncio
async def test_ut01_first_request_allowed(limiter):
    result = await limiter.allow("user1")
    assert result.allowed
    assert result.remaining == 99

@pytest.mark.asyncio
async def test_ut02_requests_1_to_100_allowed(limiter):
    for i in range(100):
        result = await limiter.allow("user2")
        assert result.allowed
        assert result.remaining == 99 - i

@pytest.mark.asyncio
async def test_ut03_request_101_blocked(limiter):
    for _ in range(100):
        await limiter.allow("user3")
    
    result = await limiter.allow("user3")
    assert not result.allowed
    assert result.remaining == 0

@pytest.mark.asyncio
async def test_ut04_window_expiration_resets(limiter):
    now1 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch.object(limiter, '_now', return_value=now1):
        await limiter.allow("user4")
    
    now2 = datetime(2023, 1, 1, 12, 1, 1, tzinfo=timezone.utc)
    with patch.object(limiter, '_now', return_value=now2):
        result = await limiter.allow("user4")
        
    assert result.allowed
    assert result.remaining == 99

@pytest.mark.asyncio
async def test_ut05_different_users_independent(limiter):
    await limiter.allow("userA")
    resultA = await limiter.allow("userA")
    assert resultA.remaining == 98
    
    resultB = await limiter.allow("userB")
    assert resultB.remaining == 99

@pytest.mark.asyncio
async def test_ut06_retry_after_calculation(limiter):
    now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch.object(limiter, '_now', return_value=now):
        for _ in range(100):
            await limiter.allow("user6")
        result = await limiter.allow("user6")
        
    assert not result.allowed
    assert result.retry_after == 60

@pytest.mark.asyncio
async def test_ut07_concurrent_access(limiter):
    async def make_request():
        return await limiter.allow("user7")
        
    tasks = [make_request() for _ in range(150)]
    results = await asyncio.gather(*tasks)
    
    allowed_count = sum(1 for r in results if r.allowed)
    blocked_count = sum(1 for r in results if not r.allowed)
    
    assert allowed_count == 100
    assert blocked_count == 50
