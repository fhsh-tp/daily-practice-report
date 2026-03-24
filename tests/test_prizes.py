"""Tests for prize preview."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_prizes")
    from core.users.models import User
    from gamification.prizes.models import Prize
    await init_beanie(database=database, document_models=[User, Prize])
    yield database
    client.close()


@pytest.fixture
async def teacher(db):
    from core.users.models import User
    from core.auth.password import hash_password
    u = User(username="tchr", hashed_password=hash_password("pw"), display_name="T", role="teacher")
    await u.insert()
    return u


async def test_create_prize(db, teacher):
    from gamification.prizes.models import Prize
    prize = Prize(
        class_id="cls1", title="書券", prize_type="physical",
        point_cost=100, created_by=str(teacher.id),
    )
    await prize.insert()
    found = await Prize.get(prize.id)
    assert found.title == "書券"
    assert found.prize_type == "physical"


async def test_only_visible_prizes_for_students(db, teacher):
    from gamification.prizes.models import Prize
    await Prize(class_id="cls1", title="A", visible=True, point_cost=10, created_by=str(teacher.id)).insert()
    await Prize(class_id="cls1", title="B", visible=False, point_cost=20, created_by=str(teacher.id)).insert()

    visible = await Prize.find(Prize.class_id == "cls1", Prize.visible == True).to_list()  # noqa: E712
    assert len(visible) == 1
    assert visible[0].title == "A"


async def test_update_prize_visibility(db, teacher):
    from gamification.prizes.models import Prize
    prize = Prize(class_id="cls1", title="X", visible=True, point_cost=0, created_by=str(teacher.id))
    await prize.insert()
    prize.visible = False
    await prize.save()

    refreshed = await Prize.get(prize.id)
    assert refreshed.visible is False


async def test_delete_prize(db, teacher):
    from gamification.prizes.models import Prize
    prize = Prize(class_id="cls1", title="Y", point_cost=0, created_by=str(teacher.id))
    await prize.insert()
    await prize.delete()
    assert await Prize.get(prize.id) is None


# ─── Router-level test: student visibility filter ────────────────────────────

@pytest.fixture
async def prizes_app(db):
    from core.users.models import User, IdentityTag
    from core.auth.password import hash_password
    from core.auth.permissions import STUDENT
    from fastapi import FastAPI
    from gamification.prizes.router import router as prizes_router

    student = User(
        username="stu_list",
        hashed_password=hash_password("pw"),
        display_name="Student",
        permissions=int(STUDENT),
        identity_tags=[IdentityTag.STUDENT],
    )
    await student.insert()

    app = FastAPI()
    app.include_router(prizes_router)
    return app, student


async def test_student_list_prizes_returns_200(prizes_app):
    """Student calling list_prizes must return 200 and see only visible prizes.

    Bug (R7): user.role raises AttributeError — User uses identity_tags, not role.
    """
    from core.auth.jwt import create_access_token
    from core.auth.permissions import STUDENT
    from gamification.prizes.models import Prize

    app, student = prizes_app
    await Prize(class_id="cls1", title="Visible", visible=True, point_cost=10, created_by=str(student.id)).insert()
    await Prize(class_id="cls1", title="Hidden", visible=False, point_cost=20, created_by=str(student.id)).insert()

    token = create_access_token(user_id=str(student.id), permissions=int(STUDENT))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("access_token", token)
        resp = await ac.get("/classes/cls1/prizes")
    assert resp.status_code == 200
    titles = [p["title"] for p in resp.json()]
    assert titles == ["Visible"]
