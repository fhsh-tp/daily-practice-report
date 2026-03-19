"""Task templates router."""
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user
from core.auth.guards import require_permission
from core.auth.permissions import MANAGE_TASKS
from core.users.models import User
from tasks.templates.service import (
    assign_template_to_date,
    create_template,
    delete_template,
    get_template_for_date,
    update_template,
)

router = APIRouter(tags=["templates"])


class FieldDef(BaseModel):
    name: str
    field_type: str
    required: bool = False


class CreateTemplateRequest(BaseModel):
    name: str
    description: str = ""
    fields: list[FieldDef]


class AssignTemplateRequest(BaseModel):
    template_id: str
    date: date


class UpdateTemplateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    fields: list[FieldDef] | None = None


@router.post("/classes/{class_id}/templates", status_code=status.HTTP_201_CREATED)
async def create_template_endpoint(
    class_id: str,
    body: CreateTemplateRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    try:
        tmpl = await create_template(
            name=body.name,
            description=body.description,
            class_id=class_id,
            fields=[f.model_dump() for f in body.fields],
            owner=teacher,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return {"id": str(tmpl.id), "name": tmpl.name}


@router.post("/classes/{class_id}/template-assignments", status_code=status.HTTP_201_CREATED)
async def assign_template(
    class_id: str,
    body: AssignTemplateRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    assignment = await assign_template_to_date(body.template_id, class_id, body.date)
    return {"template_id": assignment.template_id, "date": str(assignment.date)}


@router.get("/classes/{class_id}/today-template")
async def today_template(class_id: str, user: User = Depends(get_current_user)):
    tmpl = await get_template_for_date(class_id, date.today())
    if tmpl is None:
        return {"message": "No task available today"}
    return {
        "id": str(tmpl.id),
        "name": tmpl.name,
        "description": tmpl.description,
        "fields": [f.model_dump() for f in tmpl.fields],
    }


@router.patch("/templates/{template_id}")
async def update_template_endpoint(
    template_id: str,
    body: UpdateTemplateRequest,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if "fields" in updates:
        updates["fields"] = [f.model_dump() for f in body.fields]
    try:
        tmpl = await update_template(template_id, **updates)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"id": str(tmpl.id), "name": tmpl.name}


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template_endpoint(
    template_id: str,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    try:
        await delete_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


from fastapi import Request
from pages.deps import get_page_user
from shared.webpage import webpage


@router.get("/pages/teacher/classes/{class_id}/members", name="class_members_page")
@webpage.page("teacher/class_members.html")
async def class_members_page(
    request: Request,
    class_id: str,
    teacher: User = Depends(get_page_user),
):
    from core.auth.permissions import MANAGE_OWN_CLASS, MANAGE_ALL_CLASSES
    from core.classes.models import Class, ClassMembership
    from core.classes.service import can_manage_class
    from core.users.models import User as UserModel
    from fastapi import HTTPException, status as http_status

    if not (teacher.permissions & (MANAGE_OWN_CLASS | MANAGE_ALL_CLASSES)):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Permission denied")
    cls = await Class.get(class_id)
    if cls is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Class not found")
    if not await can_manage_class(teacher, cls):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Permission denied")

    memberships = await ClassMembership.find(ClassMembership.class_id == class_id).to_list()
    members = []
    for m in memberships:
        u = await UserModel.get(m.user_id)
        members.append({
            "user_id": m.user_id,
            "username": u.username if u else m.user_id,
            "display_name": u.display_name if u else m.user_id,
            "role": m.role,
        })
    return {
        "current_user": teacher,
        "class_id": class_id,
        "class_name": cls.name,
        "invite_code": cls.invite_code,
        "is_archived": cls.is_archived,
        "members": members,
    }


@router.get("/pages/teacher/classes/{class_id}/templates", name="templates_list_page")
@webpage.page("teacher/templates_list.html")
async def templates_list_page(
    request: Request,
    class_id: str,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    from tasks.templates.models import TaskTemplate as TT
    templates = await TT.find(TT.class_id == class_id).to_list()
    from core.classes.models import Class
    cls = await Class.get(class_id)
    class_name = cls.name if cls else class_id
    return {"current_user": teacher, "class_id": class_id, "class_name": class_name, "templates": templates}


@router.get("/pages/teacher/classes/{class_id}/templates/new", name="template_form_page")
@webpage.page("teacher/template_form.html")
async def template_form_page(
    request: Request,
    class_id: str,
    error: str | None = None,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    return {"current_user": teacher, "class_id": class_id, "template": None, "error": error}


@router.get("/pages/teacher/templates/{template_id}/edit", name="template_edit_page")
@webpage.page("teacher/template_form.html")
async def template_edit_page(
    request: Request,
    template_id: str,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    from tasks.templates.models import TaskTemplate as TT
    tmpl = await TT.get(template_id)
    if tmpl is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"current_user": teacher, "class_id": tmpl.class_id, "template": tmpl, "error": None}


@router.get("/pages/teacher/templates/{template_id}/assign", name="template_assign_page")
@webpage.page("teacher/template_assign.html")
async def template_assign_page(
    request: Request,
    template_id: str,
    teacher: User = Depends(require_permission(MANAGE_TASKS)),
):
    from tasks.templates.models import TaskTemplate as TT
    tmpl = await TT.get(template_id)
    if tmpl is None:
        raise HTTPException(status_code=404, detail="Template not found")
    from core.classes.models import Class
    cls = await Class.get(tmpl.class_id)
    class_name = cls.name if cls else tmpl.class_id
    return {"current_user": teacher, "class_id": tmpl.class_id, "class_name": class_name, "template": tmpl}
