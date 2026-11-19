from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .service import CommentService


def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(db)
