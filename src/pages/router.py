"""Pages router — login, logout redirect, dashboard, and admin panel."""
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
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

    from core.auth.permissions import MANAGE_OWN_CLASS, MANAGE_ALL_CLASSES, MANAGE_TASKS, MANAGE_USERS, WRITE_SYSTEM
    can_manage_class = bool(current_user.permissions & (MANAGE_OWN_CLASS | MANAGE_ALL_CLASSES))

    classes = []
    for m in memberships:
        cls = await Class.get(m.class_id)
        if cls is None:
            continue
        # Students don't see archived classes; managers/teachers do
        if cls.is_archived and not can_manage_class:
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
            "is_archived": cls.is_archived,
            "owner_id": cls.owner_id,
            "checkin_open": checkin_result.is_open,
            "already_checked_in": existing_checkin is not None,
            "closes_at": checkin_result.closes_at.isoformat() if checkin_result.closes_at else None,
            "reason": checkin_result.reason,
            "today_template": today_template,
        })

    return {
        "current_user": current_user,
        "classes": classes,
        "can_manage_class": can_manage_class,
        "can_manage_tasks": bool(current_user.permissions & MANAGE_TASKS),
        "can_manage_users": bool(current_user.permissions & MANAGE_USERS),
        "is_sys_admin": bool(current_user.permissions & WRITE_SYSTEM),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Admin Panel — Cookie auth + admin permission guard
# ═══════════════════════════════════════════════════════════════════════════

def _build_schema():
    """Build schema list with precomputed 'all' (read|write) for templates."""
    from core.auth.permissions import PERMISSION_SCHEMA
    return [
        {
            "domain": e["domain"],
            "label": e.get("label", e["domain"]),
            "description": e.get("description", ""),
            "hide_read": e.get("hide_read", False),
            "read": int(e["read"]),
            "write": int(e["write"]),
            "all": int(e["read"]) | int(e["write"]),
        }
        for e in PERMISSION_SCHEMA
    ]


def _compute_initial_levels(permissions: int, schema: list) -> dict:
    """Return {'Self': 'none'|'read'|'readwrite', ...} for each domain."""
    levels = {}
    for entry in schema:
        has_write = bool(permissions & entry["write"])
        has_read = bool(permissions & entry["read"])
        if has_write:
            levels[entry["domain"]] = "readwrite"
        elif has_read:
            levels[entry["domain"]] = "read"
        else:
            levels[entry["domain"]] = "none"
    return levels


def _admin_context(current_user: User) -> dict:
    """Common context injected into every admin page."""
    from core.auth.permissions import MANAGE_USERS, WRITE_SYSTEM
    return {
        "current_user": current_user,
        "can_manage_users": bool(current_user.permissions & MANAGE_USERS),
        "is_sys_admin": bool(current_user.permissions & WRITE_SYSTEM),
        "can_manage_class": False,
        "can_manage_tasks": False,
        "classes": [],
    }


async def _require_admin(current_user: User = Depends(get_page_user)) -> User:
    """Guard: user must have MANAGE_USERS or WRITE_SYSTEM."""
    from core.auth.permissions import MANAGE_USERS, WRITE_SYSTEM
    if not (current_user.permissions & MANAGE_USERS or current_user.permissions & WRITE_SYSTEM):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return current_user


async def _require_manage_users(current_user: User = Depends(get_page_user)) -> User:
    from core.auth.permissions import MANAGE_USERS
    if not (current_user.permissions & MANAGE_USERS):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return current_user


async def _require_write_system(current_user: User = Depends(get_page_user)) -> User:
    from core.auth.permissions import WRITE_SYSTEM
    if not (current_user.permissions & WRITE_SYSTEM):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return current_user


@router.get("/admin/", name="admin_overview_page")
@webpage.page("admin/index.html")
async def admin_overview(
    request: Request,
    current_user: User = Depends(_require_admin),
):
    total = await User.count()
    return {
        **_admin_context(current_user),
        "user_count": total,
        "admin_section": "overview",
        "success": request.query_params.get("success"),
        "error": request.query_params.get("error"),
    }


@router.get("/admin/users/", name="admin_users_list_page")
@webpage.page("admin/users_list.html")
async def admin_users_list(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(_require_manage_users),
):
    from core.auth.permissions import ROLE_PRESETS
    skip = (page - 1) * page_size
    total = await User.count()
    users = await User.find_all().skip(skip).limit(page_size).to_list()
    return {
        **_admin_context(current_user),
        "users": [
            {
                "id": str(u.id),
                "username": u.username,
                "display_name": u.display_name,
                "name": u.name,
                "permissions": u.permissions,
                "tags": u.tags,
                "identity_tags": [t.value if hasattr(t, "value") else t for t in u.identity_tags],
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "presets": ROLE_PRESETS,
        "admin_section": "users",
        "success": request.query_params.get("success"),
        "error": request.query_params.get("error"),
    }


@router.get("/admin/users/new", name="admin_user_new_page")
@webpage.page("admin/user_form.html")
async def admin_user_new(
    request: Request,
    current_user: User = Depends(_require_manage_users),
):
    from core.auth.permissions import ROLE_PRESETS
    schema = _build_schema()
    return {
        **_admin_context(current_user),
        "edit_user": None,
        "initial_levels": {e["domain"]: "none" for e in schema},
        "schema": schema,
        "presets": ROLE_PRESETS,
        "admin_section": "users",
        "success": request.query_params.get("success"),
        "error": request.query_params.get("error"),
    }


@router.post("/admin/users/new")
@webpage.redirect(status_code=302)
async def admin_user_new_submit(
    request: Request,
    username: str = Form(...),
    display_name: str = Form(...),
    password: str = Form(...),
    permissions: int = Form(default=0),
    tags: str = Form(default=""),
    name: str = Form(default=""),
    email: str = Form(default=""),
    class_name: str = Form(default=""),
    seat_number: int = Form(default=0),
    current_user: User = Depends(_require_manage_users),
):
    from core.auth.password import hash_password
    from core.users.models import IdentityTag, StudentProfile
    form_data = await request.form()
    identity_tag_values = form_data.getlist("identity_tags")
    valid_tags = {t.value for t in IdentityTag}
    identity_tags = [IdentityTag(v) for v in identity_tag_values if v in valid_tags]

    existing = await User.find_one(User.username == username)
    if existing:
        error_url = request.url_for("admin_user_new_page").include_query_params(error="使用者名稱已存在")
        return (str(error_url), 302)
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    student_profile = None
    if IdentityTag.STUDENT in identity_tags and (class_name or seat_number):
        student_profile = StudentProfile(class_name=class_name, seat_number=seat_number)
    user = User(
        username=username,
        hashed_password=hash_password(password),
        display_name=display_name,
        name=name,
        email=email,
        permissions=permissions,
        tags=tags_list,
        identity_tags=identity_tags,
        student_profile=student_profile,
    )
    await user.insert()
    success_url = request.url_for("admin_users_list_page").include_query_params(success="使用者已建立")
    return (str(success_url), 302)


@router.get("/admin/users/{user_id}/edit", name="admin_user_edit_page")
@webpage.page("admin/user_form.html")
async def admin_user_edit(
    request: Request,
    user_id: str,
    current_user: User = Depends(_require_manage_users),
):
    from core.auth.permissions import ROLE_PRESETS
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    schema = _build_schema()
    return {
        **_admin_context(current_user),
        "edit_user": {
            "id": str(user.id),
            "username": user.username,
            "display_name": user.display_name,
            "name": user.name,
            "email": user.email,
            "permissions": user.permissions,
            "tags": user.tags,
            "identity_tags": [t.value if hasattr(t, "value") else t for t in user.identity_tags],
            "student_profile": user.student_profile,
        },
        "initial_levels": _compute_initial_levels(user.permissions, schema),
        "schema": schema,
        "presets": ROLE_PRESETS,
        "admin_section": "users",
        "success": request.query_params.get("success"),
        "error": request.query_params.get("error"),
    }


@router.post("/admin/users/{user_id}/edit")
@webpage.redirect(status_code=302)
async def admin_user_edit_submit(
    request: Request,
    user_id: str,
    display_name: str = Form(...),
    permissions: int = Form(default=0),
    tags: str = Form(default=""),
    new_password: str = Form(default=""),
    name: str = Form(default=""),
    email: str = Form(default=""),
    class_name: str = Form(default=""),
    seat_number: int = Form(default=0),
    current_user: User = Depends(_require_manage_users),
):
    from core.auth.password import hash_password
    from core.users.models import IdentityTag, StudentProfile
    form_data = await request.form()
    identity_tag_values = form_data.getlist("identity_tags")
    valid_tags = {t.value for t in IdentityTag}
    identity_tags = [IdentityTag(v) for v in identity_tag_values if v in valid_tags]

    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.display_name = display_name
    user.name = name
    user.email = email
    user.permissions = permissions
    user.tags = [t.strip() for t in tags.split(",") if t.strip()]
    user.identity_tags = identity_tags
    if IdentityTag.STUDENT in identity_tags:
        user.student_profile = StudentProfile(class_name=class_name, seat_number=seat_number)
    else:
        user.student_profile = None
    if new_password:
        user.hashed_password = hash_password(new_password)
    await user.save()
    success_url = request.url_for("admin_users_list_page").include_query_params(success="使用者已更新")
    return (str(success_url), 302)


@router.get("/admin/system/", name="admin_system_page")
@webpage.page("admin/system_settings.html")
async def admin_system_settings(
    request: Request,
    current_user: User = Depends(_require_write_system),
):
    config = getattr(request.app.state, "system_config", None)
    return {
        **_admin_context(current_user),
        "config": config,
        "admin_section": "system",
        "success": request.query_params.get("success"),
        "error": request.query_params.get("error"),
    }


@router.post("/admin/system/")
@webpage.redirect(status_code=302)
async def admin_system_settings_submit(
    request: Request,
    site_name: str = Form(...),
    admin_email: str = Form(default=""),
    current_user: User = Depends(_require_write_system),
):
    from core.system.models import SystemConfig
    config = await SystemConfig.find_one()
    if config:
        config.site_name = site_name
        config.admin_email = admin_email
        await config.save()
        request.app.state.system_config = config
        webpage.webpage_context_update({"site_name": site_name})
    success_url = request.url_for("admin_system_page").include_query_params(success="設定已儲存")
    return (str(success_url), 302)
