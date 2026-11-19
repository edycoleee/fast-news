from __future__ import annotations

from datetime import datetime

import bleach
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.modules.settings.service import SettingsService

from .repository import CommentRepository

ALLOWED_STATUSES = {'pending', 'approved', 'rejected'}


class CommentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = CommentRepository(db)
        self.settings_service = SettingsService(db)

    async def list_public_comments(self, slug: str) -> list[Comment]:
        news = await self.repository.get_published_news_by_slug(slug.strip().lower())
        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Published news not found.',
            )
        return await self.repository.list_approved(news_id=news.id)

    async def submit_public_comment(
        self,
        *,
        slug: str,
        author_name: str,
        content: str,
        parent_id: int | None,
    ) -> Comment:
        news = await self.repository.get_published_news_by_slug(slug.strip().lower())
        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Published news not found.',
            )

        if parent_id is not None:
            parent = await self.repository.get_comment_by_id(parent_id)
            if (
                parent is None
                or parent.news_id != news.id
                or parent.status != 'approved'
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Parent comment is invalid.',
                )

        clean_name = bleach.clean(author_name, tags=set(), strip=True).strip()
        clean_content = bleach.clean(content, tags=set(), strip=True).strip()
        max_length = int(await self.settings_service.get_value('comment.max_length'))
        if len(clean_content) > max_length:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'Comment cannot exceed {max_length} characters.',
            )
        if len(clean_name) < 2 or len(clean_content) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Name or comment content is invalid.',
            )

        comment = await self.repository.create(
            news_id=news.id,
            author_name=clean_name,
            content=clean_content,
            parent_id=parent_id,
        )
        await self.repository.add_audit_log(
            actor_user_id=None,
            action='comment.submit',
            comment_id=comment.id,
            details={'news_id': news.id},
        )
        await self.db.commit()
        return comment

    async def list_comments(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: str | None,
    ) -> tuple[list[Comment], int]:
        normalized_status = status_filter.strip().lower() if status_filter else None
        if normalized_status and normalized_status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid comment status filter.',
            )
        return await self.repository.list_paginated(
            page=page,
            page_size=page_size,
            status_filter=normalized_status,
        )

    async def moderate_comment(
        self,
        *,
        actor_user_id: int,
        comment_id: int,
        target_status: str,
        note: str | None,
    ) -> Comment:
        comment = await self._get_comment(comment_id)
        normalized_status = target_status.strip().lower()
        if normalized_status not in {'approved', 'rejected'}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid moderation status.',
            )
        if comment.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Comment is already moderated.',
            )

        comment.status = normalized_status
        comment.moderation_note = bleach.clean(note or '', tags=set(), strip=True).strip() or None
        comment.moderated_by_id = actor_user_id
        comment.moderated_at = datetime.utcnow()
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action=f'comment.{normalized_status}',
            comment_id=comment.id,
            details={
                'news_id': comment.news_id,
                'note': comment.moderation_note,
            },
        )
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete_comment(
        self,
        *,
        actor_user_id: int,
        comment_id: int,
    ) -> None:
        comment = await self._get_comment(comment_id)
        await self.repository.delete(comment)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='comment.delete',
            comment_id=comment_id,
            details={'news_id': comment.news_id, 'previous_status': comment.status},
        )
        await self.db.commit()

    async def _get_comment(self, comment_id: int) -> Comment:
        comment = await self.repository.get_comment_by_id(comment_id)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Comment not found.',
            )
        return comment
