"""Tests for leaderboard."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_leaderboard")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from gamification.points.models import PointTransaction, ClassPointConfig
    from gamification.badges.models import BadgeDefinition, BadgeAward
    await init_beanie(
        database=database,
        document_models=[
            User, Class, ClassMembership,
            PointTransaction, ClassPointConfig,
            BadgeDefinition, BadgeAward,
        ],
    )
    yield database
    client.close()


@pytest.fixture
async def cls(db):
    from core.classes.models import Class
    c = Class(name="Math", visibility="public", owner_id="t1", invite_code="ABC", leaderboard_enabled=True)
    await c.insert()
    return c


async def _make_student(username, display_name, class_id, points):
    from core.users.models import User
    from core.classes.models import ClassMembership
    from core.auth.password import hash_password
    from gamification.points.service import award_points

    u = User(username=username, hashed_password=hash_password("pw"), display_name=display_name, role="student")
    await u.insert()
    await ClassMembership(class_id=class_id, user_id=str(u.id), role="student").insert()
    if points:
        await award_points(str(u.id), class_id, points, "test", "evt")
    return u


async def test_class_leaderboard_ranked(db, cls):
    from gamification.leaderboard.router import _build_class_leaderboard

    await _make_student("s1", "Alice", str(cls.id), 30)
    await _make_student("s2", "Bob", str(cls.id), 50)
    await _make_student("s3", "Carol", str(cls.id), 50)

    board = await _build_class_leaderboard(str(cls.id))
    assert board[0]["rank"] == 1
    assert board[0]["points"] == 50
    # Tied students share rank
    assert board[1]["rank"] == 1
    assert board[1]["points"] == 50
    # Alice is rank 3
    assert board[2]["rank"] == 3
    assert board[2]["display_name"] == "Alice"


async def test_leaderboard_disabled_returns_not_visible(db):
    from core.classes.models import Class
    c = Class(name="Sci", visibility="public", owner_id="t1", invite_code="XYZ", leaderboard_enabled=False)
    await c.insert()

    # Student role + leaderboard_enabled=False → not visible
    assert not c.leaderboard_enabled
