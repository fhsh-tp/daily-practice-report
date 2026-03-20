"""Tests for checkin config page (task 5.6)."""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from core.auth.jwt import create_access_token
from core.auth.password import hash_password
from core.auth.permissions import TEACHER


@pytest.fixture(autouse=True)
def register_auth_provider():
    from core.auth.local_provider import LocalAuthProvider
    from extensions.protocols import AuthProvider
    from extensions.registry import TestRegistry
    with TestRegistry() as reg:
        reg.register(AuthProvider, "local", LocalAuthProvider())
        yield


@pytest.fixture
async def checkin_config_app():
    from core.classes.models import Class, ClassMembership
    from core.users.models import User
    from gamification.badges.models import BadgeAward, BadgeDefinition
    from gamification.points.models import ClassPointConfig, PointTransaction
    from tasks.checkin.models import CheckinConfig, DailyCheckinOverride, CheckinRecord
    from tasks.templates.models import TaskAssignment, TaskScheduleRule, TaskTemplate
    from tasks.submissions.models import TaskSubmission

    client = AsyncMongoMockClient()
    db = client.get_database("test_checkin_config")
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

    teacher = User(
        username="teacher_cc",
        hashed_password=hash_password("pw"),
        display_name="Teacher CC",
        permissions=int(TEACHER),
    )
    await teacher.insert()

    cls = Class(
        name="Config Class",
        description="",
        visibility="private",
        owner_id=str(teacher.id),
        invite_code="CFG001",
    )
    await cls.insert()
    await ClassMembership(class_id=str(cls.id), user_id=str(teacher.id), role="teacher").insert()

    from core.auth.router import router as auth_router
    from gamification.badges.router import router as badges_router
    from pages.router import router as pages_router
    from tasks.checkin.router import router as checkin_router
    from tasks.submissions.router import router as submissions_router
    from tasks.templates.router import router as templates_router

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(pages_router)
    app.include_router(badges_router)
    app.include_router(checkin_router)
    app.include_router(submissions_router)
    app.include_router(templates_router)

    yield app, teacher, cls

    client.close()


def _auth_cookie(user_id: str, permissions: int) -> dict:
    token = create_access_token(user_id=user_id, permissions=permissions)
    return {"access_token": token}


async def test_checkin_config_page_returns_200(checkin_config_app):
    """GET checkin-config page returns HTTP 200 for authenticated teacher."""
    app, teacher, cls = checkin_config_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get(
            f"/pages/teacher/classes/{cls.id}/checkin-config",
            follow_redirects=False,
        )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


async def test_checkin_config_page_shows_defaults_when_no_config(checkin_config_app):
    """When no CheckinConfig exists, page renders with defaults (all weekdays shown)."""
    app, teacher, cls = checkin_config_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get(
            f"/pages/teacher/classes/{cls.id}/checkin-config",
            follow_redirects=False,
        )
    assert response.status_code == 200
    # When no config, all 7 weekday checkboxes should be checked
    content = response.content.decode()
    assert content.count('checked') >= 7
