"""
Migration: User.role → User.permissions

Maps role = "student" → STUDENT preset int
Maps role = "teacher" → TEACHER preset int
Removes the role field after migration.
"""
import os
import sys

# Allow running standalone outside of src pythonpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.auth.permissions import STUDENT, TEACHER


async def forward(db=None) -> None:
    """Convert role field to permissions integer and remove role."""
    if db is None:
        db = await _get_db()

    role_map = {
        "student": int(STUDENT),
        "teacher": int(TEACHER),
    }

    for role_value, permissions_int in role_map.items():
        await db["users"].update_many(
            {"role": role_value},
            {
                "$set": {"permissions": permissions_int},
                "$unset": {"role": ""},
            },
        )


async def backward(db=None) -> None:
    """Restore role field from permissions integer (best-effort reversal)."""
    if db is None:
        db = await _get_db()

    student_int = int(STUDENT)
    teacher_int = int(TEACHER)

    await db["users"].update_many(
        {"permissions": student_int},
        {"$set": {"role": "student"}},
    )
    await db["users"].update_many(
        {"permissions": teacher_int},
        {"$set": {"role": "teacher"}},
    )


async def _get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "dts2")
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]
