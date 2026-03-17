import pytest
from sqlalchemy import text
from sqlmodel import SQLModel, Field, select

from shared.database import engine, init_db, get_session

# --- Test Models ---
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None

# --- Tests ---

@pytest.mark.asyncio
async def test_database_connection():
    """Test that the database engine can connect."""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_init_db():
    """Test that init_db creates tables."""
    # Ensure Hero table is registered in metadata
    # (It is automatically registered when defining the class)
    
    await init_db()
    
    async with engine.connect() as conn:
        # Check if table exists (SQLite specific check)
        # For aiosqlite, we can query sqlite_master
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='hero'"))
        table_name = result.scalar()
        assert table_name == 'hero'

@pytest.mark.asyncio
async def test_session_crud():
    """Test Create, Read, Update, Delete with get_session."""
    await init_db()
    
    # Use the generator manually
    session_gen = get_session()
    session = await anext(session_gen)
    
    try:
        # Create
        hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
        session.add(hero_1)
        await session.commit()
        await session.refresh(hero_1)
        assert hero_1.id is not None
        
        # Read
        statement = select(Hero).where(Hero.name == "Deadpond")
        results = await session.exec(statement)
        hero = results.first()
        assert hero is not None
        assert hero.secret_name == "Dive Wilson"
        
        # Update
        hero.age = 48
        session.add(hero)
        await session.commit()
        await session.refresh(hero)
        assert hero.age == 48
        
        # Delete
        await session.delete(hero)
        await session.commit()
        
        statement = select(Hero).where(Hero.name == "Deadpond")
        results = await session.exec(statement)
        hero = results.first()
        assert hero is None
        
    finally:
        await session.close()
