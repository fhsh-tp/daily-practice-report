"""Tests for User model permissions and tags fields."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_user_model")
    from core.users.models import User
    await init_beanie(database=database, document_models=[User])
    yield database
    client.close()


async def test_user_model_stores_permissions_as_integer(db):
    """User created with a permissions int must store it correctly."""
    from core.users.models import User
    from core.auth.permissions import STUDENT
    u = User(
        username="alice",
        hashed_password="hashed",
        display_name="Alice",
        permissions=int(STUDENT),
    )
    assert u.permissions == int(STUDENT)


async def test_user_model_permissions_defaults_to_zero(db):
    """User.permissions must default to 0 when not specified."""
    from core.users.models import User
    u = User(username="bob", hashed_password="h", display_name="Bob")
    assert u.permissions == 0


async def test_user_model_tags_defaults_to_empty_list(db):
    """User.tags must default to an empty list."""
    from core.users.models import User
    u = User(username="carol", hashed_password="h", display_name="Carol")
    assert u.tags == []


async def test_user_model_has_no_role_field(db):
    """User model must not have a role field."""
    from core.users.models import User
    u = User(username="dave", hashed_password="h", display_name="Dave")
    assert not hasattr(u, "role")


async def test_user_created_with_permissions_preset(db):
    """Stored permissions field must equal the integer value of the Role Preset."""
    from core.users.models import User
    from core.auth.permissions import TEACHER
    u = User(
        username="teach",
        hashed_password="h",
        display_name="Teacher",
        permissions=int(TEACHER),
    )
    await u.insert()
    fetched = await User.get(u.id)
    assert fetched.permissions == int(TEACHER)
