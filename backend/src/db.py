from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(
    settings.db.async_url,
    echo=settings.db.echo,
    pool_pre_ping=True,
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

engine_null_pool = create_async_engine(
    settings.db.async_url,
    poolclass=NullPool,
    echo=settings.db.echo,
)

sessionmaker_null_pool = async_sessionmaker(
    bind=engine_null_pool,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
