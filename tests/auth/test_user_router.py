"""Tests for user router schema changes (permissions/tags, MANAGE_USERS guard)."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_user_router")
    from core.users.models import User
    await init_beanie(database=database, document_models=[User])
    yield database
    client.close()


@pytest.fixture
def app():
    from fastapi import FastAPI
    from core.users.router import router
    app = FastAPI()
    app.include_router(router)
    return app


async def test_create_user_request_accepts_permissions_field(db):
    """CreateUserRequest must accept a permissions int field."""
    from core.users.router import CreateUserRequest
    from core.auth.permissions import STUDENT
    req = CreateUserRequest(
        username="alice",
        password="pw123",
        display_name="Alice",
        permissions=int(STUDENT),
    )
    assert req.permissions == int(STUDENT)


async def test_create_user_request_has_no_role_field(db):
    """CreateUserRequest must not accept a role field."""
    import pydantic
    from core.users.router import CreateUserRequest
    # role field should be rejected or ignored (not exist in model)
    req = CreateUserRequest(username="x", password="pw", display_name="X")
    assert not hasattr(req, "role") or req.model_fields.get("role") is None


async def test_create_user_request_default_permissions_is_student(db):
    """CreateUserRequest should default permissions to STUDENT preset."""
    from core.users.router import CreateUserRequest
    from core.auth.permissions import STUDENT
    req = CreateUserRequest(username="bob", password="pw", display_name="Bob")
    assert req.permissions == int(STUDENT)
