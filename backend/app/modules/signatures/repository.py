from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.file_asset import FileAsset
from app.models.news import News
from app.models.signature import Signature


class SignatureRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_news_by_id(self, news_id: int) -> News | None:
        result = await self.db.execute(select(News).where(News.id == news_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, signature_id: int) -> Signature | None:
        result = await self.db.execute(select(Signature).where(Signature.id == signature_id))
        return result.scalar_one_or_none()

    async def get_file_asset_by_id(self, file_asset_id: int) -> FileAsset | None:
        result = await self.db.execute(
            select(FileAsset).where(FileAsset.id == file_asset_id)
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: str | None,
    ) -> tuple[list[Signature], int]:
        list_query = select(Signature).order_by(Signature.created_at.desc())
        count_query = select(func.count(Signature.id))
        if status_filter:
            list_query = list_query.where(Signature.status == status_filter)
            count_query = count_query.where(Signature.status == status_filter)

        items_result = await self.db.execute(
            list_query.offset((page - 1) * page_size).limit(page_size)
        )
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def create_file_asset(
        self,
        *,
        storage_key: str,
        original_name: str,
        size_bytes: int,
        uploaded_by: int,
    ) -> FileAsset:
        file_asset = FileAsset(
            original_name=original_name,
            storage_key=storage_key,
            mime_type='image/png',
            size_bytes=size_bytes,
            uploaded_by=uploaded_by,
            is_public=False,
        )
        self.db.add(file_asset)
        await self.db.flush()
        return file_asset

    async def create_signature(
        self,
        *,
        signer_id: int,
        news_id: int | None,
        file_asset_id: int,
        purpose: str,
    ) -> Signature:
        signature = Signature(
            signer_id=signer_id,
            news_id=news_id,
            file_asset_id=file_asset_id,
            purpose=purpose,
            status='active',
        )
        self.db.add(signature)
        await self.db.flush()
        return signature

    async def add_audit_log(
        self,
        *,
        actor_user_id: int,
        action: str,
        entity_id: int,
        details: dict,
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=actor_user_id,
                action=action,
                entity_type='signature',
                entity_id=entity_id,
                details=details,
            )
        )
        await self.db.flush()
