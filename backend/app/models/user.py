from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    roles: Mapped[list['UserRole']] = relationship(back_populates='user', cascade='all, delete-orphan')
    audit_logs: Mapped[list['AuditLog']] = relationship(back_populates='user')
    auth_sessions: Mapped[list['AuthSession']] = relationship(back_populates='user', cascade='all, delete-orphan')
    news: Mapped[list['News']] = relationship(back_populates='author')
    file_assets: Mapped[list['FileAsset']] = relationship(back_populates='uploaded_by_user')
    comments: Mapped[list['Comment']] = relationship(back_populates='user')
