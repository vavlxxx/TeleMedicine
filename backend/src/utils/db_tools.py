from typing import Iterable

from sqlalchemy import Connection, inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from src.models.base import Base
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DBHealthChecker:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def check(self) -> None:
        async with self.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            is_exists, missing = await conn.run_sync(self._check_tables_existence)
            if not is_exists:
                missing_msg = ", ".join(sorted(missing))
                raise RuntimeError(f"Missing DB tables: {missing_msg}")

    def _check_tables_existence(self, conn: Connection) -> tuple[bool, set[str]]:
        inspector = inspect(conn)
        existing_tables = set(inspector.get_table_names())
        expected_tables = set(Base.metadata.tables.keys())
        missing_tables = expected_tables - existing_tables

        logger.info("Checking database tables...")
        self._log_table_state(expected_tables, existing_tables)
        return len(missing_tables) == 0, missing_tables

    @staticmethod
    def _log_table_state(expected_tables: Iterable[str], existing_tables: set[str]) -> None:
        for table in sorted(expected_tables):
            if table in existing_tables:
                logger.info("(+) %s", table)
            else:
                logger.error("(-) %s", table)
