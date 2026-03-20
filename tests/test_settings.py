"""Tests for settings page endpoints (Tasks 5.2, 5.3)."""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from core.auth.jwt import create_access_token
from core.auth.password import hash_password, verify_password
from core.auth.permissions import MANAGE_USERS, STUDENT


def _make_app():
    from core.auth.router import router as auth_router
    from pages.router import router as pages_router

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(pages_router)
    return app


@pytest.fixture
async def db_app():
    client = AsyncMongoMockClient()
    db = client.get_database("test_settings")
    from core.users.models import User
    from core.system.models import SystemConfig
    await init_beanie(database=db, document_models=[User, SystemConfig])

    student = User(
        username="alice",
        hashed_password=hash_password("oldpass"),
        display_name="Alice",
        permissions=int(STUDENT),
        email="alice@example.com",
    )
    await student.insert()

    admin = User(
        username="admin",
        hashed_password=hash_password("adminpass"),
        display_name="Admin",
        permissions=int(MANAGE_USERS),
    )
    await admin.insert()

    app = _make_app()
    yield app, student, admin
    client.close()


def _cookie(user_id: str, permissions: int) -> dict:
    token = create_access_token(user_id=user_id, permissions=permissions)
    return {"access_token": token}


# ── Task 5.3: Email required validation ────────────────────────────────────

async def test_create_user_without_email_is_rejected(db_app):
    """POST /pages/admin/users/new without email must fail — user not created."""
    app, _, admin = db_app
    from core.users.models import User

    cookies = _cookie(str(admin.id), int(MANAGE_USERS))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for name, val in cookies.items():
            ac.cookies.set(name, val)
        resp = await ac.post(
            "/pages/admin/users/new",
            data={
                "username": "newuser",
                "display_name": "New User",
                "password": "pass123",
                # email intentionally omitted
            },
            follow_redirects=False,
        )
    # Should redirect back with an error, not to success
    assert resp.status_code == 302
    location = resp.headers["location"]
    assert "error=" in location
    # The user must not have been created
    assert await User.find_one(User.username == "newuser") is None


async def test_create_user_with_email_succeeds(db_app):
    """POST /pages/admin/users/new with email must create the user."""
    app, _, admin = db_app
    from core.users.models import User

    cookies = _cookie(str(admin.id), int(MANAGE_USERS))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for name, val in cookies.items():
            ac.cookies.set(name, val)
        resp = await ac.post(
            "/pages/admin/users/new",
            data={
                "username": "newuser",
                "display_name": "New User",
                "password": "pass123",
                "email": "new@example.com",
            },
            follow_redirects=False,
        )
    assert resp.status_code == 302
    assert "error=" not in resp.headers.get("location", "")
    assert await User.find_one(User.username == "newuser") is not None


# ── Task 5.2: Password change endpoint ─────────────────────────────────────

async def test_password_change_with_correct_old_password(db_app):
    """POST /pages/settings/password with correct old password must update it."""
    app, student, _ = db_app
    from core.users.models import User

    cookies = _cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for name, val in cookies.items():
            ac.cookies.set(name, val)
        resp = await ac.post(
            "/pages/settings/password",
            data={"current_password": "oldpass", "new_password": "newpass123"},
            follow_redirects=False,
        )
    assert resp.status_code == 302
    location = resp.headers["location"]
    assert "error=" not in location

    refreshed = await User.get(student.id)
    assert verify_password("newpass123", refreshed.hashed_password)


async def test_password_change_with_wrong_old_password_rejected(db_app):
    """POST /pages/settings/password with wrong old password must NOT change it."""
    app, student, _ = db_app
    from core.users.models import User

    original_hash = student.hashed_password
    cookies = _cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for name, val in cookies.items():
            ac.cookies.set(name, val)
        resp = await ac.post(
            "/pages/settings/password",
            data={"current_password": "wrongpass", "new_password": "newpass123"},
            follow_redirects=False,
        )
    assert resp.status_code == 302
    assert "error=" in resp.headers["location"]

    refreshed = await User.get(student.id)
    assert refreshed.hashed_password == original_hash
