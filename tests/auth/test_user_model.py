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


# --- IdentityTag ---

def test_identity_tag_enum_has_three_values():
    """IdentityTag must define exactly teacher, student, staff."""
    from core.users.models import IdentityTag
    values = {t.value for t in IdentityTag}
    assert values == {"teacher", "student", "staff"}


async def test_user_identity_tags_defaults_to_empty_list(db):
    """User.identity_tags must default to an empty list."""
    from core.users.models import User
    u = User(username="u1", hashed_password="h", display_name="U1")
    assert u.identity_tags == []


async def test_user_can_hold_multiple_identity_tags(db):
    """User must accept multiple identity tags."""
    from core.users.models import User, IdentityTag
    u = User(
        username="u2",
        hashed_password="h",
        display_name="U2",
        identity_tags=[IdentityTag.TEACHER, IdentityTag.STAFF],
    )
    await u.insert()
    fetched = await User.get(u.id)
    assert IdentityTag.TEACHER in fetched.identity_tags
    assert IdentityTag.STAFF in fetched.identity_tags


# --- User model new fields ---

async def test_user_name_defaults_to_empty_string(db):
    """User.name must default to empty string."""
    from core.users.models import User
    u = User(username="u3", hashed_password="h", display_name="U3")
    assert u.name == ""


async def test_user_email_defaults_to_empty_string(db):
    """User.email must default to empty string."""
    from core.users.models import User
    u = User(username="u4", hashed_password="h", display_name="U4")
    assert u.email == ""


async def test_user_student_profile_defaults_to_none(db):
    """User.student_profile must default to None."""
    from core.users.models import User
    u = User(username="u5", hashed_password="h", display_name="U5")
    assert u.student_profile is None


async def test_user_student_profile_stores_class_name_and_seat(db):
    """StudentProfile must store class_name and seat_number."""
    from core.users.models import User, StudentProfile, IdentityTag
    u = User(
        username="stu1",
        hashed_password="h",
        display_name="Stu1",
        name="陳小明",
        email="stu@school.edu",
        identity_tags=[IdentityTag.STUDENT],
        student_profile=StudentProfile(class_name="302班", seat_number=12),
    )
    await u.insert()
    fetched = await User.get(u.id)
    assert fetched.student_profile.class_name == "302班"
    assert fetched.student_profile.seat_number == 12
    assert fetched.name == "陳小明"
