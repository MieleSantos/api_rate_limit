import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_api01_no_user_id(client):
    response = await client.get("/api/v1/resource")
    assert response.status_code == 400
    assert response.json()["detail"] == "X-User-Id header is required"

@pytest.mark.asyncio
async def test_api02_within_limit(client):
    response = await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Request accepted", "user_id": "apiuser1"}
    assert "x-ratelimit-limit" in response.headers

@pytest.mark.asyncio
async def test_api03_after_100_requests(client):
    for _ in range(100):
        await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser3"})
        
    response = await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser3"})
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded. Try again later."

@pytest.mark.asyncio
async def test_api04_429_contains_headers(client):
    for _ in range(100):
        await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser4"})
        
    response = await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser4"})
    assert response.status_code == 429
    assert "retry-after" in response.headers
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert response.headers["x-ratelimit-remaining"] == "0"

@pytest.mark.asyncio
async def test_api05_different_users(client):
    for _ in range(100):
        await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser5A"})
        
    resA = await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser5A"})
    assert resA.status_code == 429
    
    resB = await client.get("/api/v1/resource", headers={"X-User-Id": "apiuser5B"})
    assert resB.status_code == 200
