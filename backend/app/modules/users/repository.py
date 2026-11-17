from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[User], int]:
        filters = []
        if search:
            normalized_search = f'%{search.strip().lower()}%'
            filters.append(
                or_(
                    func.lower(User.username).like(normalized_search),
                    func.lower(User.email).like(normalized_search),
                )
            )

        list_query = select(User).order_by(User.created_at.desc())
        count_query = select(func.count(User.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        offset = (page - 1) * page_size
        list_query = list_query.offset(offset).limit(page_size)

        items_result = await self.db.execute(list_query)
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def create(self, *, username: str, email: str, password_hash: str, is_active: bool) -> User:
        user = User(username=username, email=email, password_hash=password_hash, is_active=is_active)
        self.db.add(user)
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()

    async def add_audit_log(
        self,
        actor_user_id: int | None,
        action: str,
        entity_id: int | None,
        details: dict | None,
    ) -> None:
        audit_log = AuditLog(
            user_id=actor_user_id,
            action=action,
            entity_type='user',
            entity_id=entity_id,
            details=details,
        )
        self.db.add(audit_log)
        await self.db.flush()
