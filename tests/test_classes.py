"""Tests for class-management capability."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_classes")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    await init_beanie(database=database, document_models=[User, Class, ClassMembership])
    yield database
    client.close()


@pytest.fixture
async def teacher(db):
    from core.users.models import User
    from core.auth.password import hash_password
    from core.auth.permissions import TEACHER
    u = User(username="teach", hashed_password=hash_password("pw"), display_name="Teacher", permissions=int(TEACHER))
    await u.insert()
    return u


@pytest.fixture
async def student(db):
    from core.users.models import User
    from core.auth.password import hash_password
    from core.auth.permissions import STUDENT
    u = User(username="stu", hashed_password=hash_password("pw"), display_name="Student", permissions=int(STUDENT))
    await u.insert()
    return u


# --- Model structure ---

async def test_class_model_fields(db, teacher):
    from core.classes.models import Class
    cls = Class(
        name="Python 101",
        description="Intro course",
        visibility="public",
        owner_id=str(teacher.id),
        invite_code="ABCD1234",
    )
    assert cls.name == "Python 101"
    assert cls.visibility == "public"
    assert cls.invite_code == "ABCD1234"


async def test_class_visibility_must_be_valid(db):
    from core.classes.models import Class
    import pydantic
    with pytest.raises((pydantic.ValidationError, ValueError)):
        Class(name="x", visibility="invalid", owner_id="oid", invite_code="x")


async def test_membership_model_fields(db, teacher, student):
    from core.classes.models import ClassMembership
    m = ClassMembership(
        class_id="cls123",
        user_id=str(student.id),
        role="student",
    )
    assert m.class_id == "cls123"
    assert m.role == "student"


# --- Service operations ---

async def test_create_class_assigns_owner(db, teacher):
    from core.classes.service import create_class
    cls = await create_class(
        name="Test Class",
        description="desc",
        visibility="public",
        owner=teacher,
    )
    assert cls.owner_id == str(teacher.id)
    assert len(cls.invite_code) > 0


async def test_create_class_generates_invite_code(db, teacher):
    from core.classes.service import create_class
    cls1 = await create_class("A", "", "public", teacher)
    cls2 = await create_class("B", "", "public", teacher)
    assert cls1.invite_code != cls2.invite_code


async def test_join_class_via_invite_code(db, teacher, student):
    from core.classes.service import create_class, join_class_by_code
    cls = await create_class("My Class", "", "public", teacher)
    membership = await join_class_by_code(student, cls.invite_code)
    assert membership.user_id == str(student.id)
    assert membership.class_id == str(cls.id)


async def test_join_class_duplicate_returns_existing(db, teacher, student):
    from core.classes.service import create_class, join_class_by_code
    cls = await create_class("My Class", "", "public", teacher)
    m1 = await join_class_by_code(student, cls.invite_code)
    m2 = await join_class_by_code(student, cls.invite_code)
    assert m1.id == m2.id  # Same record returned, no duplicate


async def test_join_class_invalid_code_raises(db, student):
    from core.classes.service import join_class_by_code
    with pytest.raises(ValueError):
        await join_class_by_code(student, "INVALID_CODE")


async def test_public_classes_listed_private_not(db, teacher):
    from core.classes.service import create_class, get_public_classes
    await create_class("Public", "", "public", teacher)
    await create_class("Private", "", "private", teacher)
    classes = await get_public_classes()
    names = [c.name for c in classes]
    assert "Public" in names
    assert "Private" not in names


async def test_remove_member(db, teacher, student):
    from core.classes.service import create_class, join_class_by_code, remove_member, get_class_members
    cls = await create_class("MC", "", "public", teacher)
    await join_class_by_code(student, cls.invite_code)
    await remove_member(class_id=str(cls.id), user_id=str(student.id))
    members = await get_class_members(str(cls.id))
    member_ids = [m.user_id for m in members]
    assert str(student.id) not in member_ids


async def test_regenerate_invite_code_invalidates_old(db, teacher, student):
    from core.classes.service import create_class, regenerate_invite_code, join_class_by_code
    cls = await create_class("MC", "", "public", teacher)
    old_code = cls.invite_code
    await regenerate_invite_code(str(cls.id))
    with pytest.raises(ValueError):
        await join_class_by_code(student, old_code)


async def test_set_visibility(db, teacher):
    from core.classes.service import create_class, set_visibility, get_public_classes
    cls = await create_class("X", "", "public", teacher)
    await set_visibility(str(cls.id), "private")
    public = await get_public_classes()
    assert all(c.id != cls.id for c in public)
