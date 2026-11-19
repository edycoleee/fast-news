from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FileAsset(Base):
    __tablename__ = 'file_assets'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    uploaded_by_user: Mapped['User | None'] = relationship(back_populates='file_assets')
    signature: Mapped['Signature | None'] = relationship(back_populates='file_asset')
