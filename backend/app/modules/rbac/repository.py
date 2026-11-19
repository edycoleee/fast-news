from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.user_role import RolePermission, UserRole


class RBACRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def get_permission_by_name(self, name: str) -> Permission | None:
        result = await self.db.execute(select(Permission).where(Permission.name == name))
        return result.scalar_one_or_none()

    async def get_role_by_id(self, role_id: int) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_permission_by_id(self, permission_id: int) -> Permission | None:
        result = await self.db.execute(select(Permission).where(Permission.id == permission_id))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_role(self, name: str, description: str | None) -> Role:
        role = Role(name=name, description=description)
        self.db.add(role)
        await self.db.flush()
        return role

    async def create_permission(self, name: str, resource: str, action: str) -> Permission:
        permission = Permission(name=name, resource=resource, action=action)
        self.db.add(permission)
        await self.db.flush()
        return permission

    async def list_roles_paginated(self, *, page: int, page_size: int, search: str | None) -> tuple[list[Role], int]:
        filters = []
        if search:
            normalized_search = f'%{search.strip().lower()}%'
            filters.append(func.lower(Role.name).like(normalized_search))

        list_query = select(Role).order_by(Role.name.asc())
        count_query = select(func.count(Role.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        offset = (page - 1) * page_size
        list_query = list_query.offset(offset).limit(page_size)

        items_result = await self.db.execute(list_query)
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def list_permissions_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Permission], int]:
        filters = []
        if search:
            normalized_search = f'%{search.strip().lower()}%'
            filters.append(
                or_(
                    func.lower(Permission.name).like(normalized_search),
                    func.lower(Permission.resource).like(normalized_search),
                    func.lower(Permission.action).like(normalized_search),
                )
            )

        list_query = select(Permission).order_by(Permission.name.asc())
        count_query = select(func.count(Permission.id))
        if filters:
            list_query = list_query.where(*filters)
            count_query = count_query.where(*filters)

        offset = (page - 1) * page_size
        list_query = list_query.offset(offset).limit(page_size)

        items_result = await self.db.execute(list_query)
        total_result = await self.db.execute(count_query)
        return list(items_result.scalars().all()), int(total_result.scalar_one())

    async def has_role_permission_link(self, role_id: int, permission_id: int) -> bool:
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def assign_permission_to_role(self, role_id: int, permission_id: int) -> None:
        link = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(link)
        await self.db.flush()

    async def list_permissions_by_ids(self, permission_ids: list[int]) -> list[Permission]:
        if not permission_ids:
            return []
        result = await self.db.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        return list(result.scalars().all())

    async def list_role_permission_ids(self, role_id: int) -> list[int]:
        result = await self.db.execute(
            select(RolePermission.permission_id).where(RolePermission.role_id == role_id)
        )
        return list(result.scalars().all())

    async def replace_role_permissions(
        self,
        *,
        role_id: int,
        permission_ids: list[int],
    ) -> tuple[list[int], list[int]]:
        current_ids = set(await self.list_role_permission_ids(role_id))
        requested_ids = set(permission_ids)
        added_ids = sorted(requested_ids - current_ids)
        removed_ids = sorted(current_ids - requested_ids)

        if removed_ids:
            await self.db.execute(
                RolePermission.__table__.delete().where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id.in_(removed_ids),
                )
            )
        if added_ids:
            self.db.add_all(
                RolePermission(role_id=role_id, permission_id=permission_id)
                for permission_id in added_ids
            )
        await self.db.flush()
        return added_ids, removed_ids

    async def delete_role(self, role: Role) -> None:
        await self.db.delete(role)
        await self.db.flush()

    async def delete_permission(self, permission: Permission) -> None:
        await self.db.delete(permission)
        await self.db.flush()

    async def has_user_role_link(self, user_id: int, role_id: int) -> bool:
        result = await self.db.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        return result.scalar_one_or_none() is not None

    async def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        link = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(link)
        await self.db.flush()

    async def list_user_permission_names(self, user_id: int) -> list[str]:
        query = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await self.db.execute(query)
        return sorted([row[0] for row in result.all()])

    async def list_user_role_names(self, user_id: int) -> list[str]:
        query = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await self.db.execute(query)
        return sorted([row[0] for row in result.all()])

    async def list_role_permission_names(self, role_id: int) -> list[str]:
        query = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
            .distinct()
        )
        result = await self.db.execute(query)
        return sorted([row[0] for row in result.all()])

    async def add_audit_log(
        self,
        actor_user_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int | None,
        details: dict | None,
    ) -> None:
        audit_log = AuditLog(
            user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
        self.db.add(audit_log)
        await self.db.flush()
