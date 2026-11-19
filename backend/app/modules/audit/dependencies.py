from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .service import AuditService


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)
