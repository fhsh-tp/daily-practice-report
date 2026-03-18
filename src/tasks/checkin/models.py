"""Checkin Beanie Documents."""
from datetime import date, datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class CheckinConfig(Document):
    """Global check-in schedule for a class. window times stored as 'HH:MM' strings."""
    class_id: str
    active_weekdays: list[int]  # 0=Mon ... 6=Sun
    window_start: Optional[str] = None  # "HH:MM" in UTC, None = all-day
    window_end: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "checkinconfigs"


class DailyCheckinOverride(Document):
    """Per-day override for a class."""
    class_id: str
    date: date
    active: bool
    window_start: Optional[str] = None
    window_end: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "dailycheckinoverrides"


class CheckinRecord(Document):
    """Student check-in record."""
    student_id: str
    class_id: str
    checkin_date: date
    checked_in_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "checkinrecords"
