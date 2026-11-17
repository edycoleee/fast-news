from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.models.auth_session import AuthSession
from app.modules.auth.dependencies import require_csrf_protection
from app.modules.rbac.dependencies import require_any_permission

from .dependencies import get_file_service
from .schemas import FileAssetResponse, FileDeleteResponse, FileListResponse
from .service import FileService

router = APIRouter(prefix='/api/files', tags=['files'])

MANAGE_FILE_PERMISSION = 'file.manage'
MANAGE_NEWS_PERMISSION = 'news.manage'


@router.get('/query', response_model=FileListResponse, status_code=status.HTTP_200_OK)
async def list_files(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    _: AuthSession = Depends(require_any_permission([MANAGE_FILE_PERMISSION, MANAGE_NEWS_PERMISSION])),
    file_service: FileService = Depends(get_file_service),
) -> FileListResponse:
    items, total = await file_service.list_files_paginated(page=page, page_size=page_size, search=search)
    return FileListResponse(
        items=[FileAssetResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    '/upload',
    response_model=FileAssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf_protection)],
)
async def upload_file(
    upload_file: UploadFile = File(...),
    auth_session: AuthSession = Depends(require_any_permission([MANAGE_FILE_PERMISSION, MANAGE_NEWS_PERMISSION])),
    file_service: FileService = Depends(get_file_service),
) -> FileAssetResponse:
    file_asset = await file_service.upload_file(actor_user_id=auth_session.user_id, upload_file=upload_file)
    return FileAssetResponse.model_validate(file_asset)


@router.get('/{file_id}/download', status_code=status.HTTP_200_OK)
async def download_file(
    file_id: int,
    _: AuthSession = Depends(require_any_permission([MANAGE_FILE_PERMISSION, MANAGE_NEWS_PERMISSION])),
    file_service: FileService = Depends(get_file_service),
) -> FileResponse:
    file_asset = await file_service.get_file_asset(file_id)
    storage_path = file_service.get_storage_path(file_asset)
    return FileResponse(path=storage_path, media_type=file_asset.mime_type, filename=file_asset.original_name)


@router.delete(
    '/{file_id}',
    response_model=FileDeleteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_csrf_protection)],
)
async def delete_file(
    file_id: int,
    auth_session: AuthSession = Depends(require_any_permission([MANAGE_FILE_PERMISSION, MANAGE_NEWS_PERMISSION])),
    file_service: FileService = Depends(get_file_service),
) -> FileDeleteResponse:
    await file_service.delete_file(actor_user_id=auth_session.user_id, file_id=file_id)
    return FileDeleteResponse(message='File deleted.')
