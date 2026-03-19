"""Tests for permission schema and preset API endpoints (Task 5.1)."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_admin_perms")
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


async def _make_user(permissions_val: int, username: str = "admin"):
    from core.auth.password import hash_password
    from core.auth.jwt import create_access_token
    from core.users.models import User
    user = User(
        username=username,
        hashed_password=hash_password("pw"),
        display_name=username,
        permissions=permissions_val,
    )
    await user.insert()
    token = create_access_token(user_id=str(user.id), permissions=permissions_val)
    return token


async def test_permission_schema_endpoint_returns_five_domains(db, app):
    """GET /admin/permissions/schema must return 5 domain entries."""
    from core.auth.permissions import SITE_ADMIN
    token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/permissions/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    domains = {entry["domain"] for entry in data}
    assert domains == {"Self", "Class", "Task", "User", "System"}


async def test_permission_schema_endpoint_has_read_write_fields(db, app):
    """Each schema entry must have domain (str), read (int), write (int)."""
    from core.auth.permissions import SITE_ADMIN
    token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/permissions/schema")
    for entry in resp.json():
        assert isinstance(entry["domain"], str)
        assert isinstance(entry["read"], int)
        assert isinstance(entry["write"], int)


async def test_permission_schema_endpoint_requires_manage_users(db, app):
    """GET /admin/permissions/schema must return 403 without MANAGE_USERS."""
    from core.auth.permissions import STUDENT
    token = await _make_user(int(STUDENT), username="student")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/permissions/schema")
    assert resp.status_code == 403


async def test_permission_presets_endpoint_returns_all_presets(db, app):
    """GET /admin/permissions/presets must return at least the 5 named presets."""
    from core.auth.permissions import SITE_ADMIN
    token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/permissions/presets")
    assert resp.status_code == 200
    data = resp.json()
    names = {entry["name"] for entry in data}
    assert {"STUDENT", "TEACHER", "USER_ADMIN", "SYS_ADMIN", "SITE_ADMIN"} <= names


async def test_permission_presets_endpoint_has_name_and_value(db, app):
    """Each preset entry must have name (str) and value (int)."""
    from core.auth.permissions import SITE_ADMIN
    token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/permissions/presets")
    for entry in resp.json():
        assert isinstance(entry["name"], str)
        assert isinstance(entry["value"], int)


async def test_permission_presets_endpoint_requires_manage_users(db, app):
    """GET /admin/permissions/presets must return 403 without MANAGE_USERS."""
    from core.auth.permissions import STUDENT
    token = await _make_user(int(STUDENT), username="student")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/permissions/presets")
    assert resp.status_code == 403
