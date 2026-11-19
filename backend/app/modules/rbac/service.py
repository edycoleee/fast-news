from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.models.permission import Permission
from app.models.role import Role

from .repository import RBACRepository
from .permission_registry import get_registered_permission_names


class RBACService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = RBACRepository(db)

    async def create_role(
        self,
        actor_user_id: int,
        name: str,
        description: str | None,
    ) -> Role:
        normalized_name = name.strip().lower()
        existing_role = await self.repository.get_role_by_name(normalized_name)
        if existing_role:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role already exists.')

        role = await self.repository.create_role(name=normalized_name, description=description)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.role.create',
            entity_type='role',
            entity_id=role.id,
            details={'name': role.name},
        )
        await self.db.commit()
        return role

    async def list_roles_paginated(self, *, page: int, page_size: int, search: str | None) -> tuple[list[Role], int]:
        return await self.repository.list_roles_paginated(page=page, page_size=page_size, search=search)

    async def list_permissions_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Permission], int]:
        return await self.repository.list_permissions_paginated(page=page, page_size=page_size, search=search)

    async def create_permission(
        self,
        actor_user_id: int,
        name: str,
        resource: str,
        action: str,
    ) -> Permission:
        normalized_name = name.strip().lower()
        existing_permission = await self.repository.get_permission_by_name(normalized_name)
        if existing_permission:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Permission already exists.')

        permission = await self.repository.create_permission(
            name=normalized_name,
            resource=resource.strip().lower(),
            action=action.strip().lower(),
        )
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.permission.create',
            entity_type='permission',
            entity_id=permission.id,
            details={'name': permission.name},
        )
        await self.db.commit()
        return permission

    async def update_role(
        self,
        *,
        actor_user_id: int,
        role_id: int,
        name: str | None,
        description: str | None,
    ) -> Role:
        role = await self.repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found.')

        if name is not None:
            normalized_name = name.strip().lower()
            existing_role = await self.repository.get_role_by_name(normalized_name)
            if existing_role and existing_role.id != role.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role already exists.')
            role.name = normalized_name

        role.description = description
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.role.update',
            entity_type='role',
            entity_id=role.id,
            details={'name': role.name},
        )
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update_permission(
        self,
        *,
        actor_user_id: int,
        permission_id: int,
        name: str | None,
        resource: str | None,
        action: str | None,
    ) -> Permission:
        permission = await self.repository.get_permission_by_id(permission_id)
        if permission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found.')
        if permission.name in get_registered_permission_names():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Registry-managed permission cannot be changed through RBAC API.',
            )

        if name is not None:
            normalized_name = name.strip().lower()
            existing_permission = await self.repository.get_permission_by_name(normalized_name)
            if existing_permission and existing_permission.id != permission.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Permission already exists.')
            permission.name = normalized_name

        if resource is not None:
            permission.resource = resource.strip().lower()
        if action is not None:
            permission.action = action.strip().lower()

        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.permission.update',
            entity_type='permission',
            entity_id=permission.id,
            details={'name': permission.name},
        )
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def assign_permission_to_role(
        self,
        actor_user_id: int,
        role_id: int,
        permission_id: int,
    ) -> None:
        role = await self.repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found.')

        permission = await self.repository.get_permission_by_id(permission_id)
        if permission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found.')

        if await self.repository.has_role_permission_link(role_id=role_id, permission_id=permission_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role permission already assigned.')

        await self.repository.assign_permission_to_role(role_id=role_id, permission_id=permission_id)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.role.assign_permission',
            entity_type='role_permission',
            entity_id=None,
            details={'role_id': role_id, 'permission_id': permission_id},
        )
        await self.db.commit()

    async def assign_role_to_user(
        self,
        actor_user_id: int,
        user_id: int,
        role_id: int,
    ) -> None:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')

        role = await self.repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found.')

        if await self.repository.has_user_role_link(user_id=user_id, role_id=role_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User role already assigned.')

        await self.repository.assign_role_to_user(user_id=user_id, role_id=role_id)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.user.assign_role',
            entity_type='user_role',
            entity_id=None,
            details={'user_id': user_id, 'role_id': role_id},
        )
        await self.db.commit()

    async def replace_role_permissions(
        self,
        *,
        actor_user_id: int,
        role_id: int,
        permission_ids: list[int],
    ) -> list[str]:
        role = await self.repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found.')

        unique_permission_ids = sorted(set(permission_ids))
        permissions = await self.repository.list_permissions_by_ids(unique_permission_ids)
        if len(permissions) != len(unique_permission_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='One or more permissions do not exist.',
            )

        added_ids, removed_ids = await self.repository.replace_role_permissions(
            role_id=role_id,
            permission_ids=unique_permission_ids,
        )
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.role.replace_permissions',
            entity_type='role',
            entity_id=role_id,
            details={
                'role': role.name,
                'permission_ids': unique_permission_ids,
                'added_ids': added_ids,
                'removed_ids': removed_ids,
            },
        )
        await self.db.commit()
        return await self.repository.list_role_permission_names(role_id)

    async def delete_role(self, *, actor_user_id: int, role_id: int) -> None:
        role = await self.repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found.')
        await self.repository.delete_role(role)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.role.delete',
            entity_type='role',
            entity_id=role_id,
            details={'name': role.name},
        )
        await self.db.commit()

    async def delete_permission(self, *, actor_user_id: int, permission_id: int) -> None:
        permission = await self.repository.get_permission_by_id(permission_id)
        if permission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found.')
        if permission.name in get_registered_permission_names():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Registry-managed permission cannot be deleted through RBAC API.',
            )
        await self.repository.delete_permission(permission)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='rbac.permission.delete',
            entity_type='permission',
            entity_id=permission_id,
            details={'name': permission.name},
        )
        await self.db.commit()

    async def list_user_permissions(self, user_id: int) -> list[str]:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
        return await self.repository.list_user_permission_names(user_id=user_id)

    async def list_user_roles(self, user_id: int) -> list[str]:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
        return await self.repository.list_user_role_names(user_id=user_id)

    async def list_role_permissions(self, role_id: int) -> list[str]:
        role = await self.repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found.')
        return await self.repository.list_role_permission_names(role_id=role_id)

    async def ensure_user_has_permission(self, auth_session: AuthSession, permission_name: str) -> None:
        user_permissions = await self.repository.list_user_permission_names(user_id=auth_session.user_id)
        if permission_name not in user_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden.')

    async def ensure_user_has_any_permission(self, auth_session: AuthSession, permission_names: list[str]) -> None:
        if not permission_names:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden.')

        user_permissions = await self.repository.list_user_permission_names(user_id=auth_session.user_id)
        if not any(permission_name in user_permissions for permission_name in permission_names):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden.')
