"""Tests for shared page context dependency."""
import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from core.auth.password import hash_password
from core.auth.permissions import STUDENT, TEACHER, SITE_ADMIN
from core.classes.models import Class, ClassMembership
from core.users.models import User


@pytest.fixture
async def db():
    """Initialise Beanie with a mock MongoDB."""
    client = AsyncMongoMockClient()
    database = client.get_database("test_page_context")
    await init_beanie(database=database, document_models=[User, Class, ClassMembership])

    yield database

    client.close()


@pytest.fixture
async def student_user(db):
    user = User(
        username="student1",
        hashed_password=hash_password("pass"),
        display_name="Student One",
        permissions=int(STUDENT),
    )
    await user.insert()
    return user


@pytest.fixture
async def teacher_user(db):
    user = User(
        username="teacher1",
        hashed_password=hash_password("pass"),
        display_name="Teacher One",
        permissions=int(TEACHER),
    )
    await user.insert()
    return user


@pytest.fixture
async def admin_user(db):
    user = User(
        username="admin1",
        hashed_password=hash_password("pass"),
        display_name="Admin One",
        permissions=int(SITE_ADMIN),
    )
    await user.insert()
    return user


async def test_teacher_receives_full_sidebar_context(db, teacher_user):
    """Teacher user receives can_manage_class, can_manage_tasks, and classes list."""
    from shared.page_context import build_page_context

    cls = Class(
        name="Math 101",
        visibility="private",
        owner_id=str(teacher_user.id),
        invite_code="ABC",
    )
    await cls.insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(teacher_user.id), role="teacher"
    ).insert()

    ctx = await build_page_context(teacher_user)

    assert ctx["can_manage_class"] is True
    assert ctx["can_manage_tasks"] is True
    assert ctx["can_manage_users"] is False
    assert ctx["is_sys_admin"] is False
    assert len(ctx["classes"]) == 1
    assert ctx["classes"][0]["class_id"] == str(cls.id)
    assert ctx["classes"][0]["class_name"] == "Math 101"


async def test_student_receives_empty_management_context(db, student_user):
    """Student user receives all management flags as False, classes lists memberships."""
    from shared.page_context import build_page_context

    cls = Class(
        name="English 101",
        visibility="private",
        owner_id="owner",
        invite_code="DEF",
    )
    await cls.insert()
    await ClassMembership(
        class_id=str(cls.id), user_id=str(student_user.id), role="student"
    ).insert()

    ctx = await build_page_context(student_user)

    assert ctx["can_manage_class"] is False
    assert ctx["can_manage_tasks"] is False
    assert ctx["can_manage_users"] is False
    assert ctx["is_sys_admin"] is False
    assert len(ctx["classes"]) == 1
    assert ctx["classes"][0]["class_name"] == "English 101"


async def test_admin_receives_admin_flags(db, admin_user):
    """Admin user receives can_manage_users and is_sys_admin as True."""
    from shared.page_context import build_page_context

    ctx = await build_page_context(admin_user)

    assert ctx["can_manage_users"] is True
    assert ctx["is_sys_admin"] is True
    assert ctx["can_manage_class"] is True  # SITE_ADMIN includes MANAGE_ALL_CLASSES
    assert ctx["can_manage_all_classes"] is True


async def test_archived_classes_excluded(db, teacher_user):
    """Archived classes are excluded from the classes list."""
    from shared.page_context import build_page_context

    active_cls = Class(
        name="Active Class",
        visibility="private",
        owner_id=str(teacher_user.id),
        invite_code="ACT",
    )
    await active_cls.insert()
    await ClassMembership(
        class_id=str(active_cls.id), user_id=str(teacher_user.id), role="teacher"
    ).insert()

    archived_cls = Class(
        name="Archived Class",
        visibility="private",
        owner_id=str(teacher_user.id),
        invite_code="ARC",
        is_archived=True,
    )
    await archived_cls.insert()
    await ClassMembership(
        class_id=str(archived_cls.id), user_id=str(teacher_user.id), role="teacher"
    ).insert()

    ctx = await build_page_context(teacher_user)

    assert len(ctx["classes"]) == 1
    assert ctx["classes"][0]["class_name"] == "Active Class"
