"""Async PostgreSQL database client for MantraAssist (assist_db)."""

import logging
from typing import Any

import asyncpg

from livekit_mcp.config import Settings

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Async database client managing asyncpg connection pool to assist_db."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.db_url = settings.effective_db_url
        self._pool: asyncpg.Pool | None = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or initialize the asyncpg connection pool."""
        if self._pool is None or self._pool._closed:
            logger.info("Initializing asyncpg connection pool to assist_db")
            self._pool = await asyncpg.create_pool(
                dsn=self.db_url,
                min_size=1,
                max_size=10,
                command_timeout=10.0,
            )
        return self._pool

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        """Execute a query and return all matching rows."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        """Execute a query and return a single row."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool and not self._pool._closed:
            logger.info("Closing asyncpg connection pool")
            await self._pool.close()
            self._pool = None
