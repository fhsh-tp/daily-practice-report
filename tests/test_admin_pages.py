"""Tests for admin page routes — auth guards and rendering (Task 5.6)."""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient
from unittest.mock import MagicMock


def _make_app():
    from core.auth.router import router as auth_router
    from core.users.router import router as users_router
    from pages.router import router as pages_router
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(pages_router)
    app.include_router(users_router)
    return app


@pytest.fixture(autouse=True)
def register_auth_provider():
    from core.auth.local_provider import LocalAuthProvider
    from extensions.protocols import AuthProvider
    from extensions.registry import TestRegistry
    with TestRegistry() as reg:
        reg.register(AuthProvider, "local", LocalAuthProvider())
        yield


@pytest.fixture
async def db_app():
    from core.users.models import User
    from core.system.models import SystemConfig
    from core.classes.models import Class, ClassMembership
    from tasks.checkin.models import CheckinConfig, CheckinRecord, DailyCheckinOverride
    from tasks.templates.models import TaskAssignment, TaskTemplate
    from tasks.submissions.models import TaskSubmission

    client = AsyncMongoMockClient()
    db = client.get_database("test_admin_pages")
    await init_beanie(
        database=db,
        document_models=[
            User, SystemConfig, Class, ClassMembership,
            TaskTemplate, TaskAssignment, TaskSubmission,
            CheckinConfig, DailyCheckinOverride, CheckinRecord,
        ],
    )

    from core.auth.permissions import SITE_ADMIN, STUDENT
    from core.auth.password import hash_password

    admin = User(
        username="admin",
        hashed_password=hash_password("pw"),
        display_name="Admin",
        permissions=int(SITE_ADMIN),
    )
    await admin.insert()

    student = User(
        username="student",
        hashed_password=hash_password("pw"),
        display_name="Student",
        permissions=int(STUDENT),
    )
    await student.insert()

    app = _make_app()
    # Simulate configured system
    config = MagicMock()
    config.site_name = "Test Site"
    app.state.system_config = config

    yield app, admin, student
    client.close()


async def _login(ac, username, password="pw"):
    resp = await ac.post(
        "/pages/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    return resp


# ── Access control ────────────────────────────────────────────────────────────

async def test_admin_overview_returns_200_for_site_admin(db_app):
    """GET /pages/admin/ must return 200 for SITE_ADMIN user."""
    app, admin, _ = db_app
    from core.auth.jwt import create_access_token
    from core.auth.permissions import SITE_ADMIN
    token = create_access_token(user_id=str(admin.id), permissions=int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/pages/admin/")
    assert resp.status_code == 200


async def test_admin_overview_returns_302_for_unauthenticated(db_app):
    """GET /pages/admin/ must redirect to login for unauthenticated requests."""
    app, _, _ = db_app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as ac:
        resp = await ac.get("/pages/admin/")
    assert resp.status_code == 302
    assert "/pages/login" in resp.headers["location"]


async def test_admin_overview_returns_403_for_student(db_app):
    """GET /pages/admin/ must return 403 for users without admin permissions."""
    app, _, student = db_app
    from core.auth.jwt import create_access_token
    from core.auth.permissions import STUDENT
    token = create_access_token(user_id=str(student.id), permissions=int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/pages/admin/")
    assert resp.status_code == 403


async def test_admin_users_list_returns_200_for_admin(db_app):
    """GET /pages/admin/users/ must return 200 for admin with MANAGE_USERS."""
    app, admin, _ = db_app
    from core.auth.jwt import create_access_token
    from core.auth.permissions import SITE_ADMIN
    token = create_access_token(user_id=str(admin.id), permissions=int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/pages/admin/users/")
    assert resp.status_code == 200


async def test_admin_users_new_returns_200_for_admin(db_app):
    """GET /pages/admin/users/new must return 200 for admin."""
    app, admin, _ = db_app
    from core.auth.jwt import create_access_token
    from core.auth.permissions import SITE_ADMIN
    token = create_access_token(user_id=str(admin.id), permissions=int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/pages/admin/users/new")
    assert resp.status_code == 200


async def test_admin_users_edit_returns_200_for_admin(db_app):
    """GET /pages/admin/users/{id}/edit must return 200 for admin."""
    app, admin, student = db_app
    from core.auth.jwt import create_access_token
    from core.auth.permissions import SITE_ADMIN
    token = create_access_token(user_id=str(admin.id), permissions=int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get(f"/pages/admin/users/{student.id}/edit")
    assert resp.status_code == 200


async def test_admin_system_page_returns_200_for_sys_admin(db_app):
    """GET /pages/admin/system/ must return 200 for WRITE_SYSTEM user."""
    app, admin, _ = db_app
    from core.auth.jwt import create_access_token
    from core.auth.permissions import SITE_ADMIN
    token = create_access_token(user_id=str(admin.id), permissions=int(SITE_ADMIN))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/pages/admin/system/")
    assert resp.status_code == 200
