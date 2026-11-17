from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.auth_session import AuthSession

from .service import AuthService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_current_auth_session(
    session_token: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthSession:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')

    return await auth_service.get_current_session(session_token=session_token)


async def require_csrf_protection(
    request: Request,
    auth_session: AuthSession = Depends(get_current_auth_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthSession:
    csrf_header_token = request.headers.get(settings.CSRF_HEADER_NAME)
    csrf_cookie_token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    await auth_service.validate_csrf(
        auth_session=auth_session,
        csrf_token=csrf_header_token,
        csrf_cookie=csrf_cookie_token,
    )
    return auth_session
