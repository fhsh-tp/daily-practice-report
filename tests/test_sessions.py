from fastapi import FastAPI, Request

import pytest
from httpx import AsyncClient, ASGITransport

from shared.sessions import SessionMiddleware
import secrets


@pytest.mark.asyncio
async def test_session_middleware_basic():
    """Test basic session data storage and retrieval."""
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32), session_cookie="test_session")

    @app.get("/set")
    async def set_session(request: Request):
        request.scope["session"]["user"] = "test"
        return {"status": "ok"}

    @app.get("/get")
    async def get_session(request: Request):
        return request.scope["session"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Set data
        response = await client.get("/set")
        assert response.status_code == 200
        assert "test_session" in response.cookies

        # 2. Get data
        response = await client.get("/get")
        data = response.json()
        assert data["user"] == "test"
        assert "exp" in data


@pytest.mark.asyncio
async def test_session_expiry():
    """Test session expiration."""
    app = FastAPI()
    # Expire in 1 second
    app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32), max_age=1)

    @app.get("/set")
    async def set_session(request: Request):
        request.scope["session"]["data"] = "important"
        return "ok"

    @app.get("/get")
    async def get_session(request: Request):
        return request.scope["session"].get("data")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.get("/set")

        # Verify immediately
        response = await client.get("/get")
        assert response.json() == "important"

        # Wait for expiration
        import asyncio
        await asyncio.sleep(1.1)

        # Verify expired
        response = await client.get("/get")
        assert response.json() is None


@pytest.mark.asyncio
async def test_invalid_token():
    """Test invalid token handling (should reset session)."""
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

    @app.get("/get")
    async def get_session(request: Request):
        return request.scope["session"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Manually set an invalid cookie
        client.cookies.set("session", "invalid.token.structure")

        response = await client.get("/get")
        assert response.json() == {}


@pytest.mark.asyncio
async def test_pydantic_session_struct():
    """Test using Pydantic model as session structure."""
    from pydantic import BaseModel

    class UserSession(BaseModel):
        uid: int = 0
        role: str = "guest"

    app = FastAPI()
    app.add_middleware(
        SessionMiddleware,
        secret_key=secrets.token_hex(32),
        session_struct=UserSession,
        default_session={"uid": 0, "role": "guest"}
    )

    @app.post("/login")
    async def login(request: Request):
        # Modify the Pydantic model in the session
        request.scope["session"].uid = 100
        request.scope["session"].role = "admin"
        return "ok"

    @app.get("/me")
    async def me(request: Request):
        # Ensure it is the Pydantic model
        assert isinstance(request.scope["session"], UserSession)
        return request.scope["session"].model_dump()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Default session
        response = await client.get("/me")
        assert response.json() == {"uid": 0, "role": "guest"}

        # Login to change state
        await client.post("/login")

        # Persisted state
        response = await client.get("/me")
        assert response.json() == {"uid": 100, "role": "admin"}
