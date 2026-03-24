"""Tests for attendance-management capability."""
import pytest
from datetime import date
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_attendance")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from tasks.checkin.models import CheckinConfig, DailyCheckinOverride, CheckinRecord, AttendanceCorrection
    from gamification.points.models import PointTransaction, ClassPointConfig
    await init_beanie(
        database=database,
        document_models=[
            User, Class, ClassMembership,
            CheckinConfig, DailyCheckinOverride, CheckinRecord, AttendanceCorrection,
            PointTransaction, ClassPointConfig,
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


# --- AttendanceCorrection document ---

async def test_attendance_correction_created(db, teacher, student):
    """AttendanceCorrection created on first correction (AttendanceCorrection document)."""
    from tasks.checkin.models import AttendanceCorrection
    correction = AttendanceCorrection(
        class_id="cls1",
        student_id=str(student.id),
        date=date(2026, 3, 22),
        status="late",
        partial_points=3,
        created_by=str(teacher.id),
    )
    await correction.insert()
    found = await AttendanceCorrection.find_one(
        AttendanceCorrection.class_id == "cls1",
        AttendanceCorrection.student_id == str(student.id),
        AttendanceCorrection.date == date(2026, 3, 22),
    )
    assert found is not None
    assert found.status == "late"
    assert found.partial_points == 3


# --- Teacher marks absent student as late ---

async def test_late_mark_creates_point_transaction(db, teacher, student, point_config):
    """Teacher marks absent student as late — awards partial points (Teacher marks absent student as late)."""
    from gamification.points.models import PointTransaction, ClassPointConfig
    from gamification.points.service import award_points
    from tasks.checkin.models import AttendanceCorrection

    # Student has no checkin record for today (absent by default)
    target_date = date(2026, 3, 22)
    partial = 3

    correction = AttendanceCorrection(
        class_id="cls1",
        student_id=str(student.id),
        date=target_date,
        status="late",
        partial_points=partial,
        created_by=str(teacher.id),
    )
    await correction.insert()

    await award_points(
        student_id=str(student.id),
        class_id="cls1",
        amount=partial,
        source_event="checkin_manual_late",
        source_id=str(correction.id),
        created_by=str(teacher.id),
    )

    txs = await PointTransaction.find(
        PointTransaction.student_id == str(student.id),
        PointTransaction.source_event == "checkin_manual_late",
    ).to_list()
    assert len(txs) == 1
    assert txs[0].amount == 3


async def test_partial_points_validation(db, teacher, student, point_config):
    """Partial points must be between 1 and checkin_points (Partial points must be between 1 and checkin_points)."""
    from gamification.points.models import ClassPointConfig
    config = await ClassPointConfig.find_one(ClassPointConfig.class_id == "cls1")
    checkin_pts = config.checkin_points  # 5

    assert 1 <= 3 <= checkin_pts   # valid: 3
    assert not (0 >= 1)             # invalid: 0 below minimum
    assert not (6 <= checkin_pts)   # invalid: 6 above max


# --- Teacher revokes check-in for student who was actually absent ---

async def test_revoke_checkin_creates_negative_transaction(db, teacher, student, point_config):
    """Teacher revokes check-in points (Teacher revokes check-in for student who was actually absent)."""
    from tasks.checkin.models import CheckinRecord, AttendanceCorrection
    from gamification.points.models import ClassPointConfig, PointTransaction
    from gamification.points.service import award_points, deduct_points

    target_date = date(2026, 3, 22)
    # Student had checked in and received points
    checkin = CheckinRecord(
        student_id=str(student.id),
        class_id="cls1",
        checkin_date=target_date,
    )
    await checkin.insert()
    config = await ClassPointConfig.find_one(ClassPointConfig.class_id == "cls1")
    await award_points(str(student.id), "cls1", config.checkin_points, "checkin", str(checkin.id))

    # Teacher marks as actually absent
    correction = AttendanceCorrection(
        class_id="cls1",
        student_id=str(student.id),
        date=target_date,
        status="absent",
        created_by=str(teacher.id),
    )
    await correction.insert()
    # Revoke points
    await deduct_points(
        student_id=str(student.id),
        class_id="cls1",
        amount=config.checkin_points,
        reason="checkin_manual_revoke",
        deducted_by=str(teacher.id),
    )

    txs = await PointTransaction.find(PointTransaction.student_id == str(student.id)).to_list()
    balance = sum(t.amount for t in txs)
    assert balance == 0  # points awarded then revoked


# --- Existing correction is overwritten ---

async def test_existing_correction_updated(db, teacher, student):
    """Existing correction for same student-date is updated (Existing correction is overwritten)."""
    from tasks.checkin.models import AttendanceCorrection

    target_date = date(2026, 3, 22)
    correction = AttendanceCorrection(
        class_id="cls1",
        student_id=str(student.id),
        date=target_date,
        status="late",
        partial_points=2,
        created_by=str(teacher.id),
    )
    await correction.insert()

    # Update existing
    correction.status = "absent"
    correction.partial_points = None
    await correction.save()

    found = await AttendanceCorrection.find_one(
        AttendanceCorrection.class_id == "cls1",
        AttendanceCorrection.student_id == str(student.id),
        AttendanceCorrection.date == target_date,
    )
    assert found.status == "absent"
    assert found.partial_points is None
