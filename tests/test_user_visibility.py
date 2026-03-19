"""Tests for user profile visibility schemas."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_visibility")
    from core.users.models import User
    await init_beanie(database=database, document_models=[User])
    yield database
    client.close()


async def _make_user(username, identity_tags=None, name="Real Name", email="e@e.com"):
    from core.users.models import User, IdentityTag
    from core.auth.password import hash_password
    u = User(
        username=username,
        hashed_password=hash_password("pw"),
        display_name=username.capitalize(),
        name=name,
        email=email,
        identity_tags=identity_tags or [],
    )
    await u.insert()
    return u


async def test_student_viewer_sees_only_public_view(db):
    """Student viewer must receive UserPublicView (display_name only)."""
    from core.users.models import IdentityTag
    from core.users.schemas import select_view
    viewer = await _make_user("viewer", identity_tags=[IdentityTag.STUDENT])
    target = await _make_user("target", identity_tags=[IdentityTag.STUDENT])
    result = select_view(viewer, target)
    assert "display_name" in result
    assert "name" not in result
    assert "email" not in result


async def test_teacher_viewer_sees_staff_view(db):
    """Teacher viewer must receive UserStaffView (includes name and email)."""
    from core.users.models import IdentityTag
    from core.users.schemas import select_view
    viewer = await _make_user("teacher", identity_tags=[IdentityTag.TEACHER])
    target = await _make_user("stu", identity_tags=[IdentityTag.STUDENT])
    result = select_view(viewer, target)
    assert "name" in result
    assert "email" in result
    assert "display_name" in result


async def test_staff_viewer_sees_staff_view(db):
    """Staff viewer must receive UserStaffView."""
    from core.users.models import IdentityTag
    from core.users.schemas import select_view
    viewer = await _make_user("staff_user", identity_tags=[IdentityTag.STAFF])
    target = await _make_user("stu2", identity_tags=[IdentityTag.STUDENT])
    result = select_view(viewer, target)
    assert "name" in result


async def test_admin_view_includes_all_fields(db):
    """admin_view must include username, permissions, tags, and all new fields."""
    from core.users.schemas import admin_view
    user = await _make_user("adm", name="Admin Name", email="adm@b.com")
    result = admin_view(user)
    assert "username" in result
    assert "permissions" in result
    assert "tags" in result
    assert "name" in result
    assert "email" in result
    assert "identity_tags" in result
    assert "student_profile" in result
