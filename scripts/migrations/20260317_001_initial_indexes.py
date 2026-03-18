"""
Initial database indexes for dts2.

Creates indexes for all commonly queried fields to ensure performance
with 50-200 students across multiple classes.
"""
import os

from motor.motor_asyncio import AsyncIOMotorClient


async def _get_db():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "dts2")
    client = AsyncIOMotorClient(mongo_url)
    return client, client[db_name]


async def forward() -> None:
    """Create indexes for all core collections."""
    client, db = await _get_db()
    try:
        # users: unique username lookup
        await db["users"].create_index("username", unique=True)
        await db["users"].create_index("role")

        # class_memberships: lookup by class or user
        await db["classmemberships"].create_index([("class_id", 1), ("user_id", 1)], unique=True)
        await db["classmemberships"].create_index("user_id")

        # task_assignments: lookup by class + date
        await db["taskassignments"].create_index([("class_id", 1), ("date", 1)])

        # task_submissions: lookup by student + date, class + date
        await db["tasksubmissions"].create_index([("student_id", 1), ("date", -1)])
        await db["tasksubmissions"].create_index([("class_id", 1), ("date", -1)])

        # checkin_records: lookup by student + date
        await db["checkinrecords"].create_index([("student_id", 1), ("date", -1)])
        await db["checkinrecords"].create_index([("class_id", 1), ("date", -1)])

        # point_transactions: lookup by student
        await db["pointtransactions"].create_index([("student_id", 1), ("created_at", -1)])
        await db["pointtransactions"].create_index("class_id")

        # badge_awards: lookup by student
        await db["badgeawards"].create_index([("student_id", 1)])
        await db["badgeawards"].create_index([("student_id", 1), ("badge_id", 1)], unique=True)

        # feed_posts: lookup by class + created_at
        await db["feedposts"].create_index([("class_id", 1), ("created_at", -1)])

    finally:
        client.close()


async def backward() -> None:
    """Drop all custom indexes (leave _id indexes intact)."""
    client, db = await _get_db()
    try:
        for collection_name in [
            "users", "classmemberships", "taskassignments",
            "tasksubmissions", "checkinrecords", "pointtransactions",
            "badgeawards", "feedposts",
        ]:
            try:
                await db[collection_name].drop_indexes()
            except Exception:
                pass
    finally:
        client.close()
