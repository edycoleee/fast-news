from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import require_csrf_protection
from app.modules.rbac.dependencies import require_any_permission
from app.modules.security.dependencies import get_rate_limit_service
from app.modules.security.rate_limit import RateLimitService

from .dependencies import get_signature_service
from .permissions import (
    CREATE_SIGNATURE_PERMISSION,
    MANAGE_SIGNATURE_PERMISSION,
    READ_SIGNATURE_PERMISSION,
    REVOKE_SIGNATURE_PERMISSION,
)
from .schemas import (
    SignatureCreateRequest,
    SignatureListResponse,
    SignatureResponse,
    SignatureRevokeRequest,
)
from .service import SignatureService

router = APIRouter(prefix='/api/signatures', tags=['signatures'])

NEWS_MANAGE_PERMISSION = 'news.manage'

READ_PERMISSIONS = [
    READ_SIGNATURE_PERMISSION,
    MANAGE_SIGNATURE_PERMISSION,
    NEWS_MANAGE_PERMISSION,
]
CREATE_PERMISSIONS = [
    CREATE_SIGNATURE_PERMISSION,
    MANAGE_SIGNATURE_PERMISSION,
    NEWS_MANAGE_PERMISSION,
]
REVOKE_PERMISSIONS = [
    REVOKE_SIGNATURE_PERMISSION,
    MANAGE_SIGNATURE_PERMISSION,
    NEWS_MANAGE_PERMISSION,
]


@router.get('/query', response_model=SignatureListResponse, status_code=status.HTTP_200_OK)
async def list_signatures(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status_filter: str | None = Query(default=None),
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    signature_service: SignatureService = Depends(get_signature_service),
) -> SignatureListResponse:
    items, total = await signature_service.list_signatures(
        page=page,
        page_size=page_size,
        status_filter=status_filter,
    )
    return SignatureListResponse(
        items=[SignatureResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/{signature_id}', response_model=SignatureResponse, status_code=status.HTTP_200_OK)
async def get_signature(
    signature_id: int,
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    signature_service: SignatureService = Depends(get_signature_service),
) -> SignatureResponse:
    signature = await signature_service.get_signature(signature_id)
    return SignatureResponse.model_validate(signature)


@router.get('/{signature_id}/download', status_code=status.HTTP_200_OK)
async def download_signature(
    signature_id: int,
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    signature_service: SignatureService = Depends(get_signature_service),
) -> FileResponse:
    _, file_asset = await signature_service.get_signature_file(signature_id)
    storage_path = signature_service.get_storage_path(file_asset)
    return FileResponse(
        path=storage_path,
        media_type=file_asset.mime_type,
        filename=file_asset.original_name,
    )


@router.post(
    '',
    response_model=SignatureResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def create_signature(
    payload: SignatureCreateRequest,
    auth_session: AuthSession = Depends(require_any_permission(CREATE_PERMISSIONS)),
    signature_service: SignatureService = Depends(get_signature_service),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
) -> SignatureResponse:
    await rate_limit_service.check_upload(auth_session.user_id)
    signature = await signature_service.create_signature(
        actor_user_id=auth_session.user_id,
        purpose=payload.purpose,
        news_id=payload.news_id,
        signature_data_url=payload.signature_data_url,
    )
    return SignatureResponse.model_validate(signature)


@router.post(
    '/{signature_id}/revoke',
    response_model=SignatureResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def revoke_signature(
    signature_id: int,
    payload: SignatureRevokeRequest,
    auth_session: AuthSession = Depends(require_any_permission(REVOKE_PERMISSIONS)),
    signature_service: SignatureService = Depends(get_signature_service),
) -> SignatureResponse:
    signature = await signature_service.revoke_signature(
        actor_user_id=auth_session.user_id,
        signature_id=signature_id,
        reason=payload.reason,
    )
    return SignatureResponse.model_validate(signature)
