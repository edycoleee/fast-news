from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Signature(Base):
    __tablename__ = 'signatures'
    __table_args__ = (
        CheckConstraint("status IN ('active', 'revoked')", name='ck_signatures_status'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    signer_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    news_id: Mapped[int | None] = mapped_column(
        ForeignKey('news.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    file_asset_id: Mapped[int] = mapped_column(
        ForeignKey('file_assets.id', ondelete='RESTRICT'),
        nullable=False,
        unique=True,
        index=True,
    )
    purpose: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='active', index=True)
    revocation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    revoked_by_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    signer: Mapped['User | None'] = relationship(foreign_keys=[signer_id], back_populates='signatures')
    revoked_by: Mapped['User | None'] = relationship(foreign_keys=[revoked_by_id])
    news: Mapped['News | None'] = relationship(back_populates='signatures')
    file_asset: Mapped['FileAsset'] = relationship(back_populates='signature')
