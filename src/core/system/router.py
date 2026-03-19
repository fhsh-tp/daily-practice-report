"""Setup wizard router and system config admin API."""
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from core.auth.guards import require_permission
from core.auth.password import hash_password
from core.auth.permissions import READ_SYSTEM, WRITE_SYSTEM
from core.system.models import SystemConfig
from core.users.models import User
from shared.redis import SETUP_FLAG_KEY
from shared.webpage import webpage

router = APIRouter(tags=["setup"])


# ── System config admin API ──────────────────────────────────────────────────

class SystemConfigUpdate(BaseModel):
    site_name: str
    admin_email: str


@router.get("/admin/system")
async def get_system_config(
    request: Request,
    _: User = Depends(require_permission(READ_SYSTEM)),
):
    """Return current system configuration."""
    config = getattr(request.app.state, "system_config", None)
    if config is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="System not configured")
    return {"site_name": config.site_name, "admin_email": config.admin_email}


@router.put("/admin/system")
async def update_system_config(
    body: SystemConfigUpdate,
    request: Request,
    _: User = Depends(require_permission(WRITE_SYSTEM)),
):
    """Update system configuration. Refreshes in-memory state and WebPage context."""
    config = await SystemConfig.find_one()
    if config is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="System not configured")
    config.site_name = body.site_name
    config.admin_email = body.admin_email
    await config.save()
    request.app.state.system_config = config
    webpage.webpage_context_update({"site_name": body.site_name})
    return {"site_name": config.site_name, "admin_email": config.admin_email}


# ── Setup wizard ─────────────────────────────────────────────────────────────

def _is_configured(request: Request) -> bool:
    return getattr(request.app.state, "system_config", None) is not None


@router.get("/setup", name="setup_page", response_class=HTMLResponse)
@webpage.page("setup.html")
async def get_setup(request: Request, error: str | None = None):
    if _is_configured(request):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return {"error": error}


@router.post("/setup")
@webpage.redirect(status_code=302)
async def post_setup(
    request: Request,
    site_name: str = Form(...),
    admin_username: str = Form(...),
    admin_password: str = Form(...),
):
    if _is_configured(request):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already configured")

    try:
        # Persist system config
        config = SystemConfig(site_name=site_name, admin_email="")
        await config.insert()

        # Create admin user with full site-admin permissions
        from core.auth.permissions import SITE_ADMIN
        admin = User(
            username=admin_username,
            hashed_password=hash_password(admin_password),
            display_name=admin_username,
            permissions=int(SITE_ADMIN),
        )
        await admin.insert()

        # Mark as configured
        await request.app.state.redis.set(SETUP_FLAG_KEY, "true")
        request.app.state.system_config = config

        # Update WebPage global context with the new site_name
        webpage.webpage_context_update({"site_name": site_name})

    except Exception as e:
        error_url = request.url_for("setup_page").include_query_params(error=str(e))
        return (str(error_url), 302)

    return "/"
