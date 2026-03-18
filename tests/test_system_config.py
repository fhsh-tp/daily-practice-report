"""Tests for the system-config capability."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_system")
    from core.system.models import SystemConfig
    await init_beanie(database=database, document_models=[SystemConfig])
    yield database
    client.close()


async def test_system_config_insert_and_retrieve(db):
    """SystemConfig can be inserted and retrieved as a singleton via find_one."""
    from core.system.models import SystemConfig
    config = SystemConfig(site_name="Test Site", admin_email="admin@test.com")
    await config.insert()
    found = await SystemConfig.find_one()
    assert found is not None
    assert found.site_name == "Test Site"


async def test_system_config_has_required_fields(db):
    """SystemConfig must have site_name and admin_email fields."""
    from core.system.models import SystemConfig
    config = SystemConfig(site_name="DPRS", admin_email="admin@example.com")
    assert config.site_name == "DPRS"
    assert config.admin_email == "admin@example.com"


async def test_system_config_find_one(db):
    """SystemConfig can be retrieved with find_one()."""
    from core.system.models import SystemConfig
    await SystemConfig(site_name="School", admin_email="a@b.com").insert()
    found = await SystemConfig.find_one()
    assert found is not None
    assert found.site_name == "School"
