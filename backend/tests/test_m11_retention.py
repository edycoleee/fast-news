from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.audit import AuditLog
from app.models.auth_session import AuthSession
from app.models.rate_limit_bucket import RateLimitBucket
from app.modules.operations.retention import RetentionService
from app.modules.settings.service import SettingsService
from conftest import TestSessionLocal, _run_async


def create_old_records(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async def _create() -> None:
        async with session_factory() as session:
            now = datetime.utcnow()
            session.add(
                AuditLog(
                    action='test.old',
                    entity_type='test',
                    created_at=now - timedelta(days=200),
                )
            )
            session.add(
                AuthSession(
                    user_id=1,
                    session_token_hash='a' * 64,
                    csrf_token_hash='b' * 64,
                    expires_at=now + timedelta(hours=1),
                    created_at=now - timedelta(days=2),
                    last_seen_at=now - timedelta(days=2),
                )
            )
            session.add(
                RateLimitBucket(
                    scope='test',
                    identifier='127.0.0.1',
                    window_start=now - timedelta(days=10),
                    count=1,
                )
            )
            await session.commit()

    _run_async(_create())


def test_retention_dry_run_does_not_delete(client, create_user) -> None:
    create_user()
    create_old_records(TestSessionLocal)

    async def _run() -> dict:
        async with TestSessionLocal() as session:
            return await RetentionService(session).cleanup(dry_run=True, batch_size=10)

    report = _run_async(_run())

    assert report['dry_run'] is True
    assert report['eligible']['audit_logs'] == 1
    assert report['eligible']['rate_limit_buckets'] == 1
    assert report['eligible']['auth_sessions'] == 0


def test_retention_cleanup_preserves_active_session(client, create_user) -> None:
    create_user()
    create_old_records(TestSessionLocal)

    async def _run() -> tuple[dict, list]:
        async with TestSessionLocal() as session:
            SettingsService.clear_cache()
            report = await RetentionService(session).cleanup(dry_run=False, batch_size=1)
            sessions = list(
                (await session.execute(select(AuthSession))).scalars().all()
            )
            return report, sessions

    report, sessions = _run_async(_run())

    assert report['deleted']['audit_logs'] == 1
    assert report['deleted']['rate_limit_buckets'] == 1
    assert report['deleted']['auth_sessions'] == 0
    assert len(sessions) == 1
