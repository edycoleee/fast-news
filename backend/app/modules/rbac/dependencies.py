from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import get_current_auth_session

from .service import RBACService


def get_rbac_service(db: AsyncSession = Depends(get_db)) -> RBACService:
    return RBACService(db)


def require_permission(permission_name: str) -> Callable:
    async def _dependency(
        auth_session: AuthSession = Depends(get_current_auth_session),
        rbac_service: RBACService = Depends(get_rbac_service),
    ) -> AuthSession:
        await rbac_service.ensure_user_has_permission(
            auth_session=auth_session,
            permission_name=permission_name,
        )
        return auth_session

    return _dependency


def require_any_permission(permission_names: list[str]) -> Callable:
    async def _dependency(
        auth_session: AuthSession = Depends(get_current_auth_session),
        rbac_service: RBACService = Depends(get_rbac_service),
    ) -> AuthSession:
        await rbac_service.ensure_user_has_any_permission(
            auth_session=auth_session,
            permission_names=permission_names,
        )
        return auth_session

    return _dependency
