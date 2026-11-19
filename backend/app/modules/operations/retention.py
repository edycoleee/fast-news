from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.settings.service import SettingsService

from .repository import RetentionRepository


class RetentionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = RetentionRepository(db)
        self.settings_service = SettingsService(db)

    async def cleanup(
        self,
        *,
        dry_run: bool,
        batch_size: int = 1000,
        actor_user_id: int | None = None,
    ) -> dict:
        now = datetime.utcnow()
        audit_days = int(
            await self.settings_service.get_value('retention.audit_log_days')
        )
        session_days = int(
            await self.settings_service.get_value('retention.auth_session_days')
        )
        rate_limit_days = int(
            await self.settings_service.get_value('retention.rate_limit_days')
        )
        cutoff = {
            'audit_logs': now - timedelta(days=audit_days),
            'auth_sessions': now - timedelta(days=session_days),
            'rate_limit_buckets': now - timedelta(days=rate_limit_days),
        }

        counts = {
            'audit_logs': await self.repository.count_expired_audit(cutoff['audit_logs']),
            'auth_sessions': await self.repository.count_expired_sessions(cutoff['auth_sessions']),
            'rate_limit_buckets': await self.repository.count_expired_rate_limits(
                cutoff['rate_limit_buckets']
            ),
        }
        deleted = dict.fromkeys(counts, 0)
        if not dry_run:
            remaining = dict(counts)
            while any(remaining.values()):
                for name in ('audit_logs', 'auth_sessions', 'rate_limit_buckets'):
                    if remaining[name] <= 0:
                        continue
                    if name == 'audit_logs':
                        count = await self.repository.delete_expired_audit(
                            cutoff[name], batch_size
                        )
                    elif name == 'auth_sessions':
                        count = await self.repository.delete_expired_sessions(
                            cutoff[name], batch_size
                        )
                    else:
                        count = await self.repository.delete_expired_rate_limits(
                            cutoff[name], batch_size
                        )
                    deleted[name] += count
                    remaining[name] -= count
            await self.repository.add_cleanup_audit(
                actor_user_id=actor_user_id,
                dry_run=False,
                report=deleted,
            )
            await self.db.commit()

        return {
            'dry_run': dry_run,
            'eligible': counts,
            'deleted': deleted,
            'cutoff': {key: value.isoformat() for key, value in cutoff.items()},
        }
