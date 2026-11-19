from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        action: str | None,
        user_id: int | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[list[AuditLog], int]:
        filters = []
        if action:
            filters.append(AuditLog.action.like(f'%{action.strip().lower()}%'))
        if user_id is not None:
            filters.append(AuditLog.user_id == user_id)
        if date_from is not None:
            filters.append(AuditLog.created_at >= date_from)
        if date_to is not None:
            filters.append(AuditLog.created_at <= date_to)

        list_query = select(AuditLog).order_by(AuditLog.created_at.desc())
        count_query = select(func.count(AuditLog.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        result = await self.db.execute(
            list_query.offset((page - 1) * page_size).limit(page_size)
        )
        count_result = await self.db.execute(count_query)
        return list(result.scalars().all()), int(count_result.scalar_one())
