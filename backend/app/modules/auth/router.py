from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import settings
from app.models.auth_session import AuthSession
from app.modules.security.dependencies import get_rate_limit_service
from app.modules.security.rate_limit import RateLimitService
from app.modules.rbac.dependencies import require_permission

from .dependencies import get_auth_service, get_current_auth_session, require_csrf_protection
from .permissions import MANAGE_SESSIONS_PERMISSION
from .schemas import (
    AuthSessionListResponse,
    AuthSessionResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MeResponse,
    SessionRevokeResponse,
)
from .service import AuthService

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/login', response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
) -> LoginResponse:
    await rate_limit_service.check_login(
        request=request,
        identifier=payload.username_or_email,
    )
    try:
        login_result = await auth_service.login(
            username_or_email=payload.username_or_email,
            password=payload.password,
            request=request,
        )
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            await rate_limit_service.record_login_failure(payload.username_or_email)
        raise
    await rate_limit_service.clear_login_failures(payload.username_or_email)

    cookie_max_age = settings.SESSION_TTL_MINUTES * 60
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=login_result.session_token,
        max_age=cookie_max_age,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite='lax',
        path='/',
    )
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=login_result.csrf_token,
        max_age=cookie_max_age,
        httponly=False,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite='lax',
        path='/',
    )

    return LoginResponse(message='Login successful.', user=login_result.user)


@router.get('/me', response_model=MeResponse, status_code=status.HTTP_200_OK)
async def me(
    auth_session: AuthSession = Depends(get_current_auth_session),
) -> MeResponse:
    return MeResponse(user=auth_session.user)


@router.post('/logout', response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    auth_session: AuthSession = Depends(require_csrf_protection),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    await auth_service.logout(auth_session=auth_session)

    response.delete_cookie(key=settings.SESSION_COOKIE_NAME, path='/')
    response.delete_cookie(key=settings.CSRF_COOKIE_NAME, path='/')
    return LogoutResponse(message='Logout successful.')


def _serialize_sessions(
    sessions: list,
    current_session_id: int,
) -> list[AuthSessionResponse]:
    return [
        AuthSessionResponse(
            id=session.id,
            user_id=session.user_id,
            username=session.user.username if session.user else None,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            created_at=session.created_at,
            last_seen_at=session.last_seen_at,
            expires_at=session.expires_at,
            is_current=session.id == current_session_id,
        )
        for session in sessions
    ]


@router.get(
    '/sessions',
    response_model=AuthSessionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_my_sessions(
    auth_session: AuthSession = Depends(get_current_auth_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthSessionListResponse:
    sessions, current_session_id = await auth_service.list_sessions(
        current_session=auth_session,
    )
    return AuthSessionListResponse(
        items=_serialize_sessions(sessions, current_session_id),
    )


@router.get(
    '/sessions/all',
    response_model=AuthSessionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_all_sessions(
    auth_session: AuthSession = Depends(get_current_auth_session),
    _: AuthSession = Depends(require_permission(MANAGE_SESSIONS_PERMISSION)),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthSessionListResponse:
    sessions, current_session_id = await auth_service.list_all_sessions(auth_session)
    return AuthSessionListResponse(
        items=_serialize_sessions(sessions, current_session_id),
    )


@router.delete(
    '/sessions/{session_id}',
    response_model=SessionRevokeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def revoke_session(
    session_id: int,
    auth_session: AuthSession = Depends(get_current_auth_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionRevokeResponse:
    user_permissions = await auth_service.list_permissions_for_user(auth_session.user_id)
    await auth_service.revoke_session_by_id(
        current_session=auth_session,
        session_id=session_id,
        allow_other_users=MANAGE_SESSIONS_PERMISSION in user_permissions,
    )
    return SessionRevokeResponse(message='Session revoked.')


@router.delete(
    '/sessions',
    response_model=SessionRevokeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def revoke_other_sessions(
    auth_session: AuthSession = Depends(get_current_auth_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionRevokeResponse:
    count = await auth_service.revoke_other_sessions(auth_session)
    return SessionRevokeResponse(message=f'{count} session(s) revoked.')
