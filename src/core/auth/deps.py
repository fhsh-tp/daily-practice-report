"""FastAPI dependencies for authentication and role-based access control."""
from typing import Any, Callable

from fastapi import Cookie, Depends, HTTPException, status

from core.auth.jwt import decode_access_token
from core.users.models import User


async def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> User:
    """
    Validate the JWT from the HttpOnly cookie and return the current user.

    Raises:
        HTTPException 401: If no token or token is invalid/expired.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_access_token(access_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")
    user = await User.get(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


CurrentUser = Depends(get_current_user)


def require_teacher() -> Callable:
    """
    Return a FastAPI dependency that enforces the teacher role.
    Returns the current user if they are a teacher.
    Raises 403 if the user is a student.
    """
    async def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher access required",
            )
        return current_user
    return _dep


def require_student() -> Callable:
    """
    Return a FastAPI dependency that enforces the student role.
    Returns the current user if they are a student.
    Raises 403 if the user is a teacher.
    """
    async def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student access required",
            )
        return current_user
    return _dep
