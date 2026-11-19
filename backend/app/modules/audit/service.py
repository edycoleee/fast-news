from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog

from .repository import AuditRepository


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = AuditRepository(db)

    async def list_logs(
        self,
        *,
        page: int,
        page_size: int,
        action: str | None,
        user_id: int | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[list[AuditLog], int]:
        if date_from and date_to and date_from > date_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='date_from cannot be after date_to.',
            )
        return await self.repository.list_paginated(
            page=page,
            page_size=page_size,
            action=action,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
