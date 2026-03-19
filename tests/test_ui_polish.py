"""Tests for ui-polish-and-fixes change."""
import pytest
import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "src" / "templates"

# Templates that must NOT use native browser dialogs
DIALOG_FREE_TEMPLATES = [
    "teacher/class_members.html",
    "admin/users_list.html",
    "admin/classes_list.html",
    "student/dashboard.html",
    "teacher/template_form.html",
]

# Pattern for direct native calls (window.confirm / window.alert / bare confirm( / bare alert()
# We look for: confirm( or alert( that are NOT preceded by "Modal."
_NATIVE_DIALOG_RE = re.compile(r'(?<!Modal\.)(?<!\w)(confirm|alert)\s*\(')


# ---------------------------------------------------------------------------
# Dashboard total_points (task 3.5)
# ---------------------------------------------------------------------------

@pytest.fixture
async def db_points_app():
    """App fixture with PointTransaction model for dashboard points test."""
    from beanie import init_beanie
    from fastapi import FastAPI
    from mongomock_motor import AsyncMongoMockClient

    from core.auth.permissions import STUDENT
    from core.auth.password import hash_password
    from core.auth.router import router as auth_router
    from core.classes.models import Class, ClassMembership
    from core.users.models import User
    from gamification.points.models import ClassPointConfig, PointTransaction
    from pages.router import router as pages_router
    from tasks.checkin.models import CheckinConfig, CheckinRecord, DailyCheckinOverride
    from tasks.submissions.models import TaskSubmission
    from tasks.submissions.router import router as submissions_router
    from tasks.templates.models import TaskAssignment, TaskTemplate

    client = AsyncMongoMockClient()
    db = client.get_database("test_points_dashboard")
    await init_beanie(
        database=db,
        document_models=[
            User, Class, ClassMembership,
            TaskTemplate, TaskAssignment, TaskSubmission,
            CheckinConfig, DailyCheckinOverride, CheckinRecord,
            PointTransaction, ClassPointConfig,
        ],
    )

    student = User(
        username="pts_student",
        hashed_password=hash_password("pw"),
        display_name="PtsStudent",
        permissions=int(STUDENT),
    )
    await student.insert()

    # Award 25 points
    await PointTransaction(
        student_id=str(student.id),
        class_id="cls1",
        amount=25,
        reason="checkin",
        source_event="checkin",
        source_id="evt1",
    ).insert()

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(pages_router)
    app.include_router(submissions_router)

    from core.auth.jwt import create_access_token
    token = create_access_token(user_id=str(student.id), permissions=int(STUDENT))
    yield app, {"access_token": token}, student.id

    client.close()


async def test_dashboard_context_includes_total_points(db_points_app):
    """Dashboard page context must include stats.total_points from PointTransactions."""
    from httpx import ASGITransport, AsyncClient

    app, cookies, student_id = db_points_app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies) as ac:
        response = await ac.get("/pages/dashboard", follow_redirects=False)

    assert response.status_code == 200
    content = response.content
    # The stats section must show 25 (the actual balance) and must NOT show the '—' placeholder
    # The '—' placeholder is rendered when stats is not in context
    # Locate the 總積分 stat card and verify it shows the real value
    idx = content.find("總積分".encode())
    assert idx != -1, "Dashboard should contain 總積分 stat card"
    # The value appears before the label; search in the 200 chars before the label
    nearby = content[max(0, idx - 200): idx]
    assert b"\xe2\x80\x94" not in nearby, "Stats section shows '—' placeholder instead of real points"
    assert b"25" in nearby, "Stats section should show 25 points"


def test_templates_do_not_use_native_browser_dialogs():
    """No template listed in DIALOG_FREE_TEMPLATES shall call confirm() or alert() directly."""
    violations = []
    for rel_path in DIALOG_FREE_TEMPLATES:
        path = TEMPLATES_DIR / rel_path
        content = path.read_text(encoding="utf-8")
        for match in _NATIVE_DIALOG_RE.finditer(content):
            line_no = content[:match.start()].count("\n") + 1
            violations.append(f"{rel_path}:{line_no} — native `{match.group()}` call")

    assert not violations, (
        "Templates contain native browser dialogs:\n" + "\n".join(violations)
    )
