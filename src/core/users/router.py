"""Admin router: user admin manages accounts."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.guards import require_permission
from core.auth.password import hash_password
from core.auth.permissions import MANAGE_USERS, STUDENT
from core.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: str
    permissions: int = int(STUDENT)
    tags: list[str] = []


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
    return {"id": str(user.id), "username": user.username, "permissions": user.permissions}
