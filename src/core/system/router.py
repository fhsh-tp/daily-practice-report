"""Setup wizard router."""
from pathlib import Path

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.auth.password import hash_password
from core.system.models import SystemConfig
from core.users.models import User
from shared.redis import SETUP_FLAG_KEY

router = APIRouter(tags=["setup"])

_templates = Jinja2Templates(
    directory=str(Path(__file__).parents[2] / "templates")
)


def _is_configured(request: Request) -> bool:
    return getattr(request.app.state, "system_config", None) is not None


@router.get("/setup", response_class=HTMLResponse)
async def get_setup(request: Request):
    if _is_configured(request):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return _templates.TemplateResponse(request, "setup.html")


@router.post("/setup")
async def post_setup(
    request: Request,
    site_name: str = Form(...),
    admin_username: str = Form(...),
    admin_password: str = Form(...),
):
    if _is_configured(request):
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already configured")

    # Persist system config
    config = SystemConfig(site_name=site_name, admin_email="")
    await config.insert()

    # Create admin user (role will be updated to permissions after RBAC change)
    admin = User(
        username=admin_username,
        hashed_password=hash_password(admin_password),
        display_name=admin_username,
        role="teacher",
    )
    await admin.insert()

    # Mark as configured
    await request.app.state.redis.set(SETUP_FLAG_KEY, "true")
    request.app.state.system_config = config

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
