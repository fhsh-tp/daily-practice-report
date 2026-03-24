"""Check-in service functions."""
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Optional

from tasks.checkin.models import CheckinConfig, CheckinRecord, DailyCheckinOverride
from core.users.models import User


class MembershipError(ValueError):
    """Raised when the student is not a member of the target class."""


@dataclass
class CheckinStatus:
    is_open: bool
    closes_at: Optional[datetime]
    reason: str = ""


def _parse_time(t: Optional[str]) -> Optional[time]:
    """Parse 'HH:MM' string to time object, return None if None."""
    if t is None:
        return None
    h, m = t.split(":")
    return time(int(h), int(m))


def _time_to_str(t: Optional[time]) -> Optional[str]:
    """Convert time to 'HH:MM' string."""
    if t is None:
        return None
    return f"{t.hour:02d}:{t.minute:02d}"


def _time_in_window(
    current_time: datetime,
    window_start: Optional[str],
    window_end: Optional[str],
) -> bool:
    """Check if current time is within a time window."""
    if window_start is None or window_end is None:
        return True  # all-day
    t = current_time.time().replace(second=0, microsecond=0, tzinfo=None)
    start = _parse_time(window_start)
    end = _parse_time(window_end)
    return start <= t <= end


async def set_global_config(
    class_id: str,
    active_weekdays: list[int],
    window_start: Optional[time],
    window_end: Optional[time],
) -> CheckinConfig:
    """Create or update the global check-in config for a class."""
    existing = await CheckinConfig.find_one(CheckinConfig.class_id == class_id)
    ws = _time_to_str(window_start)
    we = _time_to_str(window_end)
    if existing:
        existing.active_weekdays = active_weekdays
        existing.window_start = ws
        existing.window_end = we
        await existing.save()
        return existing
    config = CheckinConfig(
        class_id=class_id,
        active_weekdays=active_weekdays,
        window_start=ws,
        window_end=we,
    )
    await config.insert()
    return config


async def set_daily_override(
    class_id: str,
    target_date: date,
    active: bool,
    window_start: Optional[time] = None,
    window_end: Optional[time] = None,
) -> DailyCheckinOverride:
    """Create or update a per-day override for a class."""
    existing = await DailyCheckinOverride.find_one(
        DailyCheckinOverride.class_id == class_id,
        DailyCheckinOverride.date == target_date,
    )
    ws = _time_to_str(window_start)
    we = _time_to_str(window_end)
    if existing:
        existing.active = active
        existing.window_start = ws
        existing.window_end = we
        await existing.save()
        return existing
    override = DailyCheckinOverride(
        class_id=class_id,
        date=target_date,
        active=active,
        window_start=ws,
        window_end=we,
    )
    await override.insert()
    return override


def _build_closes_at(now: datetime, window_end: Optional[str]) -> Optional[datetime]:
    if window_end is None:
        return None
    t = _parse_time(window_end)
    return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)


async def is_checkin_open(class_id: str, now: datetime) -> CheckinStatus:
    """
    Determine if check-in is currently open for a class.
    Per-day override takes precedence over global config.
    """
    today = now.date()
    weekday = today.weekday()

    # Check per-day override first
    override = await DailyCheckinOverride.find_one(
        DailyCheckinOverride.class_id == class_id,
        DailyCheckinOverride.date == today,
    )
    if override is not None:
        if not override.active:
            return CheckinStatus(is_open=False, closes_at=None, reason="disabled by override")
        in_window = _time_in_window(now, override.window_start, override.window_end)
        closes_at = _build_closes_at(now, override.window_end)
        if not in_window:
            return CheckinStatus(is_open=False, closes_at=closes_at, reason="outside override window")
        return CheckinStatus(is_open=True, closes_at=closes_at)

    # Fall back to global config
    config = await CheckinConfig.find_one(CheckinConfig.class_id == class_id)
    if config is None:
        return CheckinStatus(is_open=False, closes_at=None, reason="no config set")

    if weekday not in config.active_weekdays:
        return CheckinStatus(is_open=False, closes_at=None, reason="not an active weekday")

    in_window = _time_in_window(now, config.window_start, config.window_end)
    closes_at = _build_closes_at(now, config.window_end)
    if not in_window:
        return CheckinStatus(is_open=False, closes_at=closes_at, reason="outside time window")
    return CheckinStatus(is_open=True, closes_at=closes_at)


async def do_checkin(
    student: User,
    class_id: str,
    now: datetime,
) -> CheckinRecord:
    """
    Record a student check-in.

    Raises:
        MembershipError: If the student is not a member of the class.
        ValueError: If check-in window is not open or student already checked in today.
    """
    # Verify class membership — prevents non-members from checking in
    from core.classes.models import ClassMembership
    membership = await ClassMembership.find_one(
        ClassMembership.class_id == class_id,
        ClassMembership.user_id == str(student.id),
    )
    if not membership:
        raise MembershipError("Not a member of this class")

    status = await is_checkin_open(class_id, now)
    if not status.is_open:
        raise ValueError(f"Check-in is not open: {status.reason}")

    today = now.date()
    existing = await CheckinRecord.find_one(
        CheckinRecord.student_id == str(student.id),
        CheckinRecord.class_id == class_id,
        CheckinRecord.checkin_date == today,
    )
    if existing:
        raise ValueError("Student has already checked in today")

    record = CheckinRecord(
        student_id=str(student.id),
        class_id=class_id,
        checkin_date=today,
        checked_in_at=now,
    )
    await record.insert()
    return record
