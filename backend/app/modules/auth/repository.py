from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.auth_session import AuthSession
from app.models.user import User


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_login_identifier(self, identifier: str) -> User | None:
        normalized_identifier = identifier.strip().lower()
        query = select(User).where(
            or_(User.username == normalized_identifier, User.email == normalized_identifier)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_auth_session(
        self,
        user_id: int,
        session_token_hash: str,
        csrf_token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthSession:
        auth_session = AuthSession(
            user_id=user_id,
            session_token_hash=session_token_hash,
            csrf_token_hash=csrf_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(auth_session)
        await self.db.flush()
        return auth_session

    async def get_valid_session_with_user(self, session_token_hash: str) -> AuthSession | None:
        now = datetime.utcnow()
        query = (
            select(AuthSession)
            .options(joinedload(AuthSession.user))
            .where(
                AuthSession.session_token_hash == session_token_hash,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > now,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_last_seen(self, auth_session: AuthSession) -> None:
        auth_session.last_seen_at = datetime.utcnow()
        await self.db.flush()

    async def revoke_session(self, auth_session: AuthSession) -> None:
        auth_session.revoked_at = datetime.utcnow()
        await self.db.flush()
