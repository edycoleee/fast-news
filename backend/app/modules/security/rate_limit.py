from __future__ import annotations

from datetime import datetime, timedelta
import hashlib

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.settings.service import SettingsService

from .repository import RateLimitRepository


class RateLimitService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = RateLimitRepository(db)
        self.settings_service = SettingsService(db)

    async def check_login(
        self,
        *,
        request: Request,
        identifier: str,
    ) -> None:
        ip_address = request.client.host if request.client else 'unknown'
        limit = int(await self.settings_service.get_value('login.rate_limit_per_minute'))
        count = await self._consume(
            scope='login_requests',
            identifier=ip_address,
            limit=limit,
            window_seconds=60,
        )
        if count > limit:
            raise self._too_many_requests('Too many login attempts.', retry_after=60)

        cooldown_seconds = int(await self.settings_service.get_value('login.cooldown_seconds'))
        threshold = int(await self.settings_service.get_value('login.failure_threshold'))
        account_key = self._hash_identifier(identifier)
        failure_count = await self.repository.get_count_since(
            scope='login_failures',
            identifier=account_key,
            since=datetime.utcnow() - timedelta(seconds=cooldown_seconds),
        )
        if failure_count >= threshold:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail='Account temporarily locked after repeated failures.',
                headers={'Retry-After': str(cooldown_seconds)},
            )

    async def record_login_failure(self, identifier: str) -> None:
        cooldown_seconds = int(await self.settings_service.get_value('login.cooldown_seconds'))
        await self.repository.increment(
            scope='login_failures',
            identifier=self._hash_identifier(identifier),
            window_start=self._window_start(cooldown_seconds),
        )
        await self.db.commit()

    async def clear_login_failures(self, identifier: str) -> None:
        await self.repository.reset_scope(
            scope='login_failures',
            identifier=self._hash_identifier(identifier),
        )
        await self.db.commit()

    async def check_public_comment(self, request: Request) -> None:
        limit = int(await self.settings_service.get_value('comment.rate_limit_per_hour'))
        count = await self._consume(
            scope='public_comments',
            identifier=request.client.host if request.client else 'unknown',
            limit=limit,
            window_seconds=3600,
        )
        if count > limit:
            raise self._too_many_requests('Comment rate limit exceeded.', retry_after=3600)

    async def check_upload(self, user_id: int) -> None:
        limit = int(await self.settings_service.get_value('upload.rate_limit_per_hour'))
        count = await self._consume(
            scope='uploads',
            identifier=str(user_id),
            limit=limit,
            window_seconds=3600,
        )
        if count > limit:
            raise self._too_many_requests('Upload rate limit exceeded.', retry_after=3600)

    async def _consume(
        self,
        *,
        scope: str,
        identifier: str,
        limit: int,
        window_seconds: int,
    ) -> int:
        count = await self.repository.increment(
            scope=scope,
            identifier=identifier,
            window_start=self._window_start(window_seconds),
        )
        await self.db.commit()
        return count

    @staticmethod
    def _window_start(window_seconds: int) -> datetime:
        now = datetime.utcnow()
        epoch = int(now.timestamp())
        bucket_epoch = epoch - (epoch % window_seconds)
        return datetime.utcfromtimestamp(bucket_epoch)

    @staticmethod
    def _hash_identifier(identifier: str) -> str:
        return hashlib.sha256(identifier.strip().lower().encode('utf-8')).hexdigest()

    @staticmethod
    def _too_many_requests(detail: str, *, retry_after: int) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={'Retry-After': str(retry_after)},
        )
