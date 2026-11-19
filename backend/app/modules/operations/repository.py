from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.auth_session import AuthSession
from app.models.rate_limit_bucket import RateLimitBucket


class RetentionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def count_expired_audit(self, cutoff: datetime) -> int:
        result = await self.db.execute(
            select(AuditLog.id).where(AuditLog.created_at < cutoff)
        )
        return len(list(result.scalars().all()))

    async def delete_expired_audit(
        self,
        cutoff: datetime,
        limit: int,
    ) -> int:
        ids_result = await self.db.execute(
            select(AuditLog.id)
            .where(AuditLog.created_at < cutoff)
            .order_by(AuditLog.created_at.asc())
            .limit(limit)
        )
        ids = list(ids_result.scalars().all())
        if not ids:
            return 0
        result = await self.db.execute(delete(AuditLog).where(AuditLog.id.in_(ids)))
        return result.rowcount or 0

    async def count_expired_sessions(self, cutoff: datetime) -> int:
        result = await self.db.execute(
            select(AuthSession.id).where(
                or_(
                    AuthSession.expires_at < cutoff,
                    AuthSession.revoked_at < cutoff,
                )
            )
        )
        return len(list(result.scalars().all()))

    async def delete_expired_sessions(
        self,
        cutoff: datetime,
        limit: int,
    ) -> int:
        ids_result = await self.db.execute(
            select(AuthSession.id)
            .where(
                or_(
                    AuthSession.expires_at < cutoff,
                    AuthSession.revoked_at < cutoff,
                )
            )
            .order_by(AuthSession.created_at.asc())
            .limit(limit)
        )
        ids = list(ids_result.scalars().all())
        if not ids:
            return 0
        result = await self.db.execute(delete(AuthSession).where(AuthSession.id.in_(ids)))
        return result.rowcount or 0

    async def count_expired_rate_limits(self, cutoff: datetime) -> int:
        result = await self.db.execute(
            select(RateLimitBucket.id).where(RateLimitBucket.window_start < cutoff)
        )
        return len(list(result.scalars().all()))

    async def delete_expired_rate_limits(
        self,
        cutoff: datetime,
        limit: int,
    ) -> int:
        ids_result = await self.db.execute(
            select(RateLimitBucket.id)
            .where(RateLimitBucket.window_start < cutoff)
            .order_by(RateLimitBucket.window_start.asc())
            .limit(limit)
        )
        ids = list(ids_result.scalars().all())
        if not ids:
            return 0
        result = await self.db.execute(
            delete(RateLimitBucket).where(RateLimitBucket.id.in_(ids))
        )
        return result.rowcount or 0

    async def add_cleanup_audit(
        self,
        *,
        actor_user_id: int | None = None,
        dry_run: bool,
        report: dict,
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=actor_user_id,
                action='retention.cleanup',
                entity_type='retention',
                entity_id=None,
                details={'dry_run': dry_run, **report},
            )
        )
