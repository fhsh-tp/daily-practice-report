"""Task submissions router."""
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user, require_teacher
from core.users.models import User
from extensions.deps import get_reward_providers, get_submission_validators
from extensions.protocols.reward import RewardEvent, RewardEventType
from extensions.protocols.validator import ValidationResult
from tasks.submissions.service import (
    get_class_submissions_for_date,
    get_student_submissions,
    submit_task,
)
from tasks.templates.models import TaskTemplate

router = APIRouter(tags=["submissions"])


class SubmitRequest(BaseModel):
    field_values: dict[str, Any]
    submission_date: date | None = None


@router.post("/classes/{class_id}/submissions", status_code=status.HTTP_201_CREATED)
async def submit_task_endpoint(
    class_id: str,
    body: SubmitRequest,
    user: User = Depends(get_current_user),
):
    # Get today's template for this class
    target_date = body.submission_date or date.today()
    from tasks.templates.service import get_template_for_date
    template = await get_template_for_date(class_id, target_date)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No task template assigned for today",
        )

    # Run SubmissionValidators
    validators = get_submission_validators()
    for validator in validators:
        result: ValidationResult = await validator.validate(body.field_values, template)
        if not result.valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error_message,
            )

    try:
        submission = await submit_task(
            template=template,
            class_id=class_id,
            student=user,
            submission_date=target_date,
            field_values=body.field_values,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    # Trigger RewardProviders
    event = RewardEvent(
        event_type=RewardEventType.SUBMISSION,
        student_id=str(user.id),
        class_id=class_id,
        source_id=str(submission.id),
    )
    for provider in get_reward_providers():
        await provider.award(event)

    # Evaluate BadgeTriggers
    from gamification.badges.service import evaluate_triggers_for_event
    await evaluate_triggers_for_event(str(user.id), event, class_id)

    return {"id": str(submission.id), "date": str(submission.date)}


@router.get("/students/me/submissions")
async def my_submissions(user: User = Depends(get_current_user)):
    subs = await get_student_submissions(str(user.id))
    return [
        {
            "id": str(s.id),
            "date": str(s.date),
            "template_name": s.template_snapshot.get("name"),
            "field_values": s.field_values,
        }
        for s in subs
    ]


@router.get("/classes/{class_id}/submissions")
async def class_submissions(
    class_id: str,
    date_param: date | None = None,
    teacher: User = Depends(require_teacher()),
):
    target = date_param or date.today()
    subs = await get_class_submissions_for_date(class_id, target)
    return [
        {
            "id": str(s.id),
            "student_id": s.student_id,
            "date": str(s.date),
            "field_values": s.field_values,
        }
        for s in subs
    ]
