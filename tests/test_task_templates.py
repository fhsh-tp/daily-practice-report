"""Tests for task-templates capability."""
import pytest
from datetime import date
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_templates")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from tasks.templates.models import TaskTemplate, TaskAssignment
    from tasks.submissions.models import TaskSubmission
    await init_beanie(
        database=database,
        document_models=[User, Class, ClassMembership, TaskTemplate, TaskAssignment, TaskSubmission]
    )
    yield database
    client.close()


@pytest.fixture
async def teacher(db):
    from core.users.models import User
    from core.auth.password import hash_password
    u = User(username="teach", hashed_password=hash_password("pw"), display_name="T", role="teacher")
    await u.insert()
    return u


# --- Model structure ---

async def test_template_requires_at_least_one_field(db, teacher):
    from tasks.templates.service import create_template
    import pydantic
    with pytest.raises((ValueError, pydantic.ValidationError)):
        await create_template(
            name="Empty",
            description="",
            class_id="cls1",
            fields=[],
            owner=teacher,
        )


async def test_template_field_types_supported(db, teacher):
    from tasks.templates.service import create_template
    tmpl = await create_template(
        name="Daily Log",
        description="Daily report",
        class_id="cls1",
        fields=[
            {"name": "text_field", "field_type": "text", "required": True},
            {"name": "md_field", "field_type": "markdown", "required": False},
            {"name": "num_field", "field_type": "number", "required": False},
            {"name": "check_field", "field_type": "checkbox", "required": False},
        ],
        owner=teacher,
    )
    assert len(tmpl.fields) == 4
    types = [f.field_type for f in tmpl.fields]
    assert "text" in types
    assert "markdown" in types
    assert "number" in types
    assert "checkbox" in types


async def test_template_invalid_field_type_raises(db, teacher):
    from tasks.templates.service import create_template
    with pytest.raises((ValueError, Exception)):
        await create_template(
            name="Bad",
            description="",
            class_id="cls1",
            fields=[{"name": "f", "field_type": "video", "required": True}],
            owner=teacher,
        )


# --- Assignment ---

async def test_assign_template_to_date(db, teacher):
    from tasks.templates.service import create_template, assign_template_to_date, get_template_for_date
    tmpl = await create_template(
        name="T",
        description="",
        class_id="cls1",
        fields=[{"name": "f", "field_type": "text", "required": True}],
        owner=teacher,
    )
    target_date = date(2026, 3, 18)
    assignment = await assign_template_to_date(
        template_id=str(tmpl.id),
        class_id="cls1",
        target_date=target_date,
    )
    assert assignment.template_id == str(tmpl.id)

    found = await get_template_for_date("cls1", target_date)
    assert found is not None
    assert str(found.id) == str(tmpl.id)


async def test_no_template_for_date_returns_none(db):
    from tasks.templates.service import get_template_for_date
    result = await get_template_for_date("cls1", date(2026, 1, 1))
    assert result is None


# --- Edit ---

async def test_edit_template_updates_title(db, teacher):
    from tasks.templates.service import create_template, update_template
    tmpl = await create_template(
        name="Old Title",
        description="",
        class_id="cls1",
        fields=[{"name": "f", "field_type": "text", "required": True}],
        owner=teacher,
    )
    updated = await update_template(str(tmpl.id), name="New Title")
    assert updated.name == "New Title"


# --- Delete ---

async def test_delete_template_no_submissions(db, teacher):
    from tasks.templates.service import create_template, delete_template
    tmpl = await create_template(
        name="T",
        description="",
        class_id="cls1",
        fields=[{"name": "f", "field_type": "text", "required": True}],
        owner=teacher,
    )
    # No submissions; should succeed
    await delete_template(str(tmpl.id))
    from tasks.templates.models import TaskTemplate
    found = await TaskTemplate.get(tmpl.id)
    assert found is None


# --- Archive / Unarchive (task 4.6) ---

async def test_archive_template_hidden_from_get_template_for_date(db, teacher):
    """After archive_template(), get_template_for_date() shall not return the template."""
    from datetime import date
    from tasks.templates.service import (
        archive_template,
        assign_template_to_date,
        create_template,
        get_template_for_date,
    )

    tmpl = await create_template(
        name="Archived",
        description="",
        class_id="cls_arc",
        fields=[{"name": "f", "field_type": "text", "required": True}],
        owner=teacher,
    )
    target = date(2026, 3, 19)
    await assign_template_to_date(str(tmpl.id), "cls_arc", target)

    # Before archiving: should be found
    found = await get_template_for_date("cls_arc", target)
    assert found is not None

    # Archive
    await archive_template(str(tmpl.id))

    # After archiving: should NOT be found
    found_after = await get_template_for_date("cls_arc", target)
    assert found_after is None


async def test_unarchive_template_restores_visibility(db, teacher):
    """After unarchive_template(), get_template_for_date() returns the template again."""
    from datetime import date
    from tasks.templates.service import (
        archive_template,
        assign_template_to_date,
        create_template,
        get_template_for_date,
        unarchive_template,
    )

    tmpl = await create_template(
        name="Unarchived",
        description="",
        class_id="cls_unarc",
        fields=[{"name": "f", "field_type": "text", "required": True}],
        owner=teacher,
    )
    target = date(2026, 3, 19)
    await assign_template_to_date(str(tmpl.id), "cls_unarc", target)
    await archive_template(str(tmpl.id))

    # Unarchive
    await unarchive_template(str(tmpl.id))

    # Should be visible again
    found = await get_template_for_date("cls_unarc", target)
    assert found is not None
    assert str(found.id) == str(tmpl.id)
