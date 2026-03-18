"""Badges router."""
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from core.auth.deps import get_current_user
from core.auth.guards import require_permission
from core.auth.permissions import MANAGE_TASKS
from core.users.models import User
from gamification.badges.models import BadgeAward, BadgeDefinition
from gamification.badges.service import award_badge, get_student_badges

router = APIRouter(tags=["badges"])

_templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent.parent.parent / "templates")
)


class BadgeCreateRequest(BaseModel):
    name: str
    description: str
    icon: str = "🏅"
    trigger_key: Optional[str] = None


class ManualAwardRequest(BaseModel):
    student_id: str
    reason: Optional[str] = None


@router.post("/classes/{class_id}/badges", status_code=status.HTTP_201_CREATED)
async def create_badge(
    class_id: str,
    body: BadgeCreateRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    badge = BadgeDefinition(
        class_id=class_id,
        name=body.name,
        description=body.description,
        icon=body.icon,
        trigger_key=body.trigger_key,
        created_by=str(teacher.id),
    )
    await badge.insert()
    return {"id": str(badge.id), "name": badge.name}


@router.post("/classes/{class_id}/badges/{badge_id}/award")
async def manual_award_badge(
    class_id: str,
    badge_id: str,
    body: ManualAwardRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    badge = await BadgeDefinition.get(badge_id)
    if badge is None or badge.class_id != class_id:
        raise HTTPException(status_code=404, detail="Badge not found")

    award = await award_badge(
        badge_id=badge_id,
        student_id=body.student_id,
        class_id=class_id,
        awarded_by=str(teacher.id),
        reason=body.reason,
    )
    if award is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already holds this badge",
        )
    return {"awarded": True, "award_id": str(award.id)}


@router.get("/students/me/badges")
async def my_badges(user: User = Depends(get_current_user)):
    badges = await get_student_badges(str(user.id))
    return [
        {
            "badge_id": item["award"].badge_id,
            "name": item["definition"].name if item["definition"] else "Unknown",
            "icon": item["definition"].icon if item["definition"] else "🏅",
            "description": item["definition"].description if item["definition"] else "",
            "awarded_at": item["award"].awarded_at.isoformat(),
            "reason": item["award"].reason,
        }
        for item in badges
    ]


@router.get("/pages/students/me/badges")
async def badges_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    badges = await get_student_badges(str(user.id))
    return _templates.TemplateResponse("student/badges.html", {
        "request": request,
        "current_user": user,
        "badges": badges,
    })
