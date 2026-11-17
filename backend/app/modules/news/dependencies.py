from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .service import NewsService


def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(db)
