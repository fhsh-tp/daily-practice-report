"""Task templates router."""
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import get_current_user, require_teacher
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
    teacher: User = Depends(require_teacher()),
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
    teacher: User = Depends(require_teacher()),
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
    teacher: User = Depends(require_teacher()),
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
    teacher: User = Depends(require_teacher()),
):
    try:
        await delete_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
