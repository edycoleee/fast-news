from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.category import Category
from app.models.news import News


class NewsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, news_id: int) -> News | None:
        result = await self.db.execute(select(News).where(News.id == news_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> News | None:
        result = await self.db.execute(select(News).where(News.slug == slug))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[News]:
        result = await self.db.execute(select(News).order_by(News.created_at.desc()))
        return list(result.scalars().all())

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status_filter: str | None,
    ) -> tuple[list[News], int]:
        filters = []
        if search:
            normalized_search = f'%{search.strip().lower()}%'
            filters.append(
                or_(
                    func.lower(News.title).like(normalized_search),
                    func.lower(News.slug).like(normalized_search),
                    func.lower(func.coalesce(News.summary, '')).like(normalized_search),
                )
            )
        if status_filter:
            filters.append(News.status == status_filter.strip().lower())

        list_query = select(News).order_by(News.created_at.desc())
        count_query = select(func.count(News.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        offset = (page - 1) * page_size
        list_query = list_query.offset(offset).limit(page_size)

        items_result = await self.db.execute(list_query)
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def list_published(self) -> list[News]:
        result = await self.db.execute(
            select(News).where(News.status == 'published').order_by(News.published_at.desc(), News.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_published_by_slug(self, slug: str) -> News | None:
        result = await self.db.execute(select(News).where(News.slug == slug, News.status == 'published'))
        return result.scalar_one_or_none()

    async def get_category_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        title: str,
        slug: str,
        summary: str | None,
        content: str,
        status: str,
        author_id: int,
        category_id: int | None,
        published_at,
    ) -> News:
        news = News(
            title=title,
            slug=slug,
            summary=summary,
            content=content,
            status=status,
            author_id=author_id,
            category_id=category_id,
            published_at=published_at,
        )
        self.db.add(news)
        await self.db.flush()
        return news

    async def delete(self, news: News) -> None:
        await self.db.delete(news)
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
            entity_type='news',
            entity_id=entity_id,
            details=details,
        )
        self.db.add(audit_log)
        await self.db.flush()
