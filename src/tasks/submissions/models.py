"""TaskSubmission Beanie Document."""
from datetime import date, datetime, timezone
from typing import Any

from beanie import Document
from pydantic import Field


class TaskSubmission(Document):
    template_id: str
    template_snapshot: dict[str, Any]  # snapshot of template at submission time
    field_values: dict[str, Any]  # field_name -> submitted value
    student_id: str
    class_id: str
    date: date
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "tasksubmissions"
