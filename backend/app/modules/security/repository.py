from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.models.rate_limit_bucket import RateLimitBucket


class RateLimitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def increment(
        self,
        *,
        scope: str,
        identifier: str,
        window_start: datetime,
    ) -> int:
        table = RateLimitBucket.__table__
        values = {
            'scope': scope,
            'identifier': identifier,
            'window_start': window_start,
            'count': 1,
        }
        dialect = self.db.bind.dialect.name
        insert_statement = postgres_insert(table) if dialect == 'postgresql' else sqlite_insert(table)
        statement = (
            insert_statement.values(**values)
            .on_conflict_do_update(
                index_elements=['scope', 'identifier', 'window_start'],
                set_={
                    'count': table.c.count + 1,
                    'updated_at': datetime.utcnow(),
                },
            )
            .returning(table.c.count)
        )
        result = await self.db.execute(statement)
        return int(result.scalar_one())

    async def get_count(
        self,
        *,
        scope: str,
        identifier: str,
        window_start: datetime,
    ) -> int:
        result = await self.db.execute(
            select(RateLimitBucket.count).where(
                RateLimitBucket.scope == scope,
                RateLimitBucket.identifier == identifier,
                RateLimitBucket.window_start == window_start,
            )
        )
        return int(result.scalar_one_or_none() or 0)

    async def get_count_since(
        self,
        *,
        scope: str,
        identifier: str,
        since: datetime,
    ) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(RateLimitBucket.count), 0)).where(
                RateLimitBucket.scope == scope,
                RateLimitBucket.identifier == identifier,
                RateLimitBucket.window_start >= since,
            )
        )
        return int(result.scalar_one())

    async def reset_scope(self, *, scope: str, identifier: str) -> None:
        await self.db.execute(
            delete(RateLimitBucket).where(
                RateLimitBucket.scope == scope,
                RateLimitBucket.identifier == identifier,
            )
        )
