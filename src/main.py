import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from shared import SessionMiddleware, init_db
from shared.database import get_motor_client
from shared.redis import get_redis_client


def _collect_document_models():
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from tasks.templates.models import TaskTemplate, TaskAssignment
    from tasks.submissions.models import TaskSubmission
    from tasks.checkin.models import CheckinConfig, DailyCheckinOverride, CheckinRecord
    from gamification.points.models import PointTransaction, ClassPointConfig
    from gamification.badges.models import BadgeDefinition, BadgeAward
    from community.feed.models import FeedPost, Reaction
    from gamification.prizes.models import Prize
    from core.system.models import SystemConfig
    return [
        User, Class, ClassMembership,
        TaskTemplate, TaskAssignment, TaskSubmission,
        CheckinConfig, DailyCheckinOverride, CheckinRecord,
        PointTransaction, ClassPointConfig,
        BadgeDefinition, BadgeAward,
        FeedPost, Reaction,
        Prize,
        SystemConfig,
    ]


def _register_extensions():
    from extensions.registry import registry
    from extensions.protocols.auth import AuthProvider
    from extensions.protocols.reward import RewardProvider
    from core.auth.local_provider import LocalAuthProvider
    from gamification.points.providers import CheckinRewardProvider, SubmissionRewardProvider

    registry.register(AuthProvider, "local", LocalAuthProvider())
    registry.register(RewardProvider, "checkin", CheckinRewardProvider())
    registry.register(RewardProvider, "submission", SubmissionRewardProvider())


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.system.startup import init_redis_state, check_setup_state

    # MongoDB
    client = get_motor_client()
    db_name = os.getenv("MONGO_DB_NAME", "dts2")
    database = client[db_name]
    document_models = _collect_document_models()
    await init_db(database=database, document_models=document_models)

    # Redis — store client in app.state.redis
    redis_client = get_redis_client()
    await init_redis_state(app.state, redis_client)

    # Setup state check
    await check_setup_state(app.state)

    _register_extensions()

    yield

    await app.state.redis.aclose()
    client.close()


app = FastAPI(lifespan=lifespan)

SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Jinja2 templates
_templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))

# --- Routers ---
from core.auth.router import router as auth_router
from core.users.router import router as users_router
from core.classes.router import router as classes_router
from tasks.templates.router import router as templates_router
from tasks.submissions.router import router as submissions_router
from tasks.checkin.router import router as checkin_router
from gamification.points.router import router as points_router
from gamification.badges.router import router as badges_router
from community.feed.router import router as feed_router
from gamification.prizes.router import router as prizes_router
from gamification.leaderboard.router import router as leaderboard_router

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(classes_router)
app.include_router(templates_router)
app.include_router(submissions_router)
app.include_router(checkin_router)
app.include_router(points_router)
app.include_router(badges_router)
app.include_router(feed_router)
app.include_router(prizes_router)
app.include_router(leaderboard_router)


@app.get("/")
async def root():
    return {"message": "root page"}
