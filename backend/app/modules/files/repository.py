from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.file_asset import FileAsset
from app.models.signature import Signature


class FileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        original_name: str,
        storage_key: str,
        mime_type: str,
        size_bytes: int,
        uploaded_by: int | None,
        is_public: bool = True,
    ) -> FileAsset:
        file_asset = FileAsset(
            original_name=original_name,
            storage_key=storage_key,
            mime_type=mime_type,
            size_bytes=size_bytes,
            uploaded_by=uploaded_by,
            is_public=is_public,
        )
        self.db.add(file_asset)
        await self.db.flush()
        return file_asset

    async def get_by_id(self, file_id: int) -> FileAsset | None:
        result = await self.db.execute(select(FileAsset).where(FileAsset.id == file_id))
        return result.scalar_one_or_none()

    async def get_public_by_id(self, file_id: int) -> FileAsset | None:
        result = await self.db.execute(
            select(FileAsset).where(FileAsset.id == file_id, FileAsset.is_public.is_(True))
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[FileAsset], int]:
        filters = []
        if search:
            normalized_search = f'%{search.strip().lower()}%'
            filters.append(
                or_(
                    func.lower(FileAsset.original_name).like(normalized_search),
                    func.lower(FileAsset.mime_type).like(normalized_search),
                )
            )

        list_query = select(FileAsset).order_by(FileAsset.created_at.desc())
        count_query = select(func.count(FileAsset.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        offset = (page - 1) * page_size
        list_query = list_query.offset(offset).limit(page_size)

        items_result = await self.db.execute(list_query)
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def delete(self, file_asset: FileAsset) -> None:
        await self.db.delete(file_asset)
        await self.db.flush()

    async def is_referenced_by_signature(self, file_asset_id: int) -> bool:
        result = await self.db.execute(
            select(Signature.id).where(Signature.file_asset_id == file_asset_id).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def add_audit_log(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        entity_id: int | None,
        details: dict | None,
    ) -> None:
        audit_log = AuditLog(
            user_id=actor_user_id,
            action=action,
            entity_type='file_asset',
            entity_id=entity_id,
            details=details,
        )
        self.db.add(audit_log)
        await self.db.flush()
