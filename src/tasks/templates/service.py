"""Task template service functions."""
from datetime import date, datetime, timezone
from typing import Any

from tasks.templates.models import FieldDefinition, TaskAssignment, TaskTemplate
from core.users.models import User


async def create_template(
    name: str,
    description: str,
    class_id: str,
    fields: list[dict[str, Any]],
    owner: User,
) -> TaskTemplate:
    """Create a task template with at least one field."""
    if not fields:
        raise ValueError("Template must have at least one field definition")

    parsed_fields = [FieldDefinition(**f) for f in fields]

    tmpl = TaskTemplate(
        name=name,
        description=description,
        class_id=class_id,
        owner_id=str(owner.id),
        fields=parsed_fields,
    )
    await tmpl.insert()
    return tmpl


async def update_template(template_id: str, **kwargs) -> TaskTemplate:
    """Update mutable fields of a task template."""
    tmpl = await TaskTemplate.get(template_id)
    if tmpl is None:
        raise ValueError("Template not found")

    for key, value in kwargs.items():
        if key == "fields":
            setattr(tmpl, key, [FieldDefinition(**f) for f in value])
        elif hasattr(tmpl, key):
            setattr(tmpl, key, value)

    tmpl.updated_at = datetime.now(timezone.utc)
    await tmpl.save()
    return tmpl


async def delete_template(template_id: str) -> None:
    """
    Delete a template.
    Raises ValueError if submissions already reference this template.
    """
    # Import here to avoid circular imports
    from tasks.submissions.models import TaskSubmission
    has_submissions = await TaskSubmission.find_one(
        TaskSubmission.template_id == template_id
    )
    if has_submissions:
        raise ValueError("Cannot delete template with existing submissions")

    tmpl = await TaskTemplate.get(template_id)
    if tmpl:
        await tmpl.delete()


async def assign_template_to_date(
    template_id: str,
    class_id: str,
    target_date: date,
) -> TaskAssignment:
    """Assign a template to a specific date for a class (upsert)."""
    existing = await TaskAssignment.find_one(
        TaskAssignment.class_id == class_id,
        TaskAssignment.date == target_date,
    )
    if existing:
        existing.template_id = template_id
        await existing.save()
        return existing

    assignment = TaskAssignment(
        template_id=template_id,
        class_id=class_id,
        date=target_date,
    )
    await assignment.insert()
    return assignment


async def get_template_for_date(
    class_id: str,
    target_date: date,
) -> TaskTemplate | None:
    """Return the active (non-archived) template assigned to a class for the given date, or None."""
    assignment = await TaskAssignment.find_one(
        TaskAssignment.class_id == class_id,
        TaskAssignment.date == target_date,
    )
    if assignment is None:
        return None
    tmpl = await TaskTemplate.get(assignment.template_id)
    if tmpl is None or tmpl.is_archived:
        return None
    return tmpl


async def archive_template(template_id: str) -> TaskTemplate:
    """Mark a template as archived (soft-hide from students)."""
    tmpl = await TaskTemplate.get(template_id)
    if tmpl is None:
        raise ValueError("Template not found")
    tmpl.is_archived = True
    tmpl.updated_at = datetime.now(timezone.utc)
    await tmpl.save()
    return tmpl


async def unarchive_template(template_id: str) -> TaskTemplate:
    """Restore an archived template to active status."""
    tmpl = await TaskTemplate.get(template_id)
    if tmpl is None:
        raise ValueError("Template not found")
    tmpl.is_archived = False
    tmpl.updated_at = datetime.now(timezone.utc)
    await tmpl.save()
    return tmpl
