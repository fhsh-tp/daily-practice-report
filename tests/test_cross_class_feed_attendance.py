"""Cross-class isolation tests: feed post deletion and attendance correction."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


def _token(user_id: str, permissions: int) -> str:
    from core.auth.jwt import create_access_token
    return create_access_token(user_id=user_id, permissions=permissions)


@pytest.fixture
async def app():
    """Two teachers (A → Alpha, B → Beta), one student in Alpha with a FeedPost."""
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from core.auth.password import hash_password
    from core.auth.permissions import TEACHER, STUDENT
    from community.feed.models import FeedPost, Reaction
    from tasks.checkin.models import CheckinRecord, AttendanceCorrection, CheckinConfig, DailyCheckinOverride

    client = AsyncMongoMockClient()
    db = client.get_database("test_cross_class")
    await init_beanie(
        database=db,
        document_models=[
            User, Class, ClassMembership,
            FeedPost, Reaction,
            CheckinRecord, AttendanceCorrection, CheckinConfig, DailyCheckinOverride,
        ],
    )

    # Teacher A — manages class Alpha
    teacher_a = User(
        username="teacher_a",
        hashed_password=hash_password("pw"),
        display_name="Teacher A",
        permissions=int(TEACHER),
    )
    await teacher_a.insert()

    # Teacher B — manages class Beta
    teacher_b = User(
        username="teacher_b",
        hashed_password=hash_password("pw"),
        display_name="Teacher B",
        permissions=int(TEACHER),
    )
    await teacher_b.insert()

    # Student in class Alpha (post owner)
    student = User(
        username="stu_alpha",
        hashed_password=hash_password("pw"),
        display_name="Student Alpha",
        permissions=int(STUDENT),
    )
    await student.insert()

    # Class Alpha (owned by Teacher A)
    alpha = Class(
        name="Alpha",
        visibility="private",
        owner_id=str(teacher_a.id),
        invite_code="ALPHA001",
    )
    await alpha.insert()
    await ClassMembership(class_id=str(alpha.id), user_id=str(teacher_a.id), role="teacher").insert()
    await ClassMembership(class_id=str(alpha.id), user_id=str(student.id), role="student").insert()

    # Class Beta (owned by Teacher B)
    beta = Class(
        name="Beta",
        visibility="private",
        owner_id=str(teacher_b.id),
        invite_code="BETA0001",
    )
    await beta.insert()
    await ClassMembership(class_id=str(beta.id), user_id=str(teacher_b.id), role="teacher").insert()

    # A FeedPost in class Alpha created by the student
    post = FeedPost(
        submission_id="sub_dummy",
        student_id=str(student.id),
        class_id=str(alpha.id),
        event_type="submission",
    )
    await post.insert()

    from fastapi import FastAPI
    from community.feed.router import router as feed_router
    from tasks.checkin.router import router as checkin_router

    fastapi_app = FastAPI()
    fastapi_app.include_router(feed_router)
    fastapi_app.include_router(checkin_router)

    yield fastapi_app, teacher_a, teacher_b, student, alpha, beta, post
    client.close()


# ── 1. Cross-class feed post deletion is rejected ────────────────────────────

async def test_teacher_cannot_delete_post_in_another_class(app):
    """Teacher B (Beta) tries to DELETE a post in class Alpha → 403."""
    from httpx import AsyncClient, ASGITransport
    from core.auth.permissions import TEACHER

    fastapi_app, _ta, teacher_b, _stu, _alpha, _beta, post = app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        ac.cookies.set("access_token", _token(str(teacher_b.id), int(TEACHER)))
        resp = await ac.delete(f"/posts/{post.id}")

    assert resp.status_code == 403


# ── 2. Post owner (student) can delete their own post ────────────────────────

async def test_owner_can_delete_own_post(app):
    """The student who created the post can delete it → 204 (or 200 with body)."""
    from httpx import AsyncClient, ASGITransport
    from core.auth.permissions import STUDENT
    from community.feed.models import FeedPost

    fastapi_app, _ta, _tb, student, _alpha, _beta, post = app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        ac.cookies.set("access_token", _token(str(student.id), int(STUDENT)))
        resp = await ac.delete(f"/posts/{post.id}")

    assert resp.status_code == 200
    # Verify the post is actually gone
    deleted = await FeedPost.get(post.id)
    assert deleted is None


# ── 3. Cross-class attendance correction is rejected ─────────────────────────

async def test_teacher_cannot_correct_attendance_in_another_class(app):
    """Teacher B (Beta) tries to POST attendance correction in class Alpha → 403."""
    from httpx import AsyncClient, ASGITransport
    from core.auth.permissions import TEACHER

    fastapi_app, _ta, teacher_b, student, alpha, _beta, _post = app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        ac.cookies.set("access_token", _token(str(teacher_b.id), int(TEACHER)))
        resp = await ac.post(
            f"/api/classes/{alpha.id}/attendance/correct",
            json={
                "student_id": str(student.id),
                "date": "2026-03-24",
                "status": "late",
                "partial_points": 3,
            },
        )

    assert resp.status_code == 403
