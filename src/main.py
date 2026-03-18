import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared import SessionMiddleware, init_db
from shared.database import get_motor_client


def _collect_document_models():
    """
    Collect all Beanie Document models for registration.
    Import here to avoid circular imports at module level.
    """
    from core.users.models import User
    return [User]


def _register_extensions():
    """
    Register all default extension implementations into the ExtensionRegistry.
    Called during startup after database is initialized.
    """
    from extensions.registry import registry
    from core.auth.local_provider import LocalAuthProvider

    registry.register("auth", "local", LocalAuthProvider())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MongoDB + Beanie
    client = get_motor_client()
    db_name = os.getenv("MONGO_DB_NAME", "dts2")
    database = client[db_name]

    document_models = _collect_document_models()
    await init_db(database=database, document_models=document_models)

    # Register extension implementations
    _register_extensions()

    yield

    client.close()


app = FastAPI(lifespan=lifespan)

# Session middleware
SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)


@app.get("/")
async def root():
    return {"message": "root page"}
