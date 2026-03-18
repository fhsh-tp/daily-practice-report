"""Tests for get_current_user and JWT permissions flow."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_deps")
    from core.users.models import User
    await init_beanie(database=database, document_models=[User])
    yield database
    client.close()


async def test_get_current_user_payload_contains_permissions(db):
    """JWT created from User.permissions must decode with permissions claim."""
    from core.users.models import User
    from core.auth.jwt import create_access_token, decode_access_token
    from core.auth.permissions import TEACHER
    from core.auth.password import hash_password

    user = User(
        username="teach",
        hashed_password=hash_password("pw"),
        display_name="Teacher",
        permissions=int(TEACHER),
    )
    await user.insert()

    token = create_access_token(user_id=str(user.id), permissions=int(TEACHER))
    payload = decode_access_token(token)
    assert payload["permissions"] == int(TEACHER)
    assert payload["user_id"] == str(user.id)


def test_deps_has_no_require_teacher():
    """deps.py must not export require_teacher (removed)."""
    import core.auth.deps as deps
    assert not hasattr(deps, "require_teacher")
    assert not hasattr(deps, "require_student")
