import os
import logging
from typing import TYPE_CHECKING

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

if TYPE_CHECKING:
    from beanie import Document
    from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("uvicorn.error")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "dts2")


def get_motor_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(MONGO_URL)


async def init_db(
    database: "AsyncIOMotorDatabase | None" = None,
    document_models: "list[type[Document]] | None" = None,
) -> None:
    """
    初始化 Beanie ODM。

    在正式環境中不傳參數，自動使用環境變數建立 Motor client。
    測試時可傳入 mongomock_motor 的假 database 與 document_models。

    Args:
        database: 可選的 Motor database（測試用）。
        document_models: 要初始化的 Beanie Document 類別列表。
    """
    if database is None:
        client = get_motor_client()
        database = client[MONGO_DB_NAME]
        logger.info(f"[DATABASE] Connecting to {MONGO_URL}/{MONGO_DB_NAME}")

    models = document_models or []
    await init_beanie(database=database, document_models=models)
    logger.info(f"[DATABASE] Beanie initialized with {len(models)} document model(s)")
