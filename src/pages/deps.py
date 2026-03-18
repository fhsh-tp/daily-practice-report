"""Page-aware auth dependency — redirects to login instead of raising 401."""
from fastapi import Cookie, HTTPException, Request, status

from core.auth.jwt import decode_access_token
from core.users.models import User


def _redirect_to_login(request: Request) -> None:
    """Raise a 302 redirect to the login page, preserving the current URL as `next`."""
    login_url = str(
        request.url_for("login_page").include_query_params(next=str(request.url))
    )
    raise HTTPException(
        status_code=status.HTTP_302_FOUND,
        headers={"Location": login_url},
    )


async def get_page_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
) -> User:
    """
    Dependency that returns the authenticated User.

    Unlike ``get_current_user``, this redirects to the login page (302) instead
    of raising 401, so unauthenticated browser requests land on the login form.
    """
    if not access_token:
        _redirect_to_login(request)

    try:
        payload = decode_access_token(access_token)
    except Exception:
        _redirect_to_login(request)

    user_id = payload.get("user_id")
    user = await User.get(user_id)
    if user is None or not user.is_active:
        _redirect_to_login(request)

    return user
