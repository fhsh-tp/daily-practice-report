import os
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import logging

logger = logging.getLogger("uvicorn.error")

# 1. 建立 DB Engine
_db_url = os.getenv("DB_URL") or "sqlite+aiosqlite:///:memory:"

# ECHO 模式：在非正式環境下開啟 SQL log
_is_dev = os.getenv("FASTAPI_APP_ENVIRONMENT", "dev") != "prod"

# 如果使用 in-memory SQLite，需要使用 StaticPool 保持連接，
# 否則每次 session 結束資料庫內容也會消失
connect_args = {}
engine_args = {
    "echo": _is_dev,
    "future": True,
}

if "sqlite" in _db_url:
    connect_args["check_same_thread"] = False
    engine_args["connect_args"] = connect_args
    if ":memory:" in _db_url:
        engine_args["poolclass"] = StaticPool


engine: AsyncEngine = create_async_engine(_db_url, **engine_args)


# 2. 定義初始化 DB 的函式 (通常在 app startup 時呼叫)
async def init_db() -> None:
    """
    初始化資料庫。

    這通常在應用程式啟動時呼叫。它會根據 defined SQLModel models 建立資料庫表格。
    在開發環境中，如果需要重置資料庫，可以取消註解 drop_all 行。

    範例:
        >>> from contextlib import asynccontextmanager
        >>> from fastapi import FastAPI
        >>>
        >>> @asynccontextmanager
        >>> async def lifespan(app: FastAPI):
        >>>     await init_db()
        >>>     yield
        >>>
        >>> app = FastAPI(lifespan=lifespan)
    """
    logger.info(f"[DATABASE INFO] use url: {_db_url}")
    async with engine.begin() as conn:
        # 在開發模式下，如果需要自動建立 Table：
        # await conn.run_sync(SQLModel.metadata.drop_all) # Optional: Reset DB
        await conn.run_sync(SQLModel.metadata.create_all)


# 3. 定義 Dependency 供 Router 使用
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    獲取資料庫 Session 的 Dependency。

    這個函式產生一個非同步的 Session，用於與資料庫互動。
    它被設計為 FastAPI 的 Dependency injection 使用。

    Yields:
        AsyncSession: 一個資料庫 session 物件。

    範例:
        >>> from fastapi import Depends, FastAPI
        >>> from sqlmodel import select
        >>> from .models import Item
        >>>
        >>> app = FastAPI()
        >>>
        >>> @app.get("/items/")
        >>> async def read_items(session: SessionDep):
        >>>     result = await session.execute(select(Item))
        >>>     items = result.scalars().all()
        >>>     return items
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


# 4. 定義 Type Alias 方便在 Router 中使用
# 例如: async def read_users(session: SessionDep):
SessionDep = Annotated[AsyncSession, Depends(get_session)]
