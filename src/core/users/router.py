"""Admin router: user admin manages accounts."""
import csv
import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from core.auth.guards import require_permission
from core.auth.password import hash_password
from core.auth.permissions import (
    MANAGE_USERS,
    PERMISSION_SCHEMA,
    ROLE_PRESETS,
    STUDENT,
)
from core.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])

_PRESET_MAP = {p["name"]: p["value"] for p in ROLE_PRESETS}


# ── Permission schema / presets ──────────────────────────────────────────────

@router.get("/permissions/schema")
async def get_permission_schema(
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Return PERMISSION_SCHEMA as a JSON-serialisable list."""
    return [
        {"domain": entry["domain"], "read": int(entry["read"]), "write": int(entry["write"])}
        for entry in PERMISSION_SCHEMA
    ]


@router.get("/permissions/presets")
async def get_permission_presets(
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Return all named Role Presets with their integer values."""
    return ROLE_PRESETS


# ── User CRUD ────────────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: str
    permissions: int = int(STUDENT)
    tags: list[str] = []


class UpdateUserRequest(BaseModel):
    display_name: str | None = None
    permissions: int | None = None
    tags: list[str] | None = None
    new_password: str | None = None


def _user_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "permissions": user.permissions,
        "tags": user.tags,
    }


@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Return a paginated list of all users."""
    skip = (page - 1) * page_size
    total = await User.count()
    users = await User.find_all().skip(skip).limit(page_size).to_list()
    return {
        "users": [_user_response(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """User admin creates a new user account."""
    existing = await User.find_one(User.username == body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        display_name=body.display_name,
        permissions=body.permissions,
        tags=body.tags,
    )
    await user.insert()
    return _user_response(user)


# ── Bulk operations (declared before /{user_id} to avoid route shadowing) ───

class BulkIdsRequest(BaseModel):
    ids: list[str]


class BulkPermissionsRequest(BaseModel):
    ids: list[str]
    permissions: int


@router.delete("/users/bulk")
async def bulk_delete_users(
    body: BulkIdsRequest,
    current_user: User = Depends(require_permission(MANAGE_USERS)),
):
    """Bulk delete users by ID list, silently excluding the caller's own ID."""
    own_id = str(current_user.id)
    target_ids = [uid for uid in body.ids if uid != own_id]
    deleted = 0
    for uid in target_ids:
        user = await User.get(uid)
        if user:
            await user.delete()
            deleted += 1
    return {"deleted": deleted}


@router.patch("/users/bulk")
async def bulk_update_permissions(
    body: BulkPermissionsRequest,
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Bulk update permissions for a list of users."""
    updated = 0
    for uid in body.ids:
        user = await User.get(uid)
        if user:
            user.permissions = body.permissions
            await user.save()
            updated += 1
    return {"updated": updated}


# ── CSV import ───────────────────────────────────────────────────────────────

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Return a single user by ID."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user_response(user)


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Update a user's display_name, permissions, tags, or password."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.permissions is not None:
        user.permissions = body.permissions
    if body.tags is not None:
        user.tags = body.tags
    if body.new_password is not None:
        user.hashed_password = hash_password(body.new_password)
    await user.save()
    return _user_response(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permission(MANAGE_USERS)),
):
    """Delete a single user. Cannot delete own account."""
    if str(current_user.id) == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await user.delete()


@router.post("/users/import")
async def import_users_csv(
    file: UploadFile = File(...),
    _: User = Depends(require_permission(MANAGE_USERS)),
):
    """Batch-create users from a CSV file (username,password,display_name,preset,tags)."""
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    success = 0
    failed: list[dict] = []

    for row_num, row in enumerate(reader, start=2):  # row 1 is header
        username = (row.get("username") or "").strip()
        password = (row.get("password") or "").strip()
        display_name = (row.get("display_name") or "").strip()
        preset_name = (row.get("preset") or "").strip().upper()
        tags_raw = (row.get("tags") or "").strip()

        if preset_name not in _PRESET_MAP:
            failed.append({"row": row_num, "reason": f"Unknown preset: {preset_name!r}"})
            continue

        existing = await User.find_one(User.username == username)
        if existing:
            failed.append({"row": row_num, "reason": f"Username already exists: {username!r}"})
            continue

        tags = [t.strip() for t in tags_raw.split(";") if t.strip()] if tags_raw else []
        user = User(
            username=username,
            hashed_password=hash_password(password),
            display_name=display_name,
            permissions=_PRESET_MAP[preset_name],
            tags=tags,
        )
        await user.insert()
        success += 1

    return {"success": success, "failed": failed}
