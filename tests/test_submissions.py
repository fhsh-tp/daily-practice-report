"""Tests for task-submissions capability."""
import pytest
from datetime import date
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


ALL_MODELS = None


@pytest.fixture
async def db():
    global ALL_MODELS
    client = AsyncMongoMockClient()
    database = client.get_database("test_submissions")
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
    u = User(username="teach", hashed_password=hash_password("pw"), display_name="T", role="teacher")
    await u.insert()
    return u


@pytest.fixture
async def student(db):
    from core.users.models import User
    from core.auth.password import hash_password
    u = User(username="stu", hashed_password=hash_password("pw"), display_name="S", role="student")
    await u.insert()
    return u


@pytest.fixture
async def template(db, teacher):
    from tasks.templates.service import create_template
    return await create_template(
        name="Daily Log",
        description="",
        class_id="cls1",
        fields=[
            {"name": "notes", "field_type": "text", "required": True},
            {"name": "optional", "field_type": "number", "required": False},
        ],
        owner=teacher,
    )


# --- Submission ---

async def test_submit_task_success(db, student, template):
    from tasks.submissions.service import submit_task
    sub = await submit_task(
        template=template,
        class_id="cls1",
        student=student,
        submission_date=date(2026, 3, 18),
        field_values={"notes": "Today I learned Python"},
    )
    assert sub.student_id == str(student.id)
    assert sub.field_values["notes"] == "Today I learned Python"
    assert sub.template_snapshot["name"] == "Daily Log"


async def test_submit_task_duplicate_raises(db, student, template):
    from tasks.submissions.service import submit_task
    await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "first"})
    with pytest.raises(ValueError, match="already submitted"):
        await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "second"})


async def test_submit_task_missing_required_field_raises(db, student, template):
    from tasks.submissions.service import submit_task
    with pytest.raises(ValueError, match="required"):
        await submit_task(template, "cls1", student, date(2026, 3, 18), {})


async def test_submission_history_ordered_by_date(db, student, template):
    from tasks.submissions.service import submit_task, get_student_submissions
    await submit_task(template, "cls1", student, date(2026, 3, 17), {"notes": "day1"})
    await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "day2"})
    subs = await get_student_submissions(str(student.id))
    assert subs[0].date >= subs[1].date  # reverse chronological


async def test_teacher_views_class_submissions(db, student, template, teacher):
    from tasks.submissions.service import submit_task, get_class_submissions_for_date
    await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "hello"})
    subs = await get_class_submissions_for_date("cls1", date(2026, 3, 18))
    assert len(subs) == 1
    assert subs[0].student_id == str(student.id)


async def test_number_field_rejects_non_numeric(db, student, template):
    from tasks.submissions.service import submit_task
    with pytest.raises((ValueError, TypeError)):
        await submit_task(
            template, "cls1", student, date(2026, 3, 18),
            {"notes": "ok", "optional": "not_a_number"}
        )


# --- TaskSubmission model: teacher_comment / reviewed_at fields ---

async def test_new_submission_has_null_comment(db, student, template):
    """New submissions have null teacher_comment and reviewed_at (task 1.1, 1.2)."""
    from tasks.submissions.service import submit_task
    sub = await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "hi"})
    assert sub.teacher_comment is None
    assert sub.reviewed_at is None


# --- TaskSubmission review state fields ---

async def test_new_submission_has_pending_status(db, student, template):
    """New submission status defaults to pending (TaskSubmission stores review state)."""
    from tasks.submissions.service import submit_task
    sub = await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "hi"})
    assert sub.status == "pending"
    assert sub.rejection_reason is None
    assert sub.resubmit_deadline is None
    assert sub.parent_submission_id is None


async def test_rejected_submission_allows_resubmission(db, student, template):
    """A rejected submission does not block a new submission (Resubmission allowed after rejection)."""
    from tasks.submissions.service import submit_task
    sub = await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "first"})
    sub.status = "rejected"
    await sub.save()
    # Should succeed without raising
    sub2 = await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "retry"})
    assert sub2.id != sub.id


async def test_pending_submission_blocks_duplicate(db, student, template):
    """A pending submission still blocks a duplicate (Duplicate submission rejected when active submission exists)."""
    from tasks.submissions.service import submit_task
    await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "first"})
    with pytest.raises(ValueError, match="already submitted"):
        await submit_task(template, "cls1", student, date(2026, 3, 18), {"notes": "dup"})
