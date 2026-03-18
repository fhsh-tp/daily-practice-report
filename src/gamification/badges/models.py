"""Badge system Beanie Documents."""
from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class BadgeDefinition(Document):
    """A badge that can be awarded to students."""
    class_id: str
    name: str
    description: str
    icon: str = "🏅"
    trigger_key: Optional[str] = None  # key into ExtensionRegistry; None = manual only
    created_by: str  # teacher user_id

    class Settings:
        name = "badgedefinitions"


class BadgeAward(Document):
    """Records a badge awarded to a student."""
    badge_id: str
    student_id: str
    class_id: str
    awarded_by: str = "system"  # "system" or teacher user_id
    reason: Optional[str] = None
    awarded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "badgeawards"
