"""Tests that cross-class template operations are rejected.

Teacher B must not be able to create / update / delete templates belonging
to a class they are not a member of, while Teacher A (the owner) can.
"""
import pytest
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from core.auth.jwt import create_access_token
from core.auth.password import hash_password
from core.auth.permissions import TEACHER


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app() -> FastAPI:
    """Build a minimal FastAPI app with all required routers."""
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


def _auth_cookie(user_id: str, permissions: int) -> dict:
    token = create_access_token(user_id=user_id, permissions=permissions)
    return {"access_token": token}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def register_auth_provider():
    from core.auth.local_provider import LocalAuthProvider
    from extensions.protocols import AuthProvider
    from extensions.registry import TestRegistry

    with TestRegistry() as reg:
        reg.register(AuthProvider, "local", LocalAuthProvider())
        yield


@pytest.fixture
async def setup():
    """Create two teachers, two classes, memberships, and a template in class Alpha."""
    from core.classes.models import Class, ClassMembership
    from core.users.models import User
    from gamification.badges.models import BadgeAward, BadgeDefinition
    from gamification.points.models import ClassPointConfig, PointTransaction
    from tasks.checkin.models import CheckinConfig, CheckinRecord, DailyCheckinOverride
    from tasks.submissions.models import TaskSubmission
    from tasks.templates.models import TaskAssignment, TaskScheduleRule, TaskTemplate

    client = AsyncMongoMockClient()
    db = client.get_database("test_cross_class_templates")
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

    # Teacher A -- owns class Alpha
    teacher_a = User(
        username="teacher_a",
        hashed_password=hash_password("pass"),
        display_name="Teacher A",
        permissions=int(TEACHER),
    )
    await teacher_a.insert()

    # Teacher B -- owns class Beta
    teacher_b = User(
        username="teacher_b",
        hashed_password=hash_password("pass"),
        display_name="Teacher B",
        permissions=int(TEACHER),
    )
    await teacher_b.insert()

    # Class Alpha
    class_alpha = Class(
        name="Alpha",
        description="Class Alpha",
        visibility="private",
        owner_id=str(teacher_a.id),
        invite_code="ALPHA01",
    )
    await class_alpha.insert()

    # Class Beta
    class_beta = Class(
        name="Beta",
        description="Class Beta",
        visibility="private",
        owner_id=str(teacher_b.id),
        invite_code="BETA01",
    )
    await class_beta.insert()

    # Memberships
    await ClassMembership(
        class_id=str(class_alpha.id),
        user_id=str(teacher_a.id),
        role="teacher",
    ).insert()

    await ClassMembership(
        class_id=str(class_beta.id),
        user_id=str(teacher_b.id),
        role="teacher",
    ).insert()

    # Template belonging to class Alpha
    template = TaskTemplate(
        name="Alpha Homework",
        description="Homework for Alpha",
        class_id=str(class_alpha.id),
        owner_id=str(teacher_a.id),
        fields=[{"name": "answer", "field_type": "text", "required": True}],
    )
    await template.insert()

    app = _make_app()

    yield {
        "app": app,
        "teacher_a": teacher_a,
        "teacher_b": teacher_b,
        "class_alpha": class_alpha,
        "class_beta": class_beta,
        "template": template,
    }

    client.close()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_teacher_cannot_update_template_in_another_class(setup):
    """Teacher B tries to PATCH a template in class Alpha -> 403."""
    ctx = setup
    cookies = _auth_cookie(str(ctx["teacher_b"].id), int(TEACHER))
    template_id = str(ctx["template"].id)

    async with AsyncClient(
        transport=ASGITransport(app=ctx["app"]),
        base_url="http://test",
        cookies=cookies,
    ) as ac:
        response = await ac.patch(
            f"/templates/{template_id}",
            json={"name": "Hacked Name"},
        )

    assert response.status_code == 403


async def test_teacher_cannot_delete_template_in_another_class(setup):
    """Teacher B tries to DELETE a template in class Alpha -> 403."""
    ctx = setup
    cookies = _auth_cookie(str(ctx["teacher_b"].id), int(TEACHER))
    template_id = str(ctx["template"].id)

    async with AsyncClient(
        transport=ASGITransport(app=ctx["app"]),
        base_url="http://test",
        cookies=cookies,
    ) as ac:
        response = await ac.delete(f"/templates/{template_id}")

    assert response.status_code == 403


async def test_teacher_cannot_create_template_in_another_class(setup):
    """Teacher B tries to POST a new template in class Alpha -> 403."""
    ctx = setup
    cookies = _auth_cookie(str(ctx["teacher_b"].id), int(TEACHER))
    alpha_id = str(ctx["class_alpha"].id)

    async with AsyncClient(
        transport=ASGITransport(app=ctx["app"]),
        base_url="http://test",
        cookies=cookies,
    ) as ac:
        response = await ac.post(
            f"/classes/{alpha_id}/templates",
            json={
                "name": "Sneaky Template",
                "description": "Should be rejected",
                "fields": [{"name": "q1", "field_type": "text", "required": False}],
            },
        )

    assert response.status_code == 403


async def test_owner_teacher_can_update_own_template(setup):
    """Teacher A can PATCH their own template in class Alpha -> 200."""
    ctx = setup
    cookies = _auth_cookie(str(ctx["teacher_a"].id), int(TEACHER))
    template_id = str(ctx["template"].id)

    async with AsyncClient(
        transport=ASGITransport(app=ctx["app"]),
        base_url="http://test",
        cookies=cookies,
    ) as ac:
        response = await ac.patch(
            f"/templates/{template_id}",
            json={"name": "Updated Alpha Homework"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Alpha Homework"
