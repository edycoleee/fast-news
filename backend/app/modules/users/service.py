from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.auth.security import hash_password

from .repository import UserRepository


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = UserRepository(db)

    async def list_users_paginated(self, *, page: int, page_size: int, search: str | None) -> tuple[list[User], int]:
        return await self.repository.list_paginated(page=page, page_size=page_size, search=search)

    async def get_user(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
        return user

    async def create_user(
        self,
        *,
        actor_user_id: int,
        username: str,
        email: str,
        password: str,
        is_active: bool,
    ) -> User:
        normalized_username = username.strip().lower()
        normalized_email = email.strip().lower()
        if '@' not in normalized_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email format.')
        if await self.repository.get_by_username(normalized_username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists.')
        if await self.repository.get_by_email(normalized_email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists.')

        user = await self.repository.create(
            username=normalized_username,
            email=normalized_email,
            password_hash=hash_password(password),
            is_active=is_active,
        )
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='user.create',
            entity_id=user.id,
            details={'username': user.username, 'email': user.email},
        )
        await self.db.commit()
        return user

    async def update_user(
        self,
        *,
        actor_user_id: int,
        user_id: int,
        username: str | None,
        email: str | None,
        password: str | None,
        is_active: bool | None,
    ) -> User:
        user = await self.get_user(user_id)

        if username is not None:
            normalized_username = username.strip().lower()
            existing_username = await self.repository.get_by_username(normalized_username)
            if existing_username and existing_username.id != user.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists.')
            user.username = normalized_username

        if email is not None:
            normalized_email = email.strip().lower()
            if '@' not in normalized_email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email format.')
            existing_email = await self.repository.get_by_email(normalized_email)
            if existing_email and existing_email.id != user.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists.')
            user.email = normalized_email

        if password is not None:
            user.password_hash = hash_password(password)

        if is_active is not None:
            user.is_active = is_active

        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='user.update',
            entity_id=user.id,
            details={'username': user.username, 'email': user.email, 'is_active': user.is_active},
        )
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, *, actor_user_id: int, user_id: int) -> None:
        user = await self.get_user(user_id)
        await self.repository.delete(user)
        await self.repository.add_audit_log(
            actor_user_id=actor_user_id,
            action='user.delete',
            entity_id=user_id,
            details={'username': user.username},
        )
        await self.db.commit()
