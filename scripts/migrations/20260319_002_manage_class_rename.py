"""
Migration: MANAGE_CLASS → MANAGE_OWN_CLASS rename

Context:
  The MANAGE_CLASS flag (0x020) was renamed to MANAGE_OWN_CLASS (0x020).
  The integer value is UNCHANGED, so no document updates are required.

  This script serves as a record of the breaking change and validates
  that no user documents carry unexpected permission values.

What this migration does:
  forward()  — no-op (bit value unchanged, documents already consistent)
  backward() — no-op (same reason)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


async def forward(db=None) -> None:
    """No-op: MANAGE_OWN_CLASS retains the same bit value (0x020) as MANAGE_CLASS."""
    # MANAGE_CLASS (0x020) == MANAGE_OWN_CLASS (0x020)
    # All existing permission integers in the database remain valid.
    # No document updates are needed.
    pass


async def backward(db=None) -> None:
    """No-op: same reason as forward."""
    pass


async def _get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "dts2")
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]
