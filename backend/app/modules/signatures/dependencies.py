from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .service import SignatureService


def get_signature_service(db: AsyncSession = Depends(get_db)) -> SignatureService:
    return SignatureService(db)
