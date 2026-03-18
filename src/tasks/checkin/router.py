"""Check-in router."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user
from core.auth.guards import require_permission
from core.auth.permissions import MANAGE_CLASS
from core.users.models import User
from extensions.deps import get_reward_providers
from extensions.protocols.reward import RewardEvent, RewardEventType
from tasks.checkin.service import (
    do_checkin,
    is_checkin_open,
    set_daily_override,
    set_global_config,
)

router = APIRouter(tags=["checkin"])


class GlobalConfigRequest(BaseModel):
    active_weekdays: list[int]
    window_start: Optional[str] = None  # "HH:MM"
    window_end: Optional[str] = None


class OverrideRequest(BaseModel):
    date: str  # "YYYY-MM-DD"
    active: bool
    window_start: Optional[str] = None
    window_end: Optional[str] = None


@router.post("/classes/{class_id}/checkin-config")
async def configure_checkin(
    class_id: str,
    body: GlobalConfigRequest,
    teacher: User = Depends(require_permission(MANAGE_CLASS)),
):
    from datetime import time as dt_time
    ws = None
    we = None
    if body.window_start:
        h, m = body.window_start.split(":")
        ws = dt_time(int(h), int(m))
    if body.window_end:
        h, m = body.window_end.split(":")
        we = dt_time(int(h), int(m))
    config = await set_global_config(class_id, body.active_weekdays, ws, we)
    return {"class_id": class_id, "active_weekdays": config.active_weekdays}


@router.post("/classes/{class_id}/checkin-overrides")
async def create_override(
    class_id: str,
    body: OverrideRequest,
    teacher: User = Depends(require_permission(MANAGE_CLASS)),
):
    from datetime import date, time as dt_time
    target_date = date.fromisoformat(body.date)
    ws = None
    we = None
    if body.window_start:
        h, m = body.window_start.split(":")
        ws = dt_time(int(h), int(m))
    if body.window_end:
        h, m = body.window_end.split(":")
        we = dt_time(int(h), int(m))
    override = await set_daily_override(class_id, target_date, body.active, ws, we)
    return {"date": str(override.date), "active": override.active}


@router.post("/classes/{class_id}/checkin", status_code=status.HTTP_201_CREATED)
async def checkin(class_id: str, user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    try:
        record = await do_checkin(user, class_id, now)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    # Trigger RewardProviders
    event = RewardEvent(
        event_type=RewardEventType.CHECKIN,
        student_id=str(user.id),
        class_id=class_id,
        source_id=str(record.id),
    )
    for provider in get_reward_providers():
        await provider.award(event)

    # Evaluate BadgeTriggers
    from gamification.badges.service import evaluate_triggers_for_event
    await evaluate_triggers_for_event(str(user.id), event, class_id)

    return {"checked_in_at": record.checked_in_at.isoformat()}


@router.get("/classes/{class_id}/checkin-status")
async def checkin_status(class_id: str, user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    result = await is_checkin_open(class_id, now)

    # Check if student already checked in today
    from tasks.checkin.models import CheckinRecord
    existing = await CheckinRecord.find_one(
        CheckinRecord.student_id == str(user.id),
        CheckinRecord.class_id == class_id,
        CheckinRecord.checkin_date == now.date(),
    )

    return {
        "is_open": result.is_open,
        "closes_at": result.closes_at.isoformat() if result.closes_at else None,
        "already_checked_in": existing is not None,
        "reason": result.reason,
    }
