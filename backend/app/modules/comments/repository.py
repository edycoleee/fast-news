from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.comment import Comment
from app.models.news import News


class CommentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_published_news_by_slug(self, slug: str) -> News | None:
        result = await self.db.execute(
            select(News).where(News.slug == slug, News.status == 'published')
        )
        return result.scalar_one_or_none()

    async def get_comment_by_id(self, comment_id: int) -> Comment | None:
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def list_approved(self, *, news_id: int) -> list[Comment]:
        result = await self.db.execute(
            select(Comment)
            .where(Comment.news_id == news_id, Comment.status == 'approved')
            .order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: str | None,
    ) -> tuple[list[Comment], int]:
        list_query = select(Comment).order_by(Comment.created_at.desc())
        count_query = select(func.count(Comment.id))
        if status_filter:
            list_query = list_query.where(Comment.status == status_filter)
            count_query = count_query.where(Comment.status == status_filter)

        items_result = await self.db.execute(
            list_query.offset((page - 1) * page_size).limit(page_size)
        )
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def create(
        self,
        *,
        news_id: int,
        author_name: str,
        content: str,
        parent_id: int | None,
    ) -> Comment:
        comment = Comment(
            news_id=news_id,
            user_id=None,
            parent_id=parent_id,
            author_name=author_name,
            content=content,
            status='pending',
        )
        self.db.add(comment)
        await self.db.flush()
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.db.delete(comment)
        await self.db.flush()

    async def add_audit_log(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        comment_id: int,
        details: dict,
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=actor_user_id,
                action=action,
                entity_type='comment',
                entity_id=comment_id,
                details=details,
            )
        )
        await self.db.flush()
