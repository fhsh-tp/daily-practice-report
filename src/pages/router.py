"""Pages router — login, logout redirect, and dashboard."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from core.users.models import User
from pages.deps import get_page_user
from shared.webpage import webpage

router = APIRouter(prefix="/pages", tags=["pages"])

_COOKIE_NAME = "access_token"
_COOKIE_MAX_AGE = 60 * 60 * 24  # 24h


@router.get("/login", name="login_page")
@webpage.page("login.html")
async def login_page(request: Request, error: str | None = None, next: str | None = None):
    return {"error": error, "next": next}


@router.post("/login")
@webpage.redirect(status_code=302)
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str | None = Form(default=None),
):
    from extensions.protocols import AuthProvider
    from extensions.registry import registry
    from core.auth.jwt import create_access_token

    # Validate next URL to prevent open redirect (must be a relative path)
    safe_next = None
    if next and next.startswith("/") and not next.startswith("//"):
        safe_next = next

    try:
        provider: AuthProvider = registry.get(AuthProvider, "local")
        user = await provider.authenticate({"username": username, "password": password})
    except Exception:
        error_url = request.url_for("login_page").include_query_params(error="帳號或密碼錯誤")
        return (str(error_url), 302)

    token = create_access_token(user_id=str(user.id), permissions=user.permissions)
    redirect_url = safe_next or str(request.url_for("dashboard_page"))
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )
    return response


@router.get("/dashboard", name="dashboard_page")
@webpage.page("student/dashboard.html")
async def dashboard_page(
    request: Request,
    current_user: User = Depends(get_page_user),
):
    from datetime import date, datetime, timezone

    from core.classes.models import Class, ClassMembership
    from tasks.checkin.models import CheckinRecord
    from tasks.checkin.service import is_checkin_open
    from tasks.templates.service import get_template_for_date

    memberships = await ClassMembership.find(
        ClassMembership.user_id == str(current_user.id)
    ).to_list()

    now = datetime.now(timezone.utc)
    today = date.today()

    classes = []
    for m in memberships:
        cls = await Class.get(m.class_id)
        if cls is None:
            continue

        checkin_result = await is_checkin_open(m.class_id, now)
        existing_checkin = await CheckinRecord.find_one(
            CheckinRecord.student_id == str(current_user.id),
            CheckinRecord.class_id == m.class_id,
            CheckinRecord.checkin_date == today,
        )
        today_template = await get_template_for_date(m.class_id, today)

        classes.append({
            "class_id": m.class_id,
            "class_name": cls.name,
            "checkin_open": checkin_result.is_open,
            "already_checked_in": existing_checkin is not None,
            "closes_at": checkin_result.closes_at.isoformat() if checkin_result.closes_at else None,
            "reason": checkin_result.reason,
            "today_template": today_template,
        })

    return {"current_user": current_user, "classes": classes}
