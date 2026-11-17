from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import get_current_auth_session, require_csrf_protection

from .dependencies import get_rbac_service, require_permission
from .schemas import (
    AssignmentResponse,
    PermissionCreateRequest,
    PermissionListResponse,
    PermissionResponse,
    PermissionUpdateRequest,
    RoleCreateRequest,
    RoleListResponse,
    RolePermissionsResponse,
    RoleResponse,
    RoleUpdateRequest,
    UserPermissionsResponse,
    UserRolesResponse,
)
from .service import RBACService

router = APIRouter(prefix='/api/rbac', tags=['rbac'])

MANAGE_RBAC_PERMISSION = 'rbac.manage'


@router.get('/roles/query', response_model=RoleListResponse, status_code=status.HTTP_200_OK)
async def list_roles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> RoleListResponse:
    items, total = await rbac_service.list_roles_paginated(page=page, page_size=page_size, search=search)
    return RoleListResponse(
        items=[RoleResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    '/roles',
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def create_role(
    payload: RoleCreateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> RoleResponse:
    role = await rbac_service.create_role(
        actor_user_id=auth_session.user_id,
        name=payload.name,
        description=payload.description,
    )
    return RoleResponse.model_validate(role)


@router.put(
    '/roles/{role_id}',
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def update_role(
    role_id: int,
    payload: RoleUpdateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> RoleResponse:
    role = await rbac_service.update_role(
        actor_user_id=auth_session.user_id,
        role_id=role_id,
        name=payload.name,
        description=payload.description,
    )
    return RoleResponse.model_validate(role)


@router.delete(
    '/roles/{role_id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_role(
    role_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> AssignmentResponse:
    await rbac_service.delete_role(actor_user_id=auth_session.user_id, role_id=role_id)
    return AssignmentResponse(message='Role deleted.')


@router.get('/permissions/query', response_model=PermissionListResponse, status_code=status.HTTP_200_OK)
async def list_permissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> PermissionListResponse:
    items, total = await rbac_service.list_permissions_paginated(page=page, page_size=page_size, search=search)
    return PermissionListResponse(
        items=[PermissionResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    '/permissions',
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def create_permission(
    payload: PermissionCreateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> PermissionResponse:
    permission = await rbac_service.create_permission(
        actor_user_id=auth_session.user_id,
        name=payload.name,
        resource=payload.resource,
        action=payload.action,
    )
    return PermissionResponse.model_validate(permission)


@router.put(
    '/permissions/{permission_id}',
    response_model=PermissionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def update_permission(
    permission_id: int,
    payload: PermissionUpdateRequest,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> PermissionResponse:
    permission = await rbac_service.update_permission(
        actor_user_id=auth_session.user_id,
        permission_id=permission_id,
        name=payload.name,
        resource=payload.resource,
        action=payload.action,
    )
    return PermissionResponse.model_validate(permission)


@router.delete(
    '/permissions/{permission_id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_permission(
    permission_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> AssignmentResponse:
    await rbac_service.delete_permission(actor_user_id=auth_session.user_id, permission_id=permission_id)
    return AssignmentResponse(message='Permission deleted.')


@router.post(
    '/roles/{role_id}/permissions/{permission_id}',
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> AssignmentResponse:
    await rbac_service.assign_permission_to_role(
        actor_user_id=auth_session.user_id,
        role_id=role_id,
        permission_id=permission_id,
    )
    return AssignmentResponse(message='Permission assigned to role.')


@router.post(
    '/users/{user_id}/roles/{role_id}',
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    auth_session: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> AssignmentResponse:
    await rbac_service.assign_role_to_user(
        actor_user_id=auth_session.user_id,
        user_id=user_id,
        role_id=role_id,
    )
    return AssignmentResponse(message='Role assigned to user.')


@router.get('/me/permissions', response_model=UserPermissionsResponse, status_code=status.HTTP_200_OK)
async def get_my_permissions(
    auth_session: AuthSession = Depends(get_current_auth_session),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> UserPermissionsResponse:
    permissions = await rbac_service.list_user_permissions(user_id=auth_session.user_id)
    return UserPermissionsResponse(user_id=auth_session.user_id, permissions=permissions)


@router.get('/me/roles', response_model=UserRolesResponse, status_code=status.HTTP_200_OK)
async def get_my_roles(
    auth_session: AuthSession = Depends(get_current_auth_session),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> UserRolesResponse:
    roles = await rbac_service.list_user_roles(user_id=auth_session.user_id)
    return UserRolesResponse(user_id=auth_session.user_id, roles=roles)


@router.get(
    '/users/{user_id}/permissions',
    response_model=UserPermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_permissions(
    user_id: int,
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> UserPermissionsResponse:
    permissions = await rbac_service.list_user_permissions(user_id=user_id)
    return UserPermissionsResponse(user_id=user_id, permissions=permissions)


@router.get(
    '/users/{user_id}/roles',
    response_model=UserRolesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_roles(
    user_id: int,
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> UserRolesResponse:
    roles = await rbac_service.list_user_roles(user_id=user_id)
    return UserRolesResponse(user_id=user_id, roles=roles)


@router.get(
    '/roles/{role_id}/permissions',
    response_model=RolePermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_role_permissions(
    role_id: int,
    _: AuthSession = Depends(require_permission(MANAGE_RBAC_PERMISSION)),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> RolePermissionsResponse:
    permissions = await rbac_service.list_role_permissions(role_id=role_id)
    return RolePermissionsResponse(role_id=role_id, permissions=permissions)
