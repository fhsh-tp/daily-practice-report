"""Tests for can_manage_class ownership-scoped permission logic and batch invite."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_class_perms")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    await init_beanie(database=database, document_models=[User, Class, ClassMembership])
    yield database
    client.close()


async def _make_user(username, permissions_val, identity_tags=None, name=""):
    from core.users.models import User, IdentityTag
    from core.auth.password import hash_password
    u = User(
        username=username,
        hashed_password=hash_password("pw"),
        display_name=username.capitalize(),
        permissions=permissions_val,
        identity_tags=identity_tags or [],
        name=name,
    )
    await u.insert()
    return u


# ── can_manage_class ──────────────────────────────────────────────────────────

async def test_class_manager_can_manage_any_class(db):
    """User with MANAGE_ALL_CLASSES must be able to manage any class."""
    from core.auth.permissions import MANAGE_ALL_CLASSES, TEACHER
    from core.classes.service import create_class, can_manage_class
    owner = await _make_user("owner", int(TEACHER))
    manager = await _make_user("manager", int(MANAGE_ALL_CLASSES | TEACHER))
    cls = await create_class("Test", "", "public", owner)
    assert await can_manage_class(manager, cls) is True


async def test_teacher_can_manage_own_class(db):
    """Teacher with MANAGE_OWN_CLASS and teacher membership can manage their class."""
    from core.auth.permissions import TEACHER
    from core.classes.service import create_class, can_manage_class
    teacher = await _make_user("teach", int(TEACHER))
    cls = await create_class("My Class", "", "public", teacher)
    assert await can_manage_class(teacher, cls) is True


async def test_teacher_cannot_manage_other_teacher_class(db):
    """Teacher with MANAGE_OWN_CLASS but no membership in class cannot manage it."""
    from core.auth.permissions import TEACHER
    from core.classes.service import create_class, can_manage_class
    owner = await _make_user("owner", int(TEACHER))
    other_teacher = await _make_user("other", int(TEACHER))
    cls = await create_class("Owner Class", "", "public", owner)
    assert await can_manage_class(other_teacher, cls) is False


async def test_student_cannot_manage_class(db):
    """Student without MANAGE_OWN_CLASS cannot manage any class."""
    from core.auth.permissions import TEACHER, STUDENT
    from core.classes.service import create_class, can_manage_class
    owner = await _make_user("owner", int(TEACHER))
    student = await _make_user("stu", int(STUDENT))
    cls = await create_class("Some Class", "", "public", owner)
    assert await can_manage_class(student, cls) is False


# ── Teacher creates class requires MANAGE_OWN_CLASS ──────────────────────────

async def test_create_class_allowed_with_manage_own_class(db):
    """User with MANAGE_OWN_CLASS must be able to create a class."""
    from core.auth.permissions import TEACHER
    from core.classes.service import create_class
    teacher = await _make_user("t1", int(TEACHER))
    cls = await create_class("New Class", "", "public", teacher)
    assert cls.name == "New Class"
    assert cls.owner_id == str(teacher.id)


# ── Batch invite search ───────────────────────────────────────────────────────

async def test_invite_search_by_name_returns_non_members(db):
    """search_students_for_invite must return STUDENT identity users not in class."""
    from core.auth.permissions import TEACHER, STUDENT
    from core.users.models import IdentityTag
    from core.classes.service import create_class, search_students_for_invite
    teacher = await _make_user("teach", int(TEACHER))
    stu1 = await _make_user("s001", int(STUDENT), identity_tags=[IdentityTag.STUDENT], name="陳小明")
    stu2 = await _make_user("s002", int(STUDENT), identity_tags=[IdentityTag.STUDENT], name="王大華")
    cls = await create_class("Class A", "", "public", teacher)

    results = await search_students_for_invite(str(cls.id), q="陳", search_type="name")
    result_ids = [r["user_id"] for r in results]
    assert str(stu1.id) in result_ids
    assert str(stu2.id) not in result_ids


async def test_invite_search_excludes_existing_members(db):
    """search_students_for_invite must exclude users already in the class."""
    from core.auth.permissions import TEACHER, STUDENT
    from core.users.models import IdentityTag
    from core.classes.service import create_class, join_class_by_code, search_students_for_invite
    teacher = await _make_user("teach", int(TEACHER))
    stu = await _make_user("s003", int(STUDENT), identity_tags=[IdentityTag.STUDENT], name="陳已加入")
    cls = await create_class("Class B", "", "public", teacher)
    await join_class_by_code(stu, cls.invite_code)

    results = await search_students_for_invite(str(cls.id), q="陳", search_type="name")
    result_ids = [r["user_id"] for r in results]
    assert str(stu.id) not in result_ids


async def test_invite_search_by_class_name(db):
    """search_students_for_invite with type=class_name filters by student_profile.class_name."""
    from core.auth.permissions import TEACHER, STUDENT
    from core.users.models import IdentityTag, StudentProfile
    from core.classes.service import create_class, search_students_for_invite
    teacher = await _make_user("teach", int(TEACHER))
    cls = await create_class("Class C", "", "public", teacher)

    # Create student with class_name
    from core.users.models import User
    from core.auth.password import hash_password
    stu = User(
        username="s004", hashed_password=hash_password("pw"), display_name="S004",
        permissions=int(STUDENT), identity_tags=[IdentityTag.STUDENT],
        student_profile=StudentProfile(class_name="302班", seat_number=3),
    )
    await stu.insert()

    results = await search_students_for_invite(str(cls.id), q="302", search_type="class_name")
    result_ids = [r["user_id"] for r in results]
    assert str(stu.id) in result_ids


# ── Batch invite add ──────────────────────────────────────────────────────────

async def test_batch_invite_adds_students(db):
    """batch_invite_students must add all specified users to the class."""
    from core.auth.permissions import TEACHER, STUDENT
    from core.users.models import IdentityTag
    from core.classes.service import create_class, batch_invite_students, get_class_members
    teacher = await _make_user("teach", int(TEACHER))
    stu1 = await _make_user("bs1", int(STUDENT), identity_tags=[IdentityTag.STUDENT])
    stu2 = await _make_user("bs2", int(STUDENT), identity_tags=[IdentityTag.STUDENT])
    cls = await create_class("Batch Class", "", "public", teacher)

    await batch_invite_students(str(cls.id), [str(stu1.id), str(stu2.id)])
    members = await get_class_members(str(cls.id))
    member_ids = {m.user_id for m in members}
    assert str(stu1.id) in member_ids
    assert str(stu2.id) in member_ids


async def test_batch_invite_skips_existing_members(db):
    """batch_invite_students must silently skip users already in class."""
    from core.auth.permissions import TEACHER, STUDENT
    from core.users.models import IdentityTag
    from core.classes.service import create_class, join_class_by_code, batch_invite_students, get_class_members
    teacher = await _make_user("teach", int(TEACHER))
    stu = await _make_user("bs3", int(STUDENT), identity_tags=[IdentityTag.STUDENT])
    cls = await create_class("Idempotent Class", "", "public", teacher)
    await join_class_by_code(stu, cls.invite_code)

    # Should not raise, should not create duplicate
    await batch_invite_students(str(cls.id), [str(stu.id)])
    members = await get_class_members(str(cls.id))
    stu_memberships = [m for m in members if m.user_id == str(stu.id)]
    assert len(stu_memberships) == 1
