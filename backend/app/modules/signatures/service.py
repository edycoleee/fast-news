from __future__ import annotations

import base64
import binascii
from datetime import datetime
from pathlib import Path
import struct
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.file_asset import FileAsset
from app.models.signature import Signature
from app.modules.settings.service import SettingsService

from .repository import SignatureRepository

PNG_DATA_URL_PREFIX = 'data:image/png;base64,'
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
ALLOWED_SIGNATURE_STATUSES = {'active', 'revoked'}


class SignatureService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = SignatureRepository(db)
        self.settings_service = SettingsService(db)

    async def list_signatures(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: str | None,
    ) -> tuple[list[Signature], int]:
        normalized_status = status_filter.strip().lower() if status_filter else None
        if normalized_status and normalized_status not in ALLOWED_SIGNATURE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid signature status filter.',
            )
        return await self.repository.list_paginated(
            page=page,
            page_size=page_size,
            status_filter=normalized_status,
        )

    async def get_signature(self, signature_id: int) -> Signature:
        signature = await self.repository.get_by_id(signature_id)
        if signature is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Signature not found.',
            )
        return signature

    async def get_signature_file(self, signature_id: int) -> tuple[Signature, FileAsset]:
        signature = await self.get_signature(signature_id)
        file_asset = await self.repository.get_file_asset_by_id(signature.file_asset_id)
        if file_asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Signature evidence file not found.',
            )
        return signature, file_asset

    def get_storage_path(self, file_asset: FileAsset) -> Path:
        storage_path = Path(settings.UPLOAD_DIR) / file_asset.storage_key
        if not storage_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Stored signature file not found.',
            )
        return storage_path

    async def create_signature(
        self,
        *,
        actor_user_id: int,
        purpose: str,
        news_id: int | None,
        signature_data_url: str,
    ) -> Signature:
        if news_id is not None and await self.repository.get_news_by_id(news_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='News not found.')

        png_bytes = await self._decode_png_data_url(signature_data_url)
        self._validate_png_content(png_bytes)

        uploads_dir = Path(settings.UPLOAD_DIR)
        uploads_dir.mkdir(parents=True, exist_ok=True)
        storage_key = f'signature-{uuid.uuid4().hex}.png'
        storage_path = uploads_dir / storage_key
        storage_path.write_bytes(png_bytes)

        try:
            file_asset = await self.repository.create_file_asset(
                storage_key=storage_key,
                original_name=f'{storage_key}',
                size_bytes=len(png_bytes),
                uploaded_by=actor_user_id,
            )
            signature = await self.repository.create_signature(
                signer_id=actor_user_id,
                news_id=news_id,
                file_asset_id=file_asset.id,
                purpose=purpose.strip(),
            )
            await self.repository.add_audit_log(
                actor_user_id=actor_user_id,
                action='signature.create',
                entity_id=signature.id,
                details={
                    'news_id': news_id,
                    'file_asset_id': file_asset.id,
                    'purpose': signature.purpose,
                },
            )
            await self.db.commit()
            return signature
        except Exception:
            await self.db.rollback()
            if storage_path.exists():
                storage_path.unlink()
            raise

    async def revoke_signature(
        self,
        *,
        actor_user_id: int,
        signature_id: int,
        reason: str,
    ) -> Signature:
        signature = await self.get_signature(signature_id)
        if signature.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Signature is already revoked.',
            )

        signature.status = 'revoked'
        signature.revocation_reason = reason.strip()
        signature.revoked_by_id = actor_user_id
        signature.revoked_at = datetime.utcnow()
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='signature.revoke',
            entity_id=signature.id,
            details={'reason': signature.revocation_reason},
        )
        await self.db.commit()
        await self.db.refresh(signature)
        return signature

    async def _decode_png_data_url(self, data_url: str) -> bytes:
        if not data_url.startswith(PNG_DATA_URL_PREFIX):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Signature must be a PNG image.',
            )
        encoded = data_url.removeprefix(PNG_DATA_URL_PREFIX)
        try:
            png_bytes = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid signature image encoding.',
            ) from None
        if not png_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Signature image cannot be empty.',
            )
        max_size = int(await self.settings_service.get_value('signature.max_size_bytes'))
        if len(png_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Signature image exceeds maximum size.',
            )
        return png_bytes

    def _validate_png_content(self, png_bytes: bytes) -> None:
        if not png_bytes.startswith(PNG_SIGNATURE):
            self._raise_invalid_png()

        offset = len(PNG_SIGNATURE)
        found_header = False
        found_end = False
        while offset < len(png_bytes):
            if offset + 12 > len(png_bytes):
                self._raise_invalid_png()
            chunk_size = struct.unpack('>I', png_bytes[offset:offset + 4])[0]
            chunk_type = png_bytes[offset + 4:offset + 8]
            chunk_end = offset + 12 + chunk_size
            if chunk_end > len(png_bytes):
                self._raise_invalid_png()
            if not found_header:
                if chunk_type != b'IHDR' or chunk_size != 13:
                    self._raise_invalid_png()
                width, height = struct.unpack('>II', png_bytes[offset + 8:offset + 16])
                if width <= 0 or height <= 0:
                    self._raise_invalid_png()
                found_header = True
            if chunk_type == b'IEND':
                if chunk_size != 0:
                    self._raise_invalid_png()
                found_end = True
                break
            offset = chunk_end

        if not found_header or not found_end:
            self._raise_invalid_png()

    def _raise_invalid_png(self) -> None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid PNG signature content.',
        )
