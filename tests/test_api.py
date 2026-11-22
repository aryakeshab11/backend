import pytest
from httpx2 import AsyncClient

import app.main as main_module


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=main_module.app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_endpoint(monkeypatch):
    monkeypatch.setattr(main_module, "call_llm", lambda message, goals=None, context=None, model=None: "fake-reply")

    async with AsyncClient(app=main_module.app, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "hello coach"})
        assert response.status_code == 200
        body = response.json()
        assert body["reply"] == "fake-reply"
        assert body["model"] == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_chat_endpoint_requires_message():
    async with AsyncClient(app=main_module.app, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "   "})
        assert response.status_code == 400
