from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from app.core.config import settings
from app.models.auth_session import AuthSession

from .dependencies import get_auth_service, get_current_auth_session, require_csrf_protection
from .schemas import LoginRequest, LoginResponse, LogoutResponse, MeResponse
from .service import AuthService

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/login', response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    login_result = await auth_service.login(
        username_or_email=payload.username_or_email,
        password=payload.password,
        request=request,
    )

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
