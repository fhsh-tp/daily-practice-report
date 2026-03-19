"""User response schemas — controls data visibility per viewer identity."""
from pydantic import BaseModel

from core.users.models import IdentityTag, User


class UserPublicView(BaseModel):
    """Visible to all authenticated users (e.g. students viewing each other)."""
    id: str
    display_name: str


class UserStaffView(BaseModel):
    """Visible to users with TEACHER or STAFF identity tag."""
    id: str
    display_name: str
    name: str
    email: str
    identity_tags: list[str]
    student_profile: dict | None


class UserAdminView(BaseModel):
    """Full view — used by admin endpoints (requires MANAGE_USERS)."""
    id: str
    username: str
    display_name: str
    name: str
    email: str
    permissions: int
    identity_tags: list[str]
    tags: list[str]
    student_profile: dict | None


def public_view(user: User) -> dict:
    return {"id": str(user.id), "display_name": user.display_name}


def staff_view(user: User) -> dict:
    return {
        "id": str(user.id),
        "display_name": user.display_name,
        "name": user.name,
        "email": user.email,
        "identity_tags": [t.value for t in user.identity_tags],
        "student_profile": (
            {"class_name": user.student_profile.class_name,
             "seat_number": user.student_profile.seat_number}
            if user.student_profile else None
        ),
    }


def admin_view(user: User) -> dict:
    return {
        "id": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "name": user.name,
        "email": user.email,
        "permissions": user.permissions,
        "identity_tags": [t.value for t in user.identity_tags],
        "tags": user.tags,
        "student_profile": (
            {"class_name": user.student_profile.class_name,
             "seat_number": user.student_profile.seat_number}
            if user.student_profile else None
        ),
    }


def select_view(viewer: User, target: User) -> dict:
    """Select the appropriate view schema based on viewer's identity tags."""
    viewer_tags = {t.value for t in viewer.identity_tags}
    if viewer_tags & {"teacher", "staff"}:
        return staff_view(target)
    return public_view(target)
