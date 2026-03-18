"""Integration tests for role→permissions migration script."""
import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.get_database("test_role_migrate")
    yield db
    client.close()


async def test_student_role_migrated_to_permissions(mock_db):
    """User with role='student' must be migrated to STUDENT preset int."""
    from core.auth.permissions import STUDENT
    from scripts.migrations.role_to_permissions import forward

    # Insert a legacy user with role field
    await mock_db["users"].insert_one({
        "username": "alice",
        "hashed_password": "hashed",
        "display_name": "Alice",
        "role": "student",
        "is_active": True,
    })

    await forward(mock_db)

    doc = await mock_db["users"].find_one({"username": "alice"})
    assert doc["permissions"] == int(STUDENT)
    assert "role" not in doc


async def test_teacher_role_migrated_to_permissions(mock_db):
    """User with role='teacher' must be migrated to TEACHER preset int."""
    from core.auth.permissions import TEACHER
    from scripts.migrations.role_to_permissions import forward

    await mock_db["users"].insert_one({
        "username": "bob",
        "hashed_password": "hashed",
        "display_name": "Bob",
        "role": "teacher",
        "is_active": True,
    })

    await forward(mock_db)

    doc = await mock_db["users"].find_one({"username": "bob"})
    assert doc["permissions"] == int(TEACHER)
    assert "role" not in doc


async def test_migration_backward_restores_role(mock_db):
    """backward() must add back role field based on permissions int."""
    from core.auth.permissions import STUDENT, TEACHER
    from scripts.migrations.role_to_permissions import backward

    await mock_db["users"].insert_many([
        {"username": "alice", "permissions": int(STUDENT), "is_active": True},
        {"username": "bob", "permissions": int(TEACHER), "is_active": True},
    ])

    await backward(mock_db)

    alice = await mock_db["users"].find_one({"username": "alice"})
    bob = await mock_db["users"].find_one({"username": "bob"})
    assert alice.get("role") == "student"
    assert bob.get("role") == "teacher"


async def test_migration_has_forward_and_backward():
    """Migration module must expose forward() and backward() coroutines."""
    import inspect
    from scripts.migrations import role_to_permissions as m
    assert inspect.iscoroutinefunction(m.forward)
    assert inspect.iscoroutinefunction(m.backward)
