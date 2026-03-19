"""Tests for user management CRUD, bulk, and import API endpoints (Tasks 5.2-5.4)."""
import csv
import io
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_admin_users")
    from core.users.models import User
    from core.system.models import SystemConfig
    await init_beanie(database=database, document_models=[User, SystemConfig])
    yield database
    client.close()


@pytest.fixture
def app():
    from fastapi import FastAPI
    from core.users.router import router
    app = FastAPI()
    app.include_router(router)
    return app


async def _make_user(permissions_val: int, username: str = "admin", db=None):
    from core.auth.password import hash_password
    from core.auth.jwt import create_access_token
    from core.users.models import User
    user = User(
        username=username,
        hashed_password=hash_password("pw"),
        display_name=username.capitalize(),
        permissions=permissions_val,
    )
    await user.insert()
    token = create_access_token(user_id=str(user.id), permissions=permissions_val)
    return user, token


# ── GET /admin/users ────────────────────────────────────────────────────────

async def test_user_list_returns_paginated_users(db, app):
    """GET /admin/users must return a list of users with pagination metadata."""
    from core.auth.permissions import SITE_ADMIN
    _, token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/users")
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert "total" in data
    assert isinstance(data["users"], list)


async def test_user_list_requires_manage_users(db, app):
    """GET /admin/users must return 403 without MANAGE_USERS."""
    from core.auth.permissions import STUDENT
    _, token = await _make_user(int(STUDENT), username="student")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/users")
    assert resp.status_code == 403


async def test_user_list_includes_expected_fields(db, app):
    """User list entries must include id, username, display_name, permissions, tags."""
    from core.auth.permissions import SITE_ADMIN
    _, token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/users")
    assert resp.status_code == 200
    for user in resp.json()["users"]:
        assert "id" in user
        assert "username" in user
        assert "display_name" in user
        assert "permissions" in user
        assert "tags" in user


# ── GET /admin/users/{id} ────────────────────────────────────────────────────

async def test_single_user_read_returns_user(db, app):
    """GET /admin/users/{id} must return the user record."""
    from core.auth.permissions import SITE_ADMIN
    user, token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get(f"/admin/users/{user.id}")
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


async def test_single_user_read_returns_404_for_missing(db, app):
    """GET /admin/users/{id} must return 404 for non-existent user."""
    from core.auth.permissions import SITE_ADMIN
    _, token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/admin/users/000000000000000000000000")
    assert resp.status_code == 404


# ── PUT /admin/users/{id} ────────────────────────────────────────────────────

async def test_user_update_changes_display_name(db, app):
    """PUT /admin/users/{id} must update display_name."""
    from core.auth.permissions import SITE_ADMIN, STUDENT
    user, token = await _make_user(int(SITE_ADMIN))
    target, _ = await _make_user(int(STUDENT), username="target")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.put(f"/admin/users/{target.id}", json={"display_name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "New Name"


async def test_user_update_does_not_change_password_when_absent(db, app):
    """PUT /admin/users/{id} without new_password must not change hashed_password."""
    from core.auth.permissions import SITE_ADMIN, STUDENT
    from core.users.models import User
    user, token = await _make_user(int(SITE_ADMIN))
    target, _ = await _make_user(int(STUDENT), username="target")
    original_hash = target.hashed_password
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        await ac.put(f"/admin/users/{target.id}", json={"display_name": "X"})
    refreshed = await User.get(target.id)
    assert refreshed.hashed_password == original_hash


# ── DELETE /admin/users/{id} ─────────────────────────────────────────────────

async def test_user_delete_removes_user(db, app):
    """DELETE /admin/users/{id} must delete the user and return 204."""
    from core.auth.permissions import SITE_ADMIN, STUDENT
    from core.users.models import User
    user, token = await _make_user(int(SITE_ADMIN))
    target, _ = await _make_user(int(STUDENT), username="target")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.delete(f"/admin/users/{target.id}")
    assert resp.status_code == 204
    assert await User.get(target.id) is None


async def test_user_delete_self_returns_400(db, app):
    """DELETE /admin/users/{id} with own id must return 400."""
    from core.auth.permissions import SITE_ADMIN
    user, token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.delete(f"/admin/users/{user.id}")
    assert resp.status_code == 400


# ── DELETE /admin/users/bulk ─────────────────────────────────────────────────

async def test_bulk_delete_removes_multiple_users(db, app):
    """DELETE /admin/users/bulk must delete all specified users."""
    from core.auth.permissions import SITE_ADMIN, STUDENT
    from core.users.models import User
    admin, token = await _make_user(int(SITE_ADMIN))
    u1, _ = await _make_user(int(STUDENT), username="u1")
    u2, _ = await _make_user(int(STUDENT), username="u2")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.request("DELETE", "/admin/users/bulk", json={"ids": [str(u1.id), str(u2.id)]})
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 2
    assert await User.get(u1.id) is None
    assert await User.get(u2.id) is None


async def test_bulk_delete_excludes_own_id(db, app):
    """DELETE /admin/users/bulk must silently exclude the caller's own ID."""
    from core.auth.permissions import SITE_ADMIN
    from core.users.models import User
    admin, token = await _make_user(int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.request("DELETE", "/admin/users/bulk", json={"ids": [str(admin.id)]})
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 0
    assert await User.get(admin.id) is not None


# ── PATCH /admin/users/bulk ──────────────────────────────────────────────────

async def test_bulk_permissions_update(db, app):
    """PATCH /admin/users/bulk must update permissions for all specified users."""
    from core.auth.permissions import SITE_ADMIN, STUDENT, TEACHER
    from core.users.models import User
    admin, token = await _make_user(int(SITE_ADMIN))
    u1, _ = await _make_user(int(STUDENT), username="u1")
    u2, _ = await _make_user(int(STUDENT), username="u2")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.patch("/admin/users/bulk", json={"ids": [str(u1.id), str(u2.id)], "permissions": int(TEACHER)})
    assert resp.status_code == 200
    assert resp.json()["updated"] == 2
    r1 = await User.get(u1.id)
    assert r1.permissions == int(TEACHER)


# ── POST /admin/users/import ─────────────────────────────────────────────────

def _make_csv(*rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["username", "password", "display_name", "preset", "tags"])
    for row in rows:
        writer.writerow(row)
    return buf.getvalue().encode()


async def test_csv_import_creates_valid_users(db, app):
    """POST /admin/users/import must create users from valid CSV rows."""
    from core.auth.permissions import SITE_ADMIN
    from core.users.models import User
    _, token = await _make_user(int(SITE_ADMIN))
    csv_data = _make_csv(
        ["alice", "pw1", "Alice", "STUDENT", "math;science"],
        ["bob", "pw2", "Bob", "TEACHER", ""],
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.post("/admin/users/import", files={"file": ("users.csv", csv_data, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == 2
    assert data["failed"] == []
    assert await User.find_one(User.username == "alice") is not None


async def test_csv_import_skips_duplicate_username(db, app):
    """POST /admin/users/import must skip rows with existing usernames."""
    from core.auth.permissions import SITE_ADMIN
    _, token = await _make_user(int(SITE_ADMIN), username="admin")
    csv_data = _make_csv(["admin", "pw", "Admin Again", "STUDENT", ""])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.post("/admin/users/import", files={"file": ("users.csv", csv_data, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == 0
    assert len(data["failed"]) == 1
    assert "already exists" in data["failed"][0]["reason"].lower()


async def test_csv_import_skips_invalid_preset(db, app):
    """POST /admin/users/import must skip rows with unknown preset names."""
    from core.auth.permissions import SITE_ADMIN
    _, token = await _make_user(int(SITE_ADMIN))
    csv_data = _make_csv(["newuser", "pw", "New User", "SUPERADMIN", ""])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.post("/admin/users/import", files={"file": ("users.csv", csv_data, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == 0
    assert len(data["failed"]) == 1
    assert "preset" in data["failed"][0]["reason"].lower()
