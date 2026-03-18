"""Points system Beanie Documents."""
from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class PointTransaction(Document):
    student_id: str
    class_id: str
    amount: int  # positive = award, negative = revoke
    reason: str
    source_event: str  # "checkin" | "submission" | "manual_revoke" | etc.
    source_id: str   # reference to the triggering record
    created_by: str = "system"  # user_id or "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "pointtransactions"


class ClassPointConfig(Document):
    """Per-class point award configuration."""
    class_id: str
    checkin_points: int = 5
    submission_points: int = 10

    class Settings:
        name = "classpointconfigs"
