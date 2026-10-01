"""Smoke tests for core endpoints. Run with: pytest backend/tests -v
Requires a running Postgres (see docker-compose.yml) and ANTHROPIC_API_KEY set."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_general_intent() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/chat", json={"message": "Hello, what can you help with?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert isinstance(body["agent_trace"], list)


@pytest.mark.asyncio
async def test_forecast_requires_history() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/forecast", json={"target": "nonexistent_metric", "horizon": 10})
    assert resp.status_code == 200
    assert "Not enough history" in resp.json()["forecast"][0] if resp.json()["forecast"] else True
