from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_setting import AppSetting
from app.models.audit import AuditLog


class SettingsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[AppSetting]:
        result = await self.db.execute(select(AppSetting).order_by(AppSetting.key.asc()))
        return list(result.scalars().all())

    async def get_by_key(self, key: str) -> AppSetting | None:
        result = await self.db.execute(select(AppSetting).where(AppSetting.key == key))
        return result.scalar_one_or_none()

    async def upsert(
        self,
        *,
        key: str,
        category: str,
        value_type: str,
        value: int | bool,
        actor_user_id: int,
    ) -> tuple[AppSetting, object]:
        setting = await self.get_by_key(key)
        previous_value = setting.value if setting is not None else None
        if setting is None:
            setting = AppSetting(
                key=key,
                category=category,
                value=value,
                value_type=value_type,
                updated_by_id=actor_user_id,
            )
            self.db.add(setting)
        else:
            setting.value = value
            setting.updated_by_id = actor_user_id
        await self.db.flush()
        return setting, previous_value

    async def add_audit_log(
        self,
        *,
        actor_user_id: int,
        changes: list[dict],
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=actor_user_id,
                action='settings.update',
                entity_type='app_settings',
                entity_id=None,
                details={'changes': changes},
            )
        )
        await self.db.flush()
