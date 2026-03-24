"""Tests verifying class hub page statistics card data (Task 5.3)."""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from core.auth.jwt import create_access_token
from core.auth.password import hash_password
from core.auth.permissions import STUDENT, TEACHER


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
    db = client.get_database("test_class_hub_stats")
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

    student = User(
        username="student1",
        hashed_password=hash_password("pass123"),
        display_name="Student One",
        permissions=int(STUDENT),
    )
    await student.insert()

    cls = Class(
        name="Stats Class",
        description="",
        visibility="private",
        owner_id=str(teacher.id),
        invite_code="STAT01",
    )
    await cls.insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(teacher.id), role="teacher"
    ).insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(student.id), role="student"
    ).insert()

    app = _make_app()
    yield app, teacher, student, cls

    client.close()


def _auth_cookie(user_id: str, permissions: int) -> dict:
    token = create_access_token(user_id=user_id, permissions=permissions)
    return {"access_token": token}


async def test_class_hub_shows_member_count(db_app):
    """The class hub page should display the member count."""
    app, teacher, _, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(f"/pages/teacher/class/{cls.id}", follow_redirects=False)
    assert response.status_code == 200
    content = response.content.decode()
    # 2 members: teacher + student
    assert "成員數" in content


async def test_class_hub_shows_invite_code(db_app):
    """The class hub page should display the invite code."""
    app, teacher, _, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(f"/pages/teacher/class/{cls.id}", follow_redirects=False)
    assert response.status_code == 200
    assert b"STAT01" in response.content


async def test_class_hub_shows_pending_count(db_app):
    """The class hub page should display the pending submissions count."""
    from datetime import date, datetime, timezone
    from tasks.submissions.models import TaskSubmission

    app, teacher, student, cls = db_app

    # Create a pending submission
    await TaskSubmission(
        template_id="tmpl1",
        class_id=str(cls.id),
        student_id=str(student.id),
        date=date.today(),
        field_values={"answer": "test"},
        template_snapshot={"name": "Test Task"},
        status="pending",
        submitted_at=datetime.now(timezone.utc),
    ).insert()

    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(f"/pages/teacher/class/{cls.id}", follow_redirects=False)
    assert response.status_code == 200
    content = response.content.decode()
    assert "待審查" in content


async def test_class_hub_shows_checkin_rate(db_app):
    """The class hub page should display the today checkin rate section."""
    app, teacher, _, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(f"/pages/teacher/class/{cls.id}", follow_redirects=False)
    assert response.status_code == 200
    content = response.content.decode()
    assert "簽到率" in content


async def test_class_hub_shows_submission_review_card(db_app):
    """The class hub tool cards should include 任務審查."""
    app, teacher, _, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(f"/pages/teacher/class/{cls.id}", follow_redirects=False)
    assert response.status_code == 200
    assert "任務審查".encode() in response.content


async def test_class_hub_shows_attendance_card(db_app):
    """The class hub tool cards should include 出席紀錄."""
    app, teacher, _, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", cookies=cookies
    ) as ac:
        response = await ac.get(f"/pages/teacher/class/{cls.id}", follow_redirects=False)
    assert response.status_code == 200
    assert "出席紀錄".encode() in response.content
