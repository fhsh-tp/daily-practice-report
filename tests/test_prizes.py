"""Tests for prize preview."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


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
