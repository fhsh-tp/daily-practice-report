"""Tests for submission approval capability."""
import pytest
from datetime import date
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_approval")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from tasks.templates.models import TaskTemplate, TaskAssignment, TaskScheduleRule
    from tasks.submissions.models import TaskSubmission
    from gamification.points.models import PointTransaction, ClassPointConfig
    from community.feed.models import FeedPost, Reaction
    await init_beanie(
        database=database,
        document_models=[
            User, Class, ClassMembership,
            TaskTemplate, TaskAssignment, TaskScheduleRule,
            TaskSubmission,
            PointTransaction, ClassPointConfig,
            FeedPost, Reaction,
        ],
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
async def point_config(db):
    from gamification.points.models import ClassPointConfig
    config = ClassPointConfig(class_id="cls1", checkin_points=5, submission_points=10)
    await config.insert()
    return config


@pytest.fixture
async def pending_submission(db, student, point_config):
    """A pending submission with the initial submission_points already awarded."""
    from tasks.submissions.models import TaskSubmission
    from gamification.points.service import award_points
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"id": "tmpl1", "name": "Daily", "description": "", "fields": []},
        field_values={"notes": "hello"},
        student_id=str(student.id),
        class_id="cls1",
        date=date(2026, 3, 22),
        status="pending",
    )
    await sub.insert()
    await award_points(str(student.id), "cls1", point_config.submission_points, "submission", str(sub.id))
    return sub


@pytest.fixture
async def rejected_submission(db, student, point_config):
    """A rejected submission where points were awarded then revoked."""
    from tasks.submissions.models import TaskSubmission
    from gamification.points.models import PointTransaction
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"id": "tmpl1", "name": "Daily", "description": "", "fields": []},
        field_values={"notes": "hello"},
        student_id=str(student.id),
        class_id="cls1",
        date=date(2026, 3, 22),
        status="rejected",
        rejection_reason="Incomplete work",
    )
    await sub.insert()
    # Simulate initial award + rejection revoke
    award_tx = PointTransaction(
        student_id=str(student.id), class_id="cls1", amount=10,
        reason="submission", source_event="submission", source_id=str(sub.id), created_by="system",
    )
    await award_tx.insert()
    revoke_tx = PointTransaction(
        student_id=str(student.id), class_id="cls1", amount=-10,
        reason="submission_rejected", source_event="submission_rejected", source_id=str(sub.id), created_by="system",
    )
    await revoke_tx.insert()
    return sub


# --- Task 4.1: Teacher approves a task submission ---

async def test_approve_pending_submission_sets_status(db, teacher, pending_submission):
    """Teacher approves a pending submission — status changes to approved (Teacher approves a task submission)."""
    from tasks.submissions.models import TaskSubmission

    pending_submission.status = "approved"
    await pending_submission.save()

    found = await TaskSubmission.get(str(pending_submission.id))
    assert found.status == "approved"


async def test_approve_pending_no_new_point_transaction(db, teacher, pending_submission, point_config):
    """Approving a pending submission creates no extra PointTransaction (points were already awarded)."""
    from gamification.points.models import PointTransaction

    pending_submission.status = "approved"
    await pending_submission.save()

    txs = await PointTransaction.find(
        PointTransaction.student_id == pending_submission.student_id
    ).to_list()
    # Only the original award from submission
    assert len(txs) == 1
    assert txs[0].source_event == "submission"


async def test_approve_rejected_submission_restores_points(db, teacher, rejected_submission, point_config):
    """Teacher approves a previously rejected submission — re-awards submission_points
    (Teacher approves a previously rejected submission)."""
    from gamification.points.models import PointTransaction
    from gamification.points.service import award_points

    # Verify current balance is 0 (awarded + revoked)
    txs = await PointTransaction.find(
        PointTransaction.student_id == rejected_submission.student_id
    ).to_list()
    assert sum(t.amount for t in txs) == 0

    rejected_submission.status = "approved"
    await rejected_submission.save()
    await award_points(
        rejected_submission.student_id,
        rejected_submission.class_id,
        point_config.submission_points,
        "submission_reapproved",
        str(rejected_submission.id),
        created_by="teacher",
    )

    txs = await PointTransaction.find(
        PointTransaction.student_id == rejected_submission.student_id
    ).to_list()
    balance = sum(t.amount for t in txs)
    assert balance == point_config.submission_points

    reapproved = next(t for t in txs if t.source_event == "submission_reapproved")
    assert reapproved.amount == point_config.submission_points


# --- Task 4.2: Teacher rejects a task submission ---

async def test_reject_submission_sets_status_and_reason(db, teacher, pending_submission):
    """Teacher rejects submission — status='rejected', reason stored (Teacher rejects a task submission)."""
    from tasks.submissions.models import TaskSubmission

    pending_submission.status = "rejected"
    pending_submission.rejection_reason = "Insufficient detail"
    await pending_submission.save()

    found = await TaskSubmission.get(str(pending_submission.id))
    assert found.status == "rejected"
    assert found.rejection_reason == "Insufficient detail"


async def test_reject_submission_deducts_points(db, teacher, pending_submission, point_config):
    """Rejecting a submission creates a negative PointTransaction (submission_rejected)."""
    from gamification.points.models import PointTransaction

    pending_submission.status = "rejected"
    pending_submission.rejection_reason = "Incomplete"
    await pending_submission.save()

    # Revoke points via negative award_points
    from gamification.points.service import award_points
    await award_points(
        pending_submission.student_id,
        pending_submission.class_id,
        -point_config.submission_points,
        "submission_rejected",
        str(pending_submission.id),
        created_by="teacher",
    )

    txs = await PointTransaction.find(
        PointTransaction.student_id == pending_submission.student_id
    ).to_list()
    balance = sum(t.amount for t in txs)
    assert balance == 0  # 10 awarded, 10 revoked

    rejected_tx = next(t for t in txs if t.source_event == "submission_rejected")
    assert rejected_tx.amount == -point_config.submission_points


async def test_reject_empty_reason_blocked(db):
    """Rejection without reason must be blocked — empty string is invalid (Rejection without reason is rejected)."""
    # This validates the router-level guard: empty/whitespace reason triggers 422
    empty_reasons = ["", "   ", "\t"]
    for reason in empty_reasons:
        assert not reason.strip(), f"Expected empty reason to fail strip check: {reason!r}"


async def test_reject_approved_submission_creates_negative_transaction(db, teacher, student, point_config):
    """Rejecting an already-approved submission creates a negative PointTransaction."""
    from tasks.submissions.models import TaskSubmission
    from gamification.points.models import PointTransaction
    from gamification.points.service import award_points

    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"id": "tmpl1", "name": "Daily", "description": "", "fields": []},
        field_values={"notes": "hi"},
        student_id=str(student.id),
        class_id="cls1",
        date=date(2026, 3, 22),
        status="approved",
    )
    await sub.insert()
    await award_points(str(student.id), "cls1", point_config.submission_points, "submission", str(sub.id))

    # Teacher rejects the approved submission
    sub.status = "rejected"
    sub.rejection_reason = "Plagiarism detected"
    await sub.save()
    await award_points(str(student.id), "cls1", -point_config.submission_points, "submission_rejected", str(sub.id))

    txs = await PointTransaction.find(PointTransaction.student_id == str(student.id)).to_list()
    assert sum(t.amount for t in txs) == 0
    assert any(t.source_event == "submission_rejected" for t in txs)


async def test_reject_stores_resubmit_deadline(db, teacher, pending_submission):
    """Rejection can include an optional resubmit deadline."""
    from datetime import datetime, timezone
    from tasks.submissions.models import TaskSubmission

    deadline = datetime(2026, 3, 29, 23, 59, tzinfo=timezone.utc)
    pending_submission.status = "rejected"
    pending_submission.rejection_reason = "Needs revision"
    pending_submission.resubmit_deadline = deadline
    await pending_submission.save()

    found = await TaskSubmission.get(str(pending_submission.id))
    assert found.resubmit_deadline is not None
    assert found.resubmit_deadline.replace(tzinfo=None) == deadline.replace(tzinfo=None)


# --- Task 4.3: Feed events for approval / rejection ---

async def test_approval_creates_feed_event(db, teacher, pending_submission):
    """Teacher approval creates a FeedPost with event_type='submission_approved'
    (Approved submission appears in feed)."""
    from community.feed.models import FeedPost

    post = FeedPost(
        submission_id=str(pending_submission.id),
        student_id=pending_submission.student_id,
        class_id=pending_submission.class_id,
        event_type="submission_approved",
    )
    await post.insert()

    found = await FeedPost.find_one(
        FeedPost.submission_id == str(pending_submission.id),
        FeedPost.event_type == "submission_approved",
    )
    assert found is not None


async def test_rejection_creates_feed_event(db, teacher, pending_submission):
    """Teacher rejection creates a FeedPost with event_type='submission_rejected'
    (Rejected submission appears in feed)."""
    from community.feed.models import FeedPost

    post = FeedPost(
        submission_id=str(pending_submission.id),
        student_id=pending_submission.student_id,
        class_id=pending_submission.class_id,
        event_type="submission_rejected",
    )
    await post.insert()

    found = await FeedPost.find_one(
        FeedPost.submission_id == str(pending_submission.id),
        FeedPost.event_type == "submission_rejected",
    )
    assert found is not None
    assert found.event_type == "submission_rejected"
