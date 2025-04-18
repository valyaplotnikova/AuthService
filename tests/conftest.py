from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from app.database.base import Base
from app.core.config import settings
from app.main import app as main_app


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=main_app), base_url="http://test",) as client:
        yield client


@pytest.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    engine = create_async_engine(settings.get_db_url_async)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def session(engine, setup_db):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
