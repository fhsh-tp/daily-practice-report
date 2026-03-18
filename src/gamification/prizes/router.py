"""Prizes router."""
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user
from core.auth.guards import require_permission
from core.auth.permissions import MANAGE_TASKS
from core.users.models import User
from gamification.prizes.models import Prize

router = APIRouter(tags=["prizes"])


class PrizeCreateRequest(BaseModel):
    title: str
    description: str = ""
    prize_type: Literal["online", "physical"] = "online"
    image_url: Optional[str] = None
    point_cost: int = 0
    visible: bool = True


class PrizePatchRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prize_type: Optional[Literal["online", "physical"]] = None
    image_url: Optional[str] = None
    point_cost: Optional[int] = None
    visible: Optional[bool] = None


@router.post("/classes/{class_id}/prizes", status_code=status.HTTP_201_CREATED)
async def create_prize(
    class_id: str,
    body: PrizeCreateRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    prize = Prize(
        class_id=class_id,
        title=body.title,
        description=body.description,
        prize_type=body.prize_type,
        image_url=body.image_url,
        point_cost=body.point_cost,
        visible=body.visible,
        created_by=str(teacher.id),
    )
    await prize.insert()
    return {"id": str(prize.id), "title": prize.title}


@router.get("/classes/{class_id}/prizes")
async def list_prizes(
    class_id: str,
    user: User = Depends(get_current_user),
):
    if user.role == "student":
        prizes = await Prize.find(Prize.class_id == class_id, Prize.visible == True).to_list()  # noqa: E712
    else:
        prizes = await Prize.find(Prize.class_id == class_id).to_list()
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "description": p.description,
            "prize_type": p.prize_type,
            "image_url": p.image_url,
            "point_cost": p.point_cost,
            "visible": p.visible,
        }
        for p in prizes
    ]


@router.patch("/prizes/{prize_id}")
async def update_prize(
    prize_id: str,
    body: PrizePatchRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    prize = await Prize.get(prize_id)
    if prize is None:
        raise HTTPException(status_code=404, detail="Prize not found")

    updates = body.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(prize, field, value)
    await prize.save()
    return {"id": str(prize.id), "visible": prize.visible}


@router.delete("/prizes/{prize_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prize(
    prize_id: str,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    prize = await Prize.get(prize_id)
    if prize is None:
        raise HTTPException(status_code=404, detail="Prize not found")
    await prize.delete()
