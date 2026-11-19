from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.auth_session import AuthSession
from app.models.audit import AuditLog
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

    async def get_session_by_id(self, session_id: int) -> AuthSession | None:
        result = await self.db.execute(
            select(AuthSession)
            .options(joinedload(AuthSession.user))
            .where(AuthSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_active_sessions(self, user_id: int | None = None) -> list[AuthSession]:
        query = (
            select(AuthSession)
            .options(joinedload(AuthSession.user))
            .where(
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > datetime.utcnow(),
            )
            .order_by(AuthSession.last_seen_at.desc())
        )
        if user_id is not None:
            query = query.where(AuthSession.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def revoke_sessions_for_user(
        self,
        *,
        user_id: int,
        except_session_id: int | None = None,
    ) -> int:
        conditions = [
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > datetime.utcnow(),
        ]
        if except_session_id is not None:
            conditions.append(AuthSession.id != except_session_id)
        result = await self.db.execute(
            update(AuthSession)
            .where(*conditions)
            .values(revoked_at=datetime.utcnow())
        )
        return result.rowcount or 0

    async def add_audit_log(
        self,
        *,
        actor_user_id: int,
        action: str,
        target_session_id: int | None,
        details: dict,
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=actor_user_id,
                action=action,
                entity_type='auth_session',
                entity_id=target_session_id,
                details=details,
            )
        )
        await self.db.flush()

    async def add_login_audit_log(
        self,
        *,
        user_id: int | None,
        action: str,
        details: dict,
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=user_id,
                action=action,
                entity_type='auth',
                entity_id=user_id,
                details=details,
            )
        )
        await self.db.flush()
