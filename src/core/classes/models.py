"""Class and ClassMembership Beanie Documents."""
from datetime import datetime, timezone
from typing import Literal

from beanie import Document
from pydantic import Field

ClassVisibility = Literal["public", "private"]
MemberRole = Literal["student", "teacher"]


class Class(Document):
    name: str
    description: str = ""
    visibility: ClassVisibility
    owner_id: str
    invite_code: str
    leaderboard_enabled: bool = True
    is_archived: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "classes"


class ClassMembership(Document):
    class_id: str
    user_id: str
    role: MemberRole
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "classmemberships"
