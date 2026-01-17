import pytest_asyncio
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from app.core.config import settings

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

from main import app
from app.db.session import get_session
from app.db.session import Base

# Global variables to hold engine and session factory
async_engine: AsyncEngine | None = None
async_session: async_sessionmaker | None = None


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Create database engine and tables at the start of the testing session.
    This ensures the engine is created in the same event loop as the tests.
    """
    global async_engine, async_session

    # Create async engine in the test session's event loop
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_timeout=30,
        pool_recycle=1800,
        query_cache_size=0,
    )

    # Create async_session from async_engine
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup: delete the database and dispose of the engine after all tests

    await async_engine.dispose()


# Override get_session dependency
async def override_get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:  # type: ignore
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture
async def client():
    BASE_URL = "http://test"
    BASE_PATH = "/api"

    async with AsyncClient(
        transport=ASGITransport(app), base_url=f"{BASE_URL}{BASE_PATH}"
    ) as async_client:
        yield async_client
