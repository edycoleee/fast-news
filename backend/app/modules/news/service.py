from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News

from .repository import NewsRepository
from .sanitizer import has_meaningful_text, sanitize_news_html

ALLOWED_NEWS_STATUS = {'draft', 'published', 'archived'}


class NewsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = NewsRepository(db)

    async def list_news(self) -> list[News]:
        return await self.repository.list_all()

    async def list_news_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status_filter: str | None,
    ) -> tuple[list[News], int]:
        if status_filter and status_filter.strip().lower() not in ALLOWED_NEWS_STATUS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid news status filter.')
        return await self.repository.list_paginated(
            page=page,
            page_size=page_size,
            search=search,
            status_filter=status_filter,
        )

    async def list_public_news(self) -> list[News]:
        news_items = await self.repository.list_published()
        for item in news_items:
            item.content = sanitize_news_html(item.content)
        return news_items

    async def get_news(self, news_id: int) -> News:
        news = await self.repository.get_by_id(news_id)
        if news is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='News not found.')
        return news

    async def get_public_news_by_slug(self, slug: str) -> News:
        news = await self.repository.get_published_by_slug(slug.strip().lower())
        if news is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='News not found.')
        news.content = sanitize_news_html(news.content)
        return news

    async def create_news(
        self,
        actor_user_id: int,
        title: str,
        slug: str,
        summary: str | None,
        content: str,
        status_value: str,
        category_id: int | None,
    ) -> News:
        normalized_status = status_value.strip().lower()
        if normalized_status not in ALLOWED_NEWS_STATUS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid news status.')

        normalized_slug = slug.strip().lower()
        existing_slug = await self.repository.get_by_slug(normalized_slug)
        if existing_slug:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='News slug already exists.')

        if category_id is not None and await self.repository.get_category_by_id(category_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found.')

        sanitized_content = sanitize_news_html(content)
        if not has_meaningful_text(sanitized_content):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='News content cannot be empty.')

        published_at = datetime.utcnow() if normalized_status == 'published' else None
        news = await self.repository.create(
            title=title.strip(),
            slug=normalized_slug,
            summary=summary,
            content=sanitized_content,
            status=normalized_status,
            author_id=actor_user_id,
            category_id=category_id,
            published_at=published_at,
        )
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='news.create',
            entity_id=news.id,
            details={'title': news.title, 'status': news.status},
        )
        await self.db.commit()
        return news

    async def update_news(
        self,
        actor_user_id: int,
        news_id: int,
        title: str | None,
        slug: str | None,
        summary: str | None,
        content: str | None,
        status_value: str | None,
        category_id: int | None,
    ) -> News:
        news = await self.get_news(news_id)

        if title is not None:
            news.title = title.strip()
        if slug is not None:
            normalized_slug = slug.strip().lower()
            existing_slug = await self.repository.get_by_slug(normalized_slug)
            if existing_slug and existing_slug.id != news.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='News slug already exists.')
            news.slug = normalized_slug
        if summary is not None:
            news.summary = summary
        if content is not None:
            sanitized_content = sanitize_news_html(content)
            if not has_meaningful_text(sanitized_content):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='News content cannot be empty.')
            news.content = sanitized_content
        if category_id is not None and await self.repository.get_category_by_id(category_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found.')
        news.category_id = category_id

        if status_value is not None:
            normalized_status = status_value.strip().lower()
            if normalized_status not in ALLOWED_NEWS_STATUS:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid news status.')
            news.status = normalized_status
            if normalized_status == 'published' and news.published_at is None:
                news.published_at = datetime.utcnow()
            if normalized_status != 'published':
                news.published_at = None

        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='news.update',
            entity_id=news.id,
            details={'title': news.title, 'status': news.status},
        )
        await self.db.commit()
        await self.db.refresh(news)
        return news

    async def delete_news(self, actor_user_id: int, news_id: int) -> None:
        news = await self.get_news(news_id)
        await self.repository.delete(news)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='news.delete',
            entity_id=news_id,
            details={'title': news.title},
        )
        await self.db.commit()
