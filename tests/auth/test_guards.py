"""Tests for require_permission FastAPI dependency guard."""
import pytest
from unittest.mock import AsyncMock
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_guards")
    from core.users.models import User
    await init_beanie(database=database, document_models=[User])
    yield database
    client.close()


async def test_authorized_request_passes_guard(db):
    """Authorized user with the required permission flag must pass the guard."""
    from core.auth.guards import require_permission
    from core.auth.permissions import Permission, MANAGE_OWN_CLASS as MANAGE_CLASS
    from core.users.models import User
    from core.auth.password import hash_password

    user = User(
        username="teach1",
        hashed_password=hash_password("pw"),
        display_name="Teacher",
        permissions=int(MANAGE_CLASS | Permission.READ_OWN_PROFILE),
    )

    dep = require_permission(MANAGE_CLASS)
    result = await dep(current_user=user)
    assert result is user


async def test_unauthorized_request_blocked_by_guard(db):
    """User without required permission flag must get HTTP 403."""
    from core.auth.guards import require_permission
    from core.auth.permissions import Permission, MANAGE_OWN_CLASS as MANAGE_CLASS, READ_OWN_PROFILE
    from core.users.models import User
    from core.auth.password import hash_password
    from fastapi import HTTPException

    user = User(
        username="student1",
        hashed_password=hash_password("pw"),
        display_name="Student",
        permissions=int(READ_OWN_PROFILE),  # no MANAGE_CLASS
    )

    dep = require_permission(MANAGE_CLASS)
    with pytest.raises(HTTPException) as exc_info:
        await dep(current_user=user)
    assert exc_info.value.status_code == 403


async def test_guard_with_zero_permissions_blocked(db):
    """User with permissions=0 must be blocked by any guard."""
    from core.auth.guards import require_permission
    from core.auth.permissions import Permission, READ_OWN_PROFILE
    from core.users.models import User
    from core.auth.password import hash_password
    from fastapi import HTTPException

    user = User(
        username="noone",
        hashed_password=hash_password("pw"),
        display_name="NoOne",
        permissions=0,
    )

    dep = require_permission(READ_OWN_PROFILE)
    with pytest.raises(HTTPException) as exc_info:
        await dep(current_user=user)
    assert exc_info.value.status_code == 403
