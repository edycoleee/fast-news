from fastapi import APIRouter, Depends, status

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import require_csrf_protection
from app.modules.operations.retention import RetentionService
from app.modules.rbac.dependencies import require_any_permission

from .dependencies import get_settings_service
from .permissions import MANAGE_SETTINGS_PERMISSION, READ_SETTINGS_PERMISSION, UPDATE_SETTINGS_PERMISSION
from .schemas import (
    RetentionCleanupRequest,
    RetentionCleanupResponse,
    RuntimeSettingsPublicResponse,
    RuntimeSettingsResponse,
    RuntimeSettingsUpdateRequest,
)
from .service import SettingsService

router = APIRouter(prefix='/api/settings', tags=['settings'])

READ_PERMISSIONS = [READ_SETTINGS_PERMISSION, MANAGE_SETTINGS_PERMISSION, 'rbac.manage']
UPDATE_PERMISSIONS = [UPDATE_SETTINGS_PERMISSION, MANAGE_SETTINGS_PERMISSION, 'rbac.manage']


@router.get('', response_model=RuntimeSettingsResponse, status_code=status.HTTP_200_OK)
async def list_settings(
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    settings_service: SettingsService = Depends(get_settings_service),
) -> RuntimeSettingsResponse:
    return RuntimeSettingsResponse(items=await settings_service.list_settings())


@router.put(
    '',
    response_model=RuntimeSettingsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def update_settings(
    payload: RuntimeSettingsUpdateRequest,
    auth_session: AuthSession = Depends(require_any_permission(UPDATE_PERMISSIONS)),
    settings_service: SettingsService = Depends(get_settings_service),
) -> RuntimeSettingsResponse:
    items = await settings_service.update_settings(
        actor_user_id=auth_session.user_id,
        updates=[item.model_dump() for item in payload.settings],
    )
    return RuntimeSettingsResponse(items=items)


@router.get('/public', response_model=RuntimeSettingsPublicResponse, status_code=status.HTTP_200_OK)
async def get_public_limits(
    settings_service: SettingsService = Depends(get_settings_service),
) -> RuntimeSettingsPublicResponse:
    return RuntimeSettingsPublicResponse(
        comment_max_length=int(await settings_service.get_value('comment.max_length')),
        upload_max_size_bytes=int(await settings_service.get_value('upload.max_size_bytes')),
        signature_max_size_bytes=int(await settings_service.get_value('signature.max_size_bytes')),
    )


@router.post(
    '/retention/cleanup',
    response_model=RetentionCleanupResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def run_retention_cleanup(
    payload: RetentionCleanupRequest,
    auth_session: AuthSession = Depends(require_any_permission(UPDATE_PERMISSIONS)),
    settings_service: SettingsService = Depends(get_settings_service),
) -> RetentionCleanupResponse:
    report = await RetentionService(settings_service.db).cleanup(
        dry_run=payload.dry_run,
        batch_size=payload.batch_size,
        actor_user_id=auth_session.user_id,
    )
    return RetentionCleanupResponse(**report)
