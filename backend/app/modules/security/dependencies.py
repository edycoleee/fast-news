from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .rate_limit import RateLimitService


def get_rate_limit_service(
    db: AsyncSession = Depends(get_db),
) -> RateLimitService:
    return RateLimitService(db)
