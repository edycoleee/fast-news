from __future__ import annotations

import os
from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.user_role import RolePermission, UserRole
from app.modules.auth.security import hash_password
from app.modules.rbac.permission_registry import get_registered_permissions


def main() -> None:
    database_url = os.environ.get('DATABASE_URL')
    superadmin_username = os.environ.get('SUPERADMIN_USERNAME')
    superadmin_email = os.environ.get('SUPERADMIN_EMAIL')
    superadmin_password = os.environ.get('SUPERADMIN_PASSWORD')

    if not database_url:
        raise RuntimeError('DATABASE_URL is required.')
    if not superadmin_username or not superadmin_email or not superadmin_password:
        raise RuntimeError('SUPERADMIN_USERNAME, SUPERADMIN_EMAIL, and SUPERADMIN_PASSWORD are required.')

    username = superadmin_username.strip().lower()
    email = superadmin_email.strip().lower()
    engine = create_engine(database_url)

    with Session(engine) as session:
        user = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user is None:
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(superadmin_password),
                is_active=True,
            )
            session.add(user)
            session.flush()

        role = session.execute(select(Role).where(Role.name == 'superadmin')).scalar_one_or_none()
        if role is None:
            role = Role(name='superadmin', description='System superadmin role')
            session.add(role)
            session.flush()

        for definition in get_registered_permissions():
            permission = session.execute(
                select(Permission).where(Permission.name == definition.name)
            ).scalar_one_or_none()
            if permission is None:
                permission = Permission(
                    name=definition.name,
                    resource=definition.resource,
                    action=definition.action,
                )
                session.add(permission)
                session.flush()

            role_permission = session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            ).scalar_one_or_none()
            if role_permission is None:
                session.add(RolePermission(role_id=role.id, permission_id=permission.id))

        user_role = session.execute(
            select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
        ).scalar_one_or_none()
        if user_role is None:
            session.add(UserRole(user_id=user.id, role_id=role.id))

        session.commit()
        print(f'Superadmin ready: {user.email} (role: superadmin)')


if __name__ == '__main__':
    main()
