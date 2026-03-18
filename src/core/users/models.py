"""User Beanie Document."""
from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class User(Document):
    username: str
    hashed_password: str
    display_name: str
    permissions: int = 0
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = True

    class Settings:
        name = "users"
        indexes = ["username"]
