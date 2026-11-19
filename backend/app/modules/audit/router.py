from __future__ import annotations

from csv import writer
import json
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from app.models.auth_session import AuthSession
from app.modules.rbac.dependencies import require_any_permission

from .dependencies import get_audit_service
from .permissions import MANAGE_AUDIT_PERMISSION, READ_AUDIT_PERMISSION
from .schemas import AuditLogListResponse, AuditLogResponse
from .service import AuditService

router = APIRouter(prefix='/api/audit', tags=['audit'])
READ_PERMISSIONS = [READ_AUDIT_PERMISSION, MANAGE_AUDIT_PERMISSION, 'rbac.manage']


def _csv_value(value: object) -> str:
    text = str(value)
    if text.startswith(('=', '+', '-', '@')):
        return f"'{text}"
    return text


@router.get('/logs', response_model=AuditLogListResponse, status_code=status.HTTP_200_OK)
async def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
    action: str | None = Query(default=None),
    user_id: int | None = Query(default=None, gt=0),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuditLogListResponse:
    items, total = await audit_service.list_logs(
        page=page,
        page_size=page_size,
        action=action,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/logs/export', status_code=status.HTTP_200_OK)
async def export_audit_logs(
    action: str | None = Query(default=None),
    user_id: int | None = Query(default=None, gt=0),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    _: AuthSession = Depends(require_any_permission(READ_PERMISSIONS)),
    audit_service: AuditService = Depends(get_audit_service),
) -> Response:
    items, _ = await audit_service.list_logs(
        page=1,
        page_size=10000,
        action=action,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    output = StringIO()
    csv_writer = writer(output)
    csv_writer.writerow(['id', 'created_at', 'user_id', 'action', 'entity_type', 'entity_id', 'details'])
    for item in items:
        csv_writer.writerow([
            _csv_value(item.id),
            _csv_value(item.created_at.isoformat()),
            _csv_value(item.user_id or ''),
            _csv_value(item.action),
            _csv_value(item.entity_type),
            _csv_value(item.entity_id or ''),
            _csv_value(json.dumps(item.details, ensure_ascii=False) if item.details else ''),
        ])
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="newshub-audit.csv"'},
    )
