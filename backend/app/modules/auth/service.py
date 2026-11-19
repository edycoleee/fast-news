from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.models.user import User

from .repository import AuthRepository
from app.modules.rbac.repository import RBACRepository
from .security import (
    build_session_expiry,
    generate_csrf_token,
    generate_session_token,
    hash_token,
    is_token_match,
    verify_password,
)


@dataclass
class LoginResult:
    user: User
    session_token: str
    csrf_token: str


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = AuthRepository(db)
        self.rbac_repository = RBACRepository(db)

    async def list_permissions_for_user(self, user_id: int) -> list[str]:
        return await self.rbac_repository.list_user_permission_names(user_id)

    async def login(self, username_or_email: str, password: str, request: Request) -> LoginResult:
        user = await self.repository.get_user_by_login_identifier(username_or_email)
        if user is None or not user.is_active:
            await self.repository.add_login_audit_log(
                user_id=None,
                action='auth.login.failure',
                details={
                    'identifier_hash': hash_token(username_or_email.strip().lower()),
                    'ip_address': request.client.host if request.client else None,
                    'reason': 'invalid_or_inactive_user',
                },
            )
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials.')

        if not verify_password(password=password, password_hash=user.password_hash):
            await self.repository.add_login_audit_log(
                user_id=user.id,
                action='auth.login.failure',
                details={
                    'identifier_hash': hash_token(username_or_email.strip().lower()),
                    'ip_address': request.client.host if request.client else None,
                    'reason': 'invalid_password',
                },
            )
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials.')

        session_token = generate_session_token()
        csrf_token = generate_csrf_token()
        await self.repository.create_auth_session(
            user_id=user.id,
            session_token_hash=hash_token(session_token),
            csrf_token_hash=hash_token(csrf_token),
            expires_at=build_session_expiry(),
            user_agent=request.headers.get('user-agent'),
            ip_address=request.client.host if request.client else None,
        )
        await self.repository.add_login_audit_log(
            user_id=user.id,
            action='auth.login.success',
            details={
                'ip_address': request.client.host if request.client else None,
                'user_agent': request.headers.get('user-agent'),
            },
        )
        await self.db.commit()

        return LoginResult(user=user, session_token=session_token, csrf_token=csrf_token)

    async def get_current_session(self, session_token: str) -> AuthSession:
        auth_session = await self.repository.get_valid_session_with_user(hash_token(session_token))
        if auth_session is None or auth_session.user is None or not auth_session.user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')

        await self.repository.update_last_seen(auth_session)
        await self.db.commit()
        return auth_session

    async def validate_csrf(self, auth_session: AuthSession, csrf_token: str | None, csrf_cookie: str | None) -> None:
        if not csrf_token or not csrf_cookie:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF token missing.')

        if csrf_token != csrf_cookie:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF token mismatch.')

        if not is_token_match(raw_token=csrf_token, token_hash=auth_session.csrf_token_hash):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid CSRF token.')

    async def logout(self, auth_session: AuthSession) -> None:
        await self.repository.revoke_session(auth_session)
        await self.repository.add_audit_log(
            actor_user_id=auth_session.user_id,
            action='auth.logout',
            target_session_id=auth_session.id,
            details={'reason': 'user_logout'},
        )
        await self.db.commit()

    async def list_sessions(
        self,
        *,
        current_session: AuthSession,
        user_id: int | None = None,
    ) -> tuple[list[AuthSession], int]:
        target_user_id = user_id if user_id is not None else current_session.user_id
        return (
            await self.repository.list_active_sessions(user_id=target_user_id),
            current_session.id,
        )

    async def list_all_sessions(self, current_session: AuthSession) -> tuple[list[AuthSession], int]:
        return await self.repository.list_active_sessions(), current_session.id

    async def revoke_session_by_id(
        self,
        *,
        current_session: AuthSession,
        session_id: int,
        allow_other_users: bool,
    ) -> None:
        target = await self.repository.get_session_by_id(session_id)
        if target is None or target.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found.')
        if target.user_id != current_session.user_id and not allow_other_users:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden.')

        await self.repository.revoke_session(target)
        await self.repository.add_audit_log(
            actor_user_id=current_session.user_id,
            action='auth.session.revoke',
            target_session_id=target.id,
            details={
                'target_user_id': target.user_id,
                'revoked_current_session': target.id == current_session.id,
            },
        )
        await self.db.commit()

    async def revoke_other_sessions(self, current_session: AuthSession) -> int:
        count = await self.repository.revoke_sessions_for_user(
            user_id=current_session.user_id,
            except_session_id=current_session.id,
        )
        await self.repository.add_audit_log(
            actor_user_id=current_session.user_id,
            action='auth.sessions.revoke_others',
            target_session_id=None,
            details={'revoked_count': count, 'except_session_id': current_session.id},
        )
        await self.db.commit()
        return count
