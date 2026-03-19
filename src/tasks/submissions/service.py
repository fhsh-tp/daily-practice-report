"""Task submission service functions."""
from datetime import date
from typing import Any

from tasks.submissions.models import TaskSubmission
from tasks.templates.models import TaskTemplate
from core.users.models import User


def _validate_field_values(
    template: TaskTemplate,
    field_values: dict[str, Any],
) -> None:
    """
    Validate submitted field values against the template.

    Raises:
        ValueError: If a required field is missing or a number field has non-numeric value.
    """
    field_map = {f.name: f for f in template.fields}

    # Check required fields
    for field in template.fields:
        if field.required and (field.name not in field_values or field_values[field.name] in (None, "")):
            raise ValueError(f"Field '{field.name}' is required")

    # Type validation for submitted fields
    for name, value in field_values.items():
        if name not in field_map:
            continue
        field = field_map[name]
        if field.field_type == "number" and value not in (None, ""):
            try:
                float(value)
            except (TypeError, ValueError):
                raise ValueError(f"Field '{name}' must be a number, got {value!r}")


async def submit_task(
    template: TaskTemplate,
    class_id: str,
    student: User,
    submission_date: date,
    field_values: dict[str, Any],
) -> TaskSubmission:
    """
    Submit a daily task for a student.

    Raises:
        ValueError: If already submitted or required fields are missing.
    """
    # Check per-student submission limit from associated schedule rule
    from tasks.templates.models import TaskScheduleRule
    rule = await TaskScheduleRule.find_one(
        TaskScheduleRule.template_id == str(template.id),
        TaskScheduleRule.class_id == class_id,
    )
    if rule and rule.max_submissions_per_student > 0:
        existing_count = await TaskSubmission.find(
            TaskSubmission.template_id == str(template.id),
            TaskSubmission.student_id == str(student.id),
            TaskSubmission.class_id == class_id,
        ).count()
        if existing_count >= rule.max_submissions_per_student:
            raise ValueError(
                f"Submission limit reached: max {rule.max_submissions_per_student} per student"
            )

    # Check for duplicate
    existing = await TaskSubmission.find_one(
        TaskSubmission.template_id == str(template.id),
        TaskSubmission.student_id == str(student.id),
        TaskSubmission.date == submission_date,
    )
    if existing:
        raise ValueError("Student has already submitted for this template on this date")

    # Validate fields
    _validate_field_values(template, field_values)

    # Build template snapshot
    snapshot = {
        "id": str(template.id),
        "name": template.name,
        "description": template.description,
        "fields": [f.model_dump() for f in template.fields],
    }

    submission = TaskSubmission(
        template_id=str(template.id),
        template_snapshot=snapshot,
        field_values=field_values,
        student_id=str(student.id),
        class_id=class_id,
        date=submission_date,
    )
    await submission.insert()
    return submission


async def get_student_submissions(student_id: str) -> list[TaskSubmission]:
    """Return all submissions for a student in reverse chronological order."""
    return await TaskSubmission.find(
        TaskSubmission.student_id == student_id
    ).sort(-TaskSubmission.date).to_list()


async def get_class_submissions_for_date(
    class_id: str,
    target_date: date,
) -> list[TaskSubmission]:
    """Return all submissions for a class on a given date."""
    return await TaskSubmission.find(
        TaskSubmission.class_id == class_id,
        TaskSubmission.date == target_date,
    ).to_list()
