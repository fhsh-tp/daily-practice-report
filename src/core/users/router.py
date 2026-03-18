"""Admin router: teacher manages student accounts."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth.deps import require_teacher
from core.auth.password import hash_password
from core.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "student"


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    teacher: User = Depends(require_teacher()),
):
    """Teacher creates a new user account (default role: student)."""
    if body.role not in ("student", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role must be 'student' or 'teacher'",
        )

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
        role=body.role,
    )
    await user.insert()
    return {"id": str(user.id), "username": user.username, "role": user.role}
