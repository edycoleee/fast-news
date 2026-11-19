from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from .definitions import DEFINITIONS, DEFINITIONS_BY_KEY
from .repository import SettingsRepository
from .schemas import RuntimeSettingResponse

_cache: dict[str, int | bool] = {}
_cache_expiration: datetime | None = None


class SettingsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = SettingsRepository(db)

    async def list_settings(self) -> list[RuntimeSettingResponse]:
        stored = {setting.key: setting.value for setting in await self.repository.list_all()}
        return [
            RuntimeSettingResponse(
                key=definition.key,
                category=definition.category,
                label=definition.label,
                value_type=definition.value_type,
                value=stored.get(definition.key, definition.default),
                minimum=definition.minimum,
                maximum=definition.maximum,
                is_default=definition.key not in stored,
            )
            for definition in DEFINITIONS
        ]

    async def get_value(self, key: str) -> int | bool:
        global _cache, _cache_expiration
        definition = DEFINITIONS_BY_KEY.get(key)
        if definition is None:
            raise RuntimeError(f'Unknown setting key: {key}')
        now = datetime.utcnow()
        if _cache_expiration is None or now >= _cache_expiration:
            stored = await self.repository.list_all()
            _cache = {
                setting.key: definition_for_setting.validate(setting.value)
                for setting in stored
                if (definition_for_setting := DEFINITIONS_BY_KEY.get(setting.key))
            }
            _cache_expiration = now + timedelta(seconds=settings.SECURITY_SETTINGS_CACHE_SECONDS)
        return _cache.get(key, definition.default)

    async def update_settings(
        self,
        *,
        actor_user_id: int,
        updates: list[dict],
    ) -> list[RuntimeSettingResponse]:
        seen_keys: set[str] = set()
        validated_updates: list[tuple[str, int | bool]] = []
        for update in updates:
            key = update['key']
            if key in seen_keys:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Duplicate setting key: {key}',
                )
            definition = DEFINITIONS_BY_KEY.get(key)
            if definition is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Unknown setting key: {key}',
                )
            try:
                value = definition.validate(update['value'])
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                ) from None
            seen_keys.add(key)
            validated_updates.append((key, value))

        changes: list[dict] = []
        try:
            for key, value in validated_updates:
                definition = DEFINITIONS_BY_KEY[key]
                _, previous_value = await self.repository.upsert(
                    key=key,
                    category=definition.category,
                    value_type=definition.value_type,
                    value=value,
                    actor_user_id=actor_user_id,
                )
                changes.append({
                    'key': key,
                    'previous': previous_value,
                    'current': value,
                })
            await self.repository.add_audit_log(
                actor_user_id=actor_user_id,
                changes=changes,
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        self.clear_cache()
        return await self.list_settings()

    @staticmethod
    def clear_cache() -> None:
        global _cache_expiration
        _cache_expiration = None
