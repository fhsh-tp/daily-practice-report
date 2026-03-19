"""
Migration: Populate User.identity_tags from existing permissions

Rules:
  - Holds MANAGE_OWN_CLASS (0x020)  → identity_tags includes "teacher"
  - Holds SUBMIT_TASK (0x004) but NOT MANAGE_OWN_CLASS → identity_tags includes "student"
  - Already has identity_tags set → skip (idempotent)

This migration is safe to re-run; it only touches documents where
identity_tags is an empty array or missing.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

MANAGE_OWN_CLASS = 0x020
SUBMIT_TASK      = 0x004


async def forward(db=None) -> None:
    """Infer and set identity_tags for existing users."""
    if db is None:
        db = await _get_db()

    # Only update documents that have no identity_tags yet
    async for doc in db["users"].find(
        {"$or": [{"identity_tags": {"$exists": False}}, {"identity_tags": []}]}
    ):
        perms = doc.get("permissions", 0)
        tags: list[str] = []

        if perms & MANAGE_OWN_CLASS:
            tags.append("teacher")
        elif perms & SUBMIT_TASK:
            tags.append("student")

        if tags:
            await db["users"].update_one(
                {"_id": doc["_id"]},
                {"$set": {"identity_tags": tags}},
            )


async def backward(db=None) -> None:
    """Remove identity_tags field (rollback to empty state)."""
    if db is None:
        db = await _get_db()
    await db["users"].update_many({}, {"$set": {"identity_tags": []}})


async def _get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "dts2")
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]
