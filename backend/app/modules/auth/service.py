from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.models.user import User

from .repository import AuthRepository
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

    async def login(self, username_or_email: str, password: str, request: Request) -> LoginResult:
        user = await self.repository.get_user_by_login_identifier(username_or_email)
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials.')

        if not verify_password(password=password, password_hash=user.password_hash):
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
        await self.db.commit()
