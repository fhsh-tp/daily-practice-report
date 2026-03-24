"""Tests for the resubmission flow (task 7.1)."""
import pytest
from datetime import date, datetime, timezone, timedelta
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_resubmission")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from tasks.templates.models import TaskTemplate, TaskAssignment, TaskScheduleRule
    from tasks.submissions.models import TaskSubmission
    await init_beanie(
        database=database,
        document_models=[User, Class, ClassMembership, TaskTemplate, TaskAssignment, TaskScheduleRule, TaskSubmission],
    )
    yield database
    client.close()


@pytest.fixture
async def teacher(db):
    from core.users.models import User
    from core.auth.password import hash_password
    u = User(username="teach", hashed_password=hash_password("pw"), display_name="T")
    await u.insert()
    return u


@pytest.fixture
async def student(db):
    from core.users.models import User
    from core.classes.models import ClassMembership
    from core.auth.password import hash_password
    u = User(username="stu", hashed_password=hash_password("pw"), display_name="S")
    await u.insert()
    await ClassMembership(class_id="cls1", user_id=str(u.id), role="student").insert()
    return u


@pytest.fixture
async def template(db, teacher):
    from tasks.templates.service import create_template
    return await create_template(
        name="Daily Log",
        description="",
        class_id="cls1",
        fields=[{"name": "notes", "field_type": "text", "required": True}],
        owner=teacher,
    )


async def _make_rejected(template, student, target_date, deadline=None):
    """Helper: create a rejected submission with optional resubmit deadline."""
    from tasks.submissions.models import TaskSubmission
    sub = TaskSubmission(
        template_id=str(template.id),
        template_snapshot={"name": "Daily Log", "fields": []},
        field_values={"notes": "first"},
        student_id=str(student.id),
        class_id="cls1",
        date=target_date,
        status="rejected",
        rejection_reason="Not good",
        resubmit_deadline=deadline,
    )
    await sub.insert()
    return sub


# --- Student resubmits a rejected task ---

async def test_resubmit_sets_parent_submission_id(db, student, template):
    """Resubmission links parent_submission_id to the rejected submission (Student resubmits a rejected task)."""
    from tasks.submissions.service import submit_task
    target = date(2026, 3, 22)
    deadline = datetime.now(timezone.utc) + timedelta(days=3)
    rejected = await _make_rejected(template, student, target, deadline=deadline)

    new_sub = await submit_task(template, "cls1", student, target, {"notes": "retry"})
    assert new_sub.parent_submission_id == str(rejected.id)


async def test_resubmit_without_deadline_blocked(db, student, template):
    """No deadline set → resubmission is blocked (No resubmit when deadline has passed or was not set)."""
    from tasks.submissions.service import submit_task
    target = date(2026, 3, 22)
    await _make_rejected(template, student, target, deadline=None)

    with pytest.raises(ValueError, match="補繳期限"):
        await submit_task(template, "cls1", student, target, {"notes": "retry"})


async def test_resubmit_after_deadline_blocked(db, student, template):
    """Deadline passed → resubmission is blocked (No resubmit when deadline has passed or was not set)."""
    from tasks.submissions.service import submit_task
    target = date(2026, 3, 22)
    expired = datetime(2026, 1, 1, tzinfo=timezone.utc)
    await _make_rejected(template, student, target, deadline=expired)

    with pytest.raises(ValueError, match="補繳期限已過"):
        await submit_task(template, "cls1", student, target, {"notes": "too late"})


async def test_resubmit_when_pending_exists_blocked(db, student, template):
    """Pending submission still blocks resubmission (duplicate guard)."""
    from tasks.submissions.service import submit_task
    target = date(2026, 3, 22)
    # First a pending submission (status defaults to "pending")
    await submit_task(template, "cls1", student, target, {"notes": "first"})

    with pytest.raises(ValueError, match="already submitted"):
        await submit_task(template, "cls1", student, target, {"notes": "dup"})
