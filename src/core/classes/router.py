"""Classes router."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user
from core.auth.guards import require_permission
from core.auth.permissions import MANAGE_CLASS
from core.classes.models import Class, ClassMembership
from core.classes.service import (
    create_class,
    get_class_members,
    get_public_classes,
    join_class_by_code,
    join_class_by_id,
    promote_to_teacher,
    regenerate_invite_code,
    remove_member,
    set_visibility,
)
from core.users.models import User

router = APIRouter(prefix="/classes", tags=["classes"])


class CreateClassRequest(BaseModel):
    name: str
    description: str = ""
    visibility: str = "public"


class JoinByCodeRequest(BaseModel):
    invite_code: str


class SetVisibilityRequest(BaseModel):
    visibility: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_class_endpoint(
    body: CreateClassRequest,
    teacher: User = Depends(require_permission(MANAGE_CLASS)),
):
    cls = await create_class(body.name, body.description, body.visibility, teacher)
    return {"id": str(cls.id), "name": cls.name, "invite_code": cls.invite_code}


@router.get("/public")
async def list_public_classes(_: User = Depends(get_current_user)):
    classes = await get_public_classes()
    return [{"id": str(c.id), "name": c.name, "description": c.description} for c in classes]


@router.post("/join")
async def join_by_code(body: JoinByCodeRequest, user: User = Depends(get_current_user)):
    try:
        m = await join_class_by_code(user, body.invite_code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"class_id": m.class_id, "message": "Joined class"}


@router.post("/{class_id}/join")
async def join_public_class(class_id: str, user: User = Depends(get_current_user)):
    try:
        m = await join_class_by_id(user, class_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"class_id": m.class_id, "message": "Joined class"}


@router.patch("/{class_id}/visibility")
async def update_visibility(
    class_id: str,
    body: SetVisibilityRequest,
    teacher: User = Depends(require_permission(MANAGE_CLASS)),
):
    try:
        cls = await set_visibility(class_id, body.visibility)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"id": str(cls.id), "visibility": cls.visibility}


@router.get("/{class_id}/members")
async def list_members(class_id: str, teacher: User = Depends(require_permission(MANAGE_CLASS))):
    members = await get_class_members(class_id)
    return [{"user_id": m.user_id, "role": m.role} for m in members]


@router.delete("/{class_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_class_member(
    class_id: str,
    user_id: str,
    teacher: User = Depends(require_permission(MANAGE_CLASS)),
):
    await remove_member(class_id, user_id)


@router.patch("/{class_id}/members/{user_id}/promote")
async def promote_member(
    class_id: str,
    user_id: str,
    teacher: User = Depends(require_permission(MANAGE_CLASS)),
):
    try:
        m = await promote_to_teacher(class_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"user_id": m.user_id, "role": m.role}


@router.post("/{class_id}/invite-code/regenerate")
async def regen_invite_code(class_id: str, teacher: User = Depends(require_permission(MANAGE_CLASS))):
    try:
        new_code = await regenerate_invite_code(class_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"invite_code": new_code}
