"""Tests for bug-fixes change.

Covers:
- Sidebar hides "建立第一個班級" for users with can_manage_all_classes (tasks 1.2, 1.3, 4.1)
- Student dashboard class card displays owner display name (tasks 3.3, 4.2)
"""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from core.auth.jwt import create_access_token
from core.auth.permissions import CLASS_MANAGER, STUDENT, TEACHER


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _token(user_id: str, permissions: int) -> str:
    return create_access_token(user_id=user_id, permissions=permissions)


def _cookies(user_id: str, permissions: int) -> dict:
    return {"access_token": _token(user_id, permissions)}


@pytest.fixture(autouse=True)
def register_auth_provider():
    from core.auth.local_provider import LocalAuthProvider
    from extensions.protocols import AuthProvider
    from extensions.registry import TestRegistry
    with TestRegistry() as reg:
        reg.register(AuthProvider, "local", LocalAuthProvider())
        yield


async def _make_full_db(db_name: str):
    from core.classes.models import Class, ClassMembership
    from core.users.models import User
    from gamification.badges.models import BadgeAward, BadgeDefinition
    from gamification.points.models import ClassPointConfig, PointTransaction
    from tasks.checkin.models import CheckinConfig, CheckinRecord, DailyCheckinOverride
    from tasks.submissions.models import TaskSubmission
    from tasks.templates.models import TaskAssignment, TaskScheduleRule, TaskTemplate

    client = AsyncMongoMockClient()
    db = client.get_database(db_name)
    await init_beanie(
        database=db,
        document_models=[
            User, Class, ClassMembership,
            TaskTemplate, TaskAssignment, TaskScheduleRule, TaskSubmission,
            CheckinConfig, DailyCheckinOverride, CheckinRecord,
            PointTransaction, ClassPointConfig,
            BadgeDefinition, BadgeAward,
        ],
    )
    return client


def _make_app():
    from community.feed.router import router as feed_router
    from core.auth.router import router as auth_router
    from gamification.badges.router import router as badges_router
    from gamification.leaderboard.router import router as leaderboard_router
    from gamification.points.router import router as points_router
    from pages.router import router as pages_router
    from tasks.checkin.router import router as checkin_router
    from tasks.submissions.router import router as submissions_router
    from tasks.templates.router import router as templates_router

    app = FastAPI()
    for r in [auth_router, pages_router, submissions_router,
              badges_router, leaderboard_router, points_router,
              feed_router, checkin_router, templates_router]:
        app.include_router(r)
    return app


# ─── Tasks 1.2, 1.3, 4.1 — Sidebar "建立第一個班級" condition ─────────────────

@pytest.fixture
async def sidebar_app():
    """App with a CLASS_MANAGER user (no memberships) and a plain TEACHER user (no memberships)."""
    client = await _make_full_db("test_sidebar_condition")
    from core.users.models import User

    class_manager = User(
        username="mgr",
        hashed_password="x",
        display_name="Manager",
        permissions=int(CLASS_MANAGER),
    )
    await class_manager.insert()

    teacher = User(
        username="teacher",
        hashed_password="x",
        display_name="Teacher",
        permissions=int(TEACHER),
    )
    await teacher.insert()

    yield _make_app(), class_manager, teacher
    client.close()


async def test_sidebar_hides_create_class_for_class_manager(sidebar_app):
    """CLASS_MANAGER with no class memberships must NOT see '建立第一個班級' in sidebar.

    Scenario: System admin sees no create-class shortcut (task 1.2).
    """
    app, class_manager, _ = sidebar_app
    cookies = _cookies(str(class_manager.id), int(CLASS_MANAGER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test",
                           cookies=cookies) as ac:
        resp = await ac.get("/pages/dashboard", follow_redirects=False)
    assert resp.status_code == 200
    assert "建立第一個班級".encode() not in resp.content, (
        "CLASS_MANAGER should NOT see '建立第一個班級' — they manage classes via admin tools"
    )


async def test_sidebar_shows_create_class_for_teacher_with_no_classes(sidebar_app):
    """Regular TEACHER with no class memberships MUST see '建立第一個班級' in sidebar.

    Scenario: Teacher with no classes still sees create-class shortcut (task 1.3).
    """
    app, _, teacher = sidebar_app
    cookies = _cookies(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test",
                           cookies=cookies) as ac:
        resp = await ac.get("/pages/dashboard", follow_redirects=False)
    assert resp.status_code == 200
    assert "建立第一個班級".encode() in resp.content, (
        "Regular TEACHER with no classes should see '建立第一個班級' shortcut"
    )


# ─── Tasks 3.3, 4.2 — Student dashboard owner_display_name ──────────────────

@pytest.fixture
async def owner_name_app():
    """App with a teacher-owned class and an enrolled student."""
    client = await _make_full_db("test_owner_display_name")
    from core.classes.models import Class, ClassMembership
    from core.users.models import User

    teacher = User(
        username="owner_teacher",
        hashed_password="x",
        display_name="Ms. Chen",
        permissions=int(TEACHER),
    )
    await teacher.insert()

    student = User(
        username="enrolled_student",
        hashed_password="x",
        display_name="Student A",
        permissions=int(STUDENT),
    )
    await student.insert()

    cls = Class(
        name="Math 101",
        description="",
        visibility="private",
        owner_id=str(teacher.id),
        invite_code="OWN001",
    )
    await cls.insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(student.id), role="student"
    ).insert()

    yield _make_app(), student, teacher, cls
    client.close()


async def test_dashboard_class_card_shows_owner_display_name(owner_name_app):
    """Student dashboard class card must display owner's display_name.

    Scenario: Class card shows teacher display name (task 3.2).
    """
    app, student, teacher, _ = owner_name_app
    cookies = _cookies(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test",
                           cookies=cookies) as ac:
        resp = await ac.get("/pages/dashboard", follow_redirects=False)
    assert resp.status_code == 200
    assert teacher.display_name.encode() in resp.content, (
        f"Dashboard class card should display teacher name '{teacher.display_name}'"
    )


@pytest.fixture
async def missing_owner_app():
    """App with a class whose owner_id references a non-existent user."""
    client = await _make_full_db("test_missing_owner")
    from core.classes.models import Class, ClassMembership
    from core.users.models import User

    student = User(
        username="orphan_student",
        hashed_password="x",
        display_name="Orphan Student",
        permissions=int(STUDENT),
    )
    await student.insert()

    cls = Class(
        name="Orphan Class",
        description="",
        visibility="private",
        owner_id="000000000000000000000000",  # non-existent
        invite_code="ORP001",
    )
    await cls.insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(student.id), role="student"
    ).insert()

    yield _make_app(), student, cls
    client.close()


async def test_dashboard_class_card_owner_not_found_shows_empty_string(missing_owner_app):
    """When class owner does not exist, dashboard must render 200 with empty teacher name.

    Scenario: Teacher name fallback when owner not found (task 3.3).
    """
    app, student, _ = missing_owner_app
    cookies = _cookies(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test",
                           cookies=cookies) as ac:
        resp = await ac.get("/pages/dashboard", follow_redirects=False)
    assert resp.status_code == 200, (
        f"Dashboard must not raise when owner is missing, got {resp.status_code}"
    )
    assert b"Orphan Class" in resp.content, "Class name must still appear"
