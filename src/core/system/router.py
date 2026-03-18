"""Setup wizard router."""
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from core.auth.password import hash_password
from core.system.models import SystemConfig
from core.users.models import User
from shared.redis import SETUP_FLAG_KEY
from shared.webpage import webpage

router = APIRouter(tags=["setup"])


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

        # Create admin user
        admin = User(
            username=admin_username,
            hashed_password=hash_password(admin_password),
            display_name=admin_username,
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
