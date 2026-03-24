"""Tests for checkin capability."""
import pytest
from datetime import date, datetime, time, timezone
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_checkin")
    from core.users.models import User
    from core.classes.models import ClassMembership
    from tasks.checkin.models import CheckinConfig, DailyCheckinOverride, CheckinRecord
    await init_beanie(
        database=database,
        document_models=[User, ClassMembership, CheckinConfig, DailyCheckinOverride, CheckinRecord],
    )
    yield database
    client.close()


@pytest.fixture
async def student(db):
    from core.users.models import User
    from core.classes.models import ClassMembership
    from core.auth.password import hash_password
    u = User(username="stu", hashed_password=hash_password("pw"), display_name="S", role="student")
    await u.insert()
    await ClassMembership(class_id="cls1", user_id=str(u.id), role="student").insert()
    return u


# --- Window resolution ---

async def test_is_checkin_open_all_day(db):
    """All-day window (no time restriction) should always be open."""
    from tasks.checkin.service import set_global_config, is_checkin_open
    await set_global_config(
        class_id="cls1",
        active_weekdays=list(range(7)),
        window_start=None,
        window_end=None,
    )
    now = datetime.now(timezone.utc)
    result = await is_checkin_open("cls1", now)
    assert result.is_open is True
    assert result.closes_at is None


async def test_is_checkin_closed_wrong_weekday(db):
    """Check-in closed on excluded weekday."""
    from tasks.checkin.service import set_global_config, is_checkin_open
    # Only Monday (0) is active
    await set_global_config("cls1", active_weekdays=[0], window_start=None, window_end=None)
    # Use a Tuesday (weekday=1) timestamp
    tuesday = datetime(2026, 3, 17, 10, 0, tzinfo=timezone.utc)  # Tuesday
    result = await is_checkin_open("cls1", tuesday)
    assert result.is_open is False


async def test_override_disables_checkin(db):
    """Override with active=False should disable check-in even on active day."""
    from tasks.checkin.service import set_global_config, set_daily_override, is_checkin_open
    await set_global_config("cls1", active_weekdays=list(range(7)), window_start=None, window_end=None)
    target_date = date(2026, 3, 18)
    await set_daily_override("cls1", target_date, active=False)
    wednesday = datetime(2026, 3, 18, 10, 0, tzinfo=timezone.utc)
    result = await is_checkin_open("cls1", wednesday)
    assert result.is_open is False


# --- Check-in recording ---

async def test_checkin_success(db, student):
    """Successful check-in records and returns record."""
    from tasks.checkin.service import set_global_config, do_checkin
    await set_global_config("cls1", active_weekdays=list(range(7)), window_start=None, window_end=None)
    now = datetime(2026, 3, 18, 10, 0, tzinfo=timezone.utc)
    record = await do_checkin(student, "cls1", now)
    assert record.student_id == str(student.id)
    assert record.class_id == "cls1"


async def test_checkin_duplicate_raises(db, student):
    """Second check-in same day raises ValueError."""
    from tasks.checkin.service import set_global_config, do_checkin
    await set_global_config("cls1", active_weekdays=list(range(7)), window_start=None, window_end=None)
    now = datetime(2026, 3, 18, 10, 0, tzinfo=timezone.utc)
    await do_checkin(student, "cls1", now)
    with pytest.raises(ValueError, match="already checked in"):
        await do_checkin(student, "cls1", now)


async def test_checkin_outside_window_raises(db, student):
    """Check-in outside time window raises ValueError."""
    from tasks.checkin.service import set_global_config, do_checkin
    # Window 08:00-09:00 UTC
    await set_global_config(
        "cls1",
        active_weekdays=list(range(7)),
        window_start=time(8, 0),
        window_end=time(9, 0),
    )
    outside = datetime(2026, 3, 18, 12, 0, tzinfo=timezone.utc)  # 12:00 outside window
    with pytest.raises(ValueError, match="not open"):
        await do_checkin(student, "cls1", outside)
