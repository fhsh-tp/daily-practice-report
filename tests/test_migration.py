"""Tests for the Migration Script framework."""
import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.get_database("test_migrate")
    yield db
    client.close()


async def test_migration_record_structure(mock_db):
    """Migration tracking collection should record filename, applied_at, direction."""
    from scripts.migrate import MigrationRecord
    record = MigrationRecord(
        filename="20260317_001_initial_indexes.py",
        direction="forward",
    )
    assert record.filename == "20260317_001_initial_indexes.py"
    assert record.direction == "forward"
    assert record.applied_at is not None


async def test_get_applied_migrations_empty(mock_db):
    """Should return empty list when no migrations have been applied."""
    from scripts.migrate import get_applied_migrations
    applied = await get_applied_migrations(mock_db)
    assert applied == []


async def test_record_migration(mock_db):
    """Should insert a migration record into the tracking collection."""
    from scripts.migrate import record_migration, get_applied_migrations
    await record_migration(mock_db, "20260317_001_initial_indexes.py", "forward")
    applied = await get_applied_migrations(mock_db)
    assert "20260317_001_initial_indexes.py" in applied


async def test_idempotency_no_duplicate(mock_db):
    """Running record_migration twice should not create duplicates."""
    from scripts.migrate import record_migration, get_applied_migrations
    await record_migration(mock_db, "20260317_001_initial_indexes.py", "forward")
    await record_migration(mock_db, "20260317_001_initial_indexes.py", "forward")
    applied = await get_applied_migrations(mock_db)
    assert applied.count("20260317_001_initial_indexes.py") == 1


async def test_migration_file_has_forward_and_backward():
    """Each migration file must expose forward() and backward() coroutines."""
    import inspect
    from scripts.migrations import test_example_migration as m
    assert inspect.iscoroutinefunction(m.forward)
    assert inspect.iscoroutinefunction(m.backward)
