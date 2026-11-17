from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .service import FileService


def get_file_service(db: AsyncSession = Depends(get_db)) -> FileService:
    return FileService(db)
