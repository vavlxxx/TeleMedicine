from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.v1.dependencies.db import get_db
from src.main import app
from src.models.base import Base

TEST_DB_PATH = Path("./test_virtualmedic.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH.as_posix()}"

engine = create_async_engine(TEST_DB_URL, future=True)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database() -> AsyncGenerator[None, None]:
    app.dependency_overrides[get_db] = override_get_db
    original_sessionmaker = app.state.db_sessionmaker
    app.state.db_sessionmaker = TestingSessionLocal
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def _noop_lifespan(_):
        yield

    app.router.lifespan_context = _noop_lifespan

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    app.dependency_overrides.clear()
    app.state.db_sessionmaker = original_sessionmaker
    app.router.lifespan_context = original_lifespan

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
    TEST_DB_PATH.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
async def clear_database() -> AsyncGenerator[None, None]:
    async with TestingSessionLocal() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(delete(table))
        await session.commit()
    yield


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        yield client
