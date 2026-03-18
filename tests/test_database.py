"""Tests for Beanie database initialization."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import Document


class DummyDoc(Document):
    name: str

    class Settings:
        name = "dummy_docs"


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.get_database("test_db")
    yield db
    client.close()


async def test_init_db_initializes_beanie(mock_db):
    """init_db should initialize Beanie with the provided database."""
    from shared.database import init_db
    await init_db(database=mock_db, document_models=[DummyDoc])

    # If Beanie is initialized, we should be able to insert and find a document
    doc = DummyDoc(name="test")
    await doc.insert()
    found = await DummyDoc.find_one(DummyDoc.name == "test")
    assert found is not None
    assert found.name == "test"


async def test_get_motor_client_returns_client():
    """get_motor_client should return a motor AsyncIOMotorClient."""
    from shared.database import get_motor_client
    client = get_motor_client()
    assert client is not None
