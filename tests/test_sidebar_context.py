"""Tests verifying all teacher pages include sidebar context variables (Task 5.2)."""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from core.auth.jwt import create_access_token
from core.auth.password import hash_password
from core.auth.permissions import TEACHER


def _make_app():
    from core.auth.router import router as auth_router
    from gamification.badges.router import router as badges_router
    from gamification.leaderboard.router import router as leaderboard_router
    from gamification.points.router import router as points_router
    from pages.router import router as pages_router
    from tasks.checkin.router import router as checkin_router
    from tasks.submissions.router import router as submissions_router
    from tasks.templates.router import router as templates_router

    app = FastAPI()
    for r in [
        auth_router, pages_router, submissions_router,
        badges_router, leaderboard_router, points_router,
        checkin_router, templates_router,
    ]:
        app.include_router(r)
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
    from core.classes.models import Class, ClassMembership
    from core.users.models import User
    from gamification.badges.models import BadgeAward, BadgeDefinition
    from gamification.points.models import ClassPointConfig, PointTransaction
    from tasks.checkin.models import AttendanceCorrection, CheckinConfig, CheckinRecord, DailyCheckinOverride
    from tasks.submissions.models import TaskSubmission
    from tasks.templates.models import TaskAssignment, TaskScheduleRule, TaskTemplate

    client = AsyncMongoMockClient()
    db = client.get_database("test_sidebar_context")
    await init_beanie(
        database=db,
        document_models=[
            User, Class, ClassMembership,
            TaskTemplate, TaskAssignment, TaskScheduleRule, TaskSubmission,
            CheckinConfig, DailyCheckinOverride, CheckinRecord,
            AttendanceCorrection,
            PointTransaction, ClassPointConfig,
            BadgeDefinition, BadgeAward,
        ],
    )

    teacher = User(
        username="teacher1",
        hashed_password=hash_password("pass123"),
        display_name="Teacher One",
        permissions=int(TEACHER),
    )
    await teacher.insert()

    cls = Class(
        name="Test Class",
        description="A test class",
        visibility="private",
        owner_id=str(teacher.id),
        invite_code="TEST01",
    )
    await cls.insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(teacher.id), role="teacher"
    ).insert()

    app = _make_app()
    yield app, teacher, cls

    client.close()


def _auth_cookie(user_id: str, permissions: int) -> dict:
    token = create_access_token(user_id=user_id, permissions=permissions)
    return {"access_token": token}


# Sidebar context marker: the sidebar renders "班級管理" section label
# only when page context variables are correctly injected
_SIDEBAR_MARKER = "班級管理".encode()


async def _get_page(app, teacher, url: str) -> bytes:
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(url, follow_redirects=False)
    assert response.status_code == 200, f"Expected 200 for {url}, got {response.status_code}"
    return response.content


async def test_class_hub_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/teacher/class/{cls.id}")
    assert _SIDEBAR_MARKER in content
    assert "Test Class".encode() in content


async def test_class_members_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/teacher/classes/{cls.id}/members")
    assert _SIDEBAR_MARKER in content


async def test_templates_list_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/teacher/classes/{cls.id}/templates")
    assert _SIDEBAR_MARKER in content


async def test_submission_review_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/teacher/class/{cls.id}/submissions")
    assert _SIDEBAR_MARKER in content


async def test_checkin_config_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/teacher/classes/{cls.id}/checkin-config")
    assert _SIDEBAR_MARKER in content


async def test_attendance_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/teacher/classes/{cls.id}/attendance")
    assert _SIDEBAR_MARKER in content


async def test_points_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/classes/{cls.id}/points")
    assert _SIDEBAR_MARKER in content


async def test_leaderboard_includes_sidebar_context(db_app):
    app, teacher, cls = db_app
    content = await _get_page(app, teacher, f"/pages/classes/{cls.id}/leaderboard")
    assert _SIDEBAR_MARKER in content
