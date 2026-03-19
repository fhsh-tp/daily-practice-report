"""Classes router."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user
from core.auth.guards import require_permission
from core.auth.permissions import MANAGE_OWN_CLASS, MANAGE_ALL_CLASSES, READ_CLASS
from core.classes.models import Class, ClassMembership
from core.classes.service import (
    batch_invite_students,
    can_manage_class,
    create_class,
    get_class_members,
    get_public_classes,
    join_class_by_code,
    join_class_by_id,
    promote_to_teacher,
    regenerate_invite_code,
    remove_member,
    search_students_for_invite,
    set_visibility,
)
from core.users.models import User

router = APIRouter(prefix="/classes", tags=["classes"])

_CAN_CREATE_CLASS = MANAGE_OWN_CLASS | MANAGE_ALL_CLASSES


async def _require_manage(class_id: str, user: User) -> Class:
    """Load class and assert user can manage it; raises 403 if not authorised."""
    cls = await Class.get(class_id)
    if cls is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
    if not await can_manage_class(user, cls):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return cls


class CreateClassRequest(BaseModel):
    name: str
    description: str = ""
    visibility: str = "public"


class JoinByCodeRequest(BaseModel):
    invite_code: str


class SetVisibilityRequest(BaseModel):
    visibility: str


class BatchInviteRequest(BaseModel):
    user_ids: list[str]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_class_endpoint(
    body: CreateClassRequest,
    teacher: User = Depends(require_permission(_CAN_CREATE_CLASS)),
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
    user: User = Depends(get_current_user),
):
    cls = await _require_manage(class_id, user)
    try:
        cls = await set_visibility(class_id, body.visibility)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"id": str(cls.id), "visibility": cls.visibility}


@router.get("/{class_id}/members")
async def list_members(class_id: str, user: User = Depends(get_current_user)):
    await _require_manage(class_id, user)
    members = await get_class_members(class_id)
    return [{"user_id": m.user_id, "role": m.role} for m in members]


@router.delete("/{class_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_class_member(
    class_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
):
    await _require_manage(class_id, user)
    await remove_member(class_id, user_id)


@router.patch("/{class_id}/members/{user_id}/promote")
async def promote_member(
    class_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
):
    await _require_manage(class_id, user)
    try:
        m = await promote_to_teacher(class_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"user_id": m.user_id, "role": m.role}


@router.post("/{class_id}/invite-code/regenerate")
async def regen_invite_code(class_id: str, user: User = Depends(get_current_user)):
    await _require_manage(class_id, user)
    try:
        new_code = await regenerate_invite_code(class_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"invite_code": new_code}


@router.get("/{class_id}/invite/search")
async def search_invite_students(
    class_id: str,
    q: str = "",
    type: str = "name",
    user: User = Depends(get_current_user),
):
    """Search for students not yet in this class (by name or admin class_name)."""
    await _require_manage(class_id, user)
    results = await search_students_for_invite(class_id, q=q, search_type=type)
    return results


@router.post("/{class_id}/invite/batch", status_code=status.HTTP_201_CREATED)
async def batch_invite(
    class_id: str,
    body: BatchInviteRequest,
    user: User = Depends(get_current_user),
):
    """Directly add a list of users to the class as students."""
    await _require_manage(class_id, user)
    added = await batch_invite_students(class_id, body.user_ids)
    return {"added": added}
