from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared import init_db
from shared.sessions import SessionMiddleware
import os
import secrets

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    ...
    yield
    ...

app = FastAPI(lifespan=lifespan)

# Set session middleware
## Detect session secret key is set.
SESSION_SECRET=os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    SESSION_SECRET = secrets.token_hex(32)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

@app.get("/")
async def root():
    return { "message": "root page" }