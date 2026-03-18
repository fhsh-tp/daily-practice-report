"""TaskTemplate and TaskAssignment Beanie Documents."""
from datetime import date, datetime, timezone
from typing import Literal

from beanie import Document
from pydantic import BaseModel, Field

FieldType = Literal["text", "markdown", "number", "checkbox"]


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
