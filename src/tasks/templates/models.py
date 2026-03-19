"""TaskTemplate and TaskAssignment Beanie Documents."""
from datetime import date, datetime, timezone
from typing import Literal, Optional

from beanie import Document
from pydantic import BaseModel, Field

FieldType = Literal["text", "markdown", "number", "checkbox"]
ScheduleType = Literal["once", "range", "open"]
_DateField = date  # module-level alias — prevents 'date' field from shadowing the type


class FieldDefinition(BaseModel):
    name: str
    field_type: FieldType
    required: bool = False


class TaskTemplate(Document):
    name: str
    description: str = ""
    class_id: str
    owner_id: str
    fields: list[FieldDefinition]
    is_archived: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "tasktemplates"


class TaskAssignment(Document):
    template_id: str
    class_id: str
    date: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "taskassignments"


class TaskScheduleRule(Document):
    """Scheduling rule that batch-creates TaskAssignment records on save."""
    template_id: str
    class_id: str
    schedule_type: ScheduleType
    start_date: Optional[date] = None    # range/open mode (evaluated before 'date' shadows)
    end_date: Optional[date] = None      # range mode (open: None)
    date: Optional[_DateField] = None    # once mode; _DateField alias avoids self-shadowing
    weekdays: list[int] = Field(default_factory=list)  # [] = every day
    max_submissions_per_student: int = 0  # 0 = no limit
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "taskschedulerules"
