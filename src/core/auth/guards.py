"""Route guards for permission-based access control."""
from fastapi import Depends, HTTPException, status

from core.auth.deps import get_current_user
from core.auth.permissions import Permission
from core.users.models import User


def require_permission(flag: Permission):
    """
    FastAPI dependency factory that enforces a required permission flag.

    Usage::

        @router.post("/foo")
        async def foo(user: User = Depends(require_permission(MANAGE_CLASS))):
            ...

    Raises:
        HTTPException 403: If the current user does not hold the required flag.
    """
    async def guard(current_user: User = Depends(get_current_user)) -> User:
        if not (current_user.permissions & flag):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current_user

    return guard
