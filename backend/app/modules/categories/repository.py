from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Category]:
        result = await self.db.execute(select(Category).order_by(Category.name.asc()))
        return list(result.scalars().all())

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Category], int]:
        filters = []
        if search:
            normalized_search = f'%{search.strip().lower()}%'
            filters.append(
                or_(
                    func.lower(Category.name).like(normalized_search),
                    func.lower(Category.slug).like(normalized_search),
                    func.lower(func.coalesce(Category.description, '')).like(normalized_search),
                )
            )

        list_query = select(Category).order_by(Category.name.asc())
        count_query = select(func.count(Category.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        offset = (page - 1) * page_size
        list_query = list_query.offset(offset).limit(page_size)

        items_result = await self.db.execute(list_query)
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def create(
        self,
        name: str,
        slug: str,
        description: str | None,
        parent_id: int | None,
    ) -> Category:
        category = Category(name=name, slug=slug, description=description, parent_id=parent_id)
        self.db.add(category)
        await self.db.flush()
        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
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
            entity_type='category',
            entity_id=entity_id,
            details=details,
        )
        self.db.add(audit_log)
        await self.db.flush()
