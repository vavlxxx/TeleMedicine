from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import sessionmaker
from src.utils.db_tools import DBManager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_db_manager(session: DBSessionDep) -> DBManager:
    return DBManager(session)


DBDep = Annotated[DBManager, Depends(get_db_manager)]
