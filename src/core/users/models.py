"""User Beanie Document."""
from datetime import datetime, timezone
from typing import Literal

from beanie import Document
from pydantic import Field


UserRole = Literal["student", "teacher"]


class User(Document):
    username: str
    hashed_password: str
    display_name: str
    role: UserRole
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = True

    class Settings:
        name = "users"
        indexes = ["username"]
