from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import require_csrf_protection
from app.modules.rbac.dependencies import require_permission

from .dependencies import get_user_service
from .schemas import UserCreateRequest, UserListResponse, UserResponse, UserUpdateRequest
from .service import UserService

router = APIRouter(prefix='/api/users', tags=['users'])

MANAGE_RBAC_PERMISSION = 'rbac.manage'


@router.get('/query', response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    items, total = await user_service.list_users_paginated(page=page, page_size=page_size, search=search)
    return UserListResponse(
        items=[UserResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.get_user(user_id)
    return UserResponse.model_validate(user)


@router.post(
    '',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def create_user(
    payload: UserCreateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.create_user(
        actor_user_id=auth_session.user_id,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        is_active=payload.is_active,
    )
    return UserResponse.model_validate(user)


@router.put(
    '/{user_id}',
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.update_user(
        actor_user_id=auth_session.user_id,
        user_id=user_id,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        is_active=payload.is_active,
    )
    return UserResponse.model_validate(user)


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_user(
    user_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    user_service: UserService = Depends(get_user_service),
) -> dict[str, str]:
    await user_service.delete_user(actor_user_id=auth_session.user_id, user_id=user_id)
    return {'message': 'User deleted.'}
