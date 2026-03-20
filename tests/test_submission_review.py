"""Tests for submission-review-and-history capability."""
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
    for r in [auth_router, pages_router, submissions_router,
              badges_router, leaderboard_router, points_router,
              checkin_router, templates_router]:
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
    from tasks.checkin.models import CheckinConfig, CheckinRecord, DailyCheckinOverride
    from tasks.templates.models import TaskAssignment, TaskScheduleRule, TaskTemplate
    from tasks.submissions.models import TaskSubmission

    client = AsyncMongoMockClient()
    db = client.get_database("test_review")
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

    student = User(
        username="alice", hashed_password=hash_password("pass123"),
        display_name="Alice", permissions=int(STUDENT),
    )
    await student.insert()

    teacher = User(
        username="bob", hashed_password=hash_password("teachpass"),
        display_name="Bob", permissions=int(TEACHER),
    )
    await teacher.insert()

    cls = Class(
        name="Test Class", description="", visibility="private",
        owner_id=str(teacher.id), invite_code="REVIEW01",
    )
    await cls.insert()
    await ClassMembership(class_id=str(cls.id), user_id=str(student.id), role="student").insert()
    await ClassMembership(class_id=str(cls.id), user_id=str(teacher.id), role="teacher").insert()

    app = _make_app()
    yield app, student, teacher, cls

    client.close()


def _auth_cookie(user_id: str, permissions: int) -> dict:
    token = create_access_token(user_id=user_id, permissions=permissions)
    return {"access_token": token}


# ---------------------------------------------------------------------------
# POST /api/points/deduct — teacher deduct
# ---------------------------------------------------------------------------

async def test_teacher_can_deduct_points(db_app):
    """Teacher can deduct points from a student via API (task 2.1)."""
    from gamification.points.service import award_points, get_balance

    app, student, teacher, cls = db_app
    await award_points(str(student.id), str(cls.id), 50, "submission", "evt1")

    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.post(
            "/api/points/deduct",
            json={"student_id": str(student.id), "class_id": str(cls.id), "amount": 10, "reason": "誤用積分"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["deducted"] == 10
    assert data["new_balance"] == 40


async def test_deduct_requires_reason(db_app):
    """POST /api/points/deduct returns 422 when reason is missing (task 2.2)."""
    app, student, teacher, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.post(
            "/api/points/deduct",
            json={"student_id": str(student.id), "class_id": str(cls.id), "amount": 5},
        )
    assert response.status_code == 422


async def test_deduct_requires_teacher_permission(db_app):
    """Student cannot call POST /api/points/deduct (403)."""
    app, student, teacher, cls = db_app
    cookies = _auth_cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.post(
            "/api/points/deduct",
            json={"student_id": str(student.id), "class_id": str(cls.id), "amount": 5, "reason": "test"},
        )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/submissions/<submission_id>/comment — teacher comment
# ---------------------------------------------------------------------------

async def test_teacher_can_leave_comment(db_app):
    """Teacher can leave a comment on a submission (task 3.1)."""
    from tasks.submissions.models import TaskSubmission
    from datetime import date

    app, student, teacher, cls = db_app
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"name": "Daily Log"},
        field_values={"note": "hello"},
        student_id=str(student.id),
        class_id=str(cls.id),
        date=date(2026, 3, 18),
    )
    await sub.insert()

    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.post(
            f"/api/submissions/{sub.id}/comment",
            json={"comment": "很好！"},
        )
    assert response.status_code == 200

    await sub.sync()
    assert sub.teacher_comment == "很好！"
    assert sub.reviewed_at is not None


async def test_comment_can_be_overwritten(db_app):
    """Teacher can overwrite an existing comment (task 3.2)."""
    from tasks.submissions.models import TaskSubmission
    from datetime import date

    app, student, teacher, cls = db_app
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"name": "Daily Log"},
        field_values={"note": "hello"},
        student_id=str(student.id),
        class_id=str(cls.id),
        date=date(2026, 3, 19),
        teacher_comment="舊評語",
    )
    await sub.insert()

    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.post(
            f"/api/submissions/{sub.id}/comment",
            json={"comment": "新評語"},
        )
    assert response.status_code == 200

    await sub.sync()
    assert sub.teacher_comment == "新評語"


async def test_comment_unauthorized_access_rejected(db_app):
    """Student cannot leave a comment (403) (task 3.3)."""
    from tasks.submissions.models import TaskSubmission
    from datetime import date

    app, student, teacher, cls = db_app
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"name": "Daily Log"},
        field_values={"note": "hello"},
        student_id=str(student.id),
        class_id=str(cls.id),
        date=date(2026, 3, 20),
    )
    await sub.insert()

    cookies = _auth_cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.post(
            f"/api/submissions/{sub.id}/comment",
            json={"comment": "不應該可以"},
        )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /pages/teacher/class/<class_id>/submissions — review page
# ---------------------------------------------------------------------------

async def test_teacher_can_view_submission_review_page(db_app):
    """Teacher can access submission review page (task 4.1)."""
    app, student, teacher, cls = db_app
    cookies = _auth_cookie(str(teacher.id), int(TEACHER))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get(
            f"/pages/teacher/class/{cls.id}/submissions", follow_redirects=False
        )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


async def test_student_cannot_access_review_page(db_app):
    """Student cannot access teacher review page (403 or redirect) (task 4.1)."""
    app, student, teacher, cls = db_app
    cookies = _auth_cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get(
            f"/pages/teacher/class/{cls.id}/submissions", follow_redirects=False
        )
    assert response.status_code in (403, 302)


# ---------------------------------------------------------------------------
# GET /pages/student/history — learning history page
# ---------------------------------------------------------------------------

async def test_student_can_view_learning_history(db_app):
    """Student can access their learning history page (task 5.1)."""
    app, student, teacher, cls = db_app
    cookies = _auth_cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get("/pages/student/history", follow_redirects=False)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


async def test_history_page_shows_submissions(db_app):
    """History page shows all student submissions (task 5.1)."""
    from tasks.submissions.models import TaskSubmission
    from datetime import date

    app, student, teacher, cls = db_app
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"name": "Weekly Review"},
        field_values={"note": "week1"},
        student_id=str(student.id),
        class_id=str(cls.id),
        date=date(2026, 3, 18),
    )
    await sub.insert()

    cookies = _auth_cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get("/pages/student/history", follow_redirects=False)
    assert response.status_code == 200
    assert "Weekly Review".encode() in response.content


async def test_history_page_shows_teacher_comment(db_app):
    """History page shows teacher_comment when present (task 5.4)."""
    from tasks.submissions.models import TaskSubmission
    from datetime import date, datetime, timezone

    app, student, teacher, cls = db_app
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"name": "Daily Log"},
        field_values={"note": "hi"},
        student_id=str(student.id),
        class_id=str(cls.id),
        date=date(2026, 3, 17),
        teacher_comment="做得很好！",
        reviewed_at=datetime.now(timezone.utc),
    )
    await sub.insert()

    cookies = _auth_cookie(str(student.id), int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get("/pages/student/history", follow_redirects=False)
    assert response.status_code == 200
    assert "做得很好！".encode() in response.content
