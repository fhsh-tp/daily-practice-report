"""Community feed Beanie Documents."""
from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class FeedPost(Document):
    """A shared submission post on the class feed."""
    submission_id: str
    student_id: str
    class_id: str
    content_preview: str = ""  # short excerpt from submission
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "feedposts"


class Reaction(Document):
    """A reaction (emoji) on a feed post."""
    post_id: str
    user_id: str
    emoji: str = "👍"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reactions"
