from __future__ import annotations

from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.file_asset import FileAsset

from .repository import FileRepository

ALLOWED_UPLOAD_MIME_TYPES = {
    'application/pdf': '.pdf',
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/webp': '.webp',
}

IMAGE_MIME_SIGNATURES = {
    'image/png': [b'\x89PNG\r\n\x1a\n'],
    'image/jpeg': [b'\xff\xd8\xff'],
    'image/webp': [b'RIFF'],
}


class FileService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = FileRepository(db)

    async def list_files_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[FileAsset], int]:
        return await self.repository.list_paginated(page=page, page_size=page_size, search=search)

    async def get_file_asset(self, file_id: int) -> FileAsset:
        file_asset = await self.repository.get_by_id(file_id)
        if file_asset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found.')
        return file_asset

    async def upload_file(self, *, actor_user_id: int, upload_file: UploadFile) -> FileAsset:
        mime_type = (upload_file.content_type or '').strip().lower()
        if mime_type not in ALLOWED_UPLOAD_MIME_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsupported file type.')

        file_bytes = await upload_file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File cannot be empty.')
        if len(file_bytes) > settings.UPLOAD_MAX_SIZE_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File exceeds maximum size.')

        self._validate_file_content(mime_type=mime_type, file_bytes=file_bytes)

        uploads_dir = Path(settings.UPLOAD_DIR)
        uploads_dir.mkdir(parents=True, exist_ok=True)
        file_extension = ALLOWED_UPLOAD_MIME_TYPES[mime_type]
        storage_key = f'{uuid.uuid4().hex}{file_extension}'
        storage_path = uploads_dir / storage_key
        storage_path.write_bytes(file_bytes)

        try:
            file_asset = await self.repository.create(
                original_name=upload_file.filename or storage_key,
                storage_key=storage_key,
                mime_type=mime_type,
                size_bytes=len(file_bytes),
                uploaded_by=actor_user_id,
            )
            await self.repository.add_audit_log(
                actor_user_id=actor_user_id,
                action='file.upload',
                entity_id=file_asset.id,
                details={'original_name': file_asset.original_name, 'mime_type': file_asset.mime_type},
            )
            await self.db.commit()
            return file_asset
        except Exception:
            if storage_path.exists():
                storage_path.unlink()
            raise

    async def delete_file(self, *, actor_user_id: int, file_id: int) -> None:
        file_asset = await self.get_file_asset(file_id)
        storage_path = Path(settings.UPLOAD_DIR) / file_asset.storage_key
        await self.repository.delete(file_asset)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='file.delete',
            entity_id=file_id,
            details={'original_name': file_asset.original_name},
        )
        await self.db.commit()
        if storage_path.exists():
            storage_path.unlink()

    def get_storage_path(self, file_asset: FileAsset) -> Path:
        storage_path = Path(settings.UPLOAD_DIR) / file_asset.storage_key
        if not storage_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stored file not found.')
        return storage_path

    def _validate_file_content(self, *, mime_type: str, file_bytes: bytes) -> None:
        if mime_type == 'application/pdf':
            if not file_bytes.startswith(b'%PDF-'):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid PDF file content.')
            return

        signatures = IMAGE_MIME_SIGNATURES[mime_type]
        if not any(file_bytes.startswith(signature) for signature in signatures):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid image file content.')
        if mime_type == 'image/webp' and b'WEBP' not in file_bytes[:16]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid image file content.')
