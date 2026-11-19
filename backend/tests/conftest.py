from __future__ import annotations

import asyncio
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import *  # noqa: F401,F403
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.user_role import RolePermission, UserRole
from app.modules.auth.security import hash_password
from app.modules.settings.service import SettingsService

TEST_DB_PATH = Path(__file__).parent / 'test_auth.db'
TEST_DATABASE_URL = f'sqlite+aiosqlite:///{TEST_DB_PATH}'

test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


def _run_async(coro):
    return asyncio.run(coro)


@pytest.fixture(scope='session', autouse=True)
def setup_test_database():
    async def _setup():
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    _run_async(_setup())
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

    async def _teardown():
        await test_engine.dispose()

    _run_async(_teardown())
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def clean_database():
    SettingsService.clear_cache()
    async def _clean():
        async with test_engine.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                await connection.execute(table.delete())

    _run_async(_clean())


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def create_user():
    def _create(
        username: str = 'admin',
        email: str = 'admin@example.com',
        password: str = 'StrongPass123!',
        is_active: bool = True,
    ) -> None:
        async def _persist() -> None:
            async with TestSessionLocal() as session:
                user = User(
                    username=username,
                    email=email,
                    password_hash=hash_password(password),
                    is_active=is_active,
                )
                session.add(user)
                await session.commit()

        _run_async(_persist())

    return _create


@pytest.fixture
def assign_permission_to_user():
    def _assign(*, user_email: str, permission_name: str, resource: str, action: str) -> None:
        async def _persist() -> None:
            async with TestSessionLocal() as session:
                user_result = await session.execute(select(User).where(User.email == user_email))
                user = user_result.scalar_one()

                role_name = f'role-{permission_name}'
                role_result = await session.execute(select(Role).where(Role.name == role_name))
                role = role_result.scalar_one_or_none()
                if role is None:
                    role = Role(name=role_name, description='test role')
                    session.add(role)
                    await session.flush()

                permission_result = await session.execute(select(Permission).where(Permission.name == permission_name))
                permission = permission_result.scalar_one_or_none()
                if permission is None:
                    permission = Permission(name=permission_name, resource=resource, action=action)
                    session.add(permission)
                    await session.flush()

                role_permission_result = await session.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == permission.id,
                    )
                )
                if role_permission_result.scalar_one_or_none() is None:
                    session.add(RolePermission(role_id=role.id, permission_id=permission.id))

                user_role_result = await session.execute(
                    select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
                )
                if user_role_result.scalar_one_or_none() is None:
                    session.add(UserRole(user_id=user.id, role_id=role.id))

                await session.commit()

        _run_async(_persist())

    return _assign
