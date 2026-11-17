from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    news_id: Mapped[int] = mapped_column(ForeignKey('news.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending', index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    news: Mapped['News'] = relationship(back_populates='comments')
    user: Mapped['User'] = relationship(back_populates='comments')
    parent: Mapped['Comment | None'] = relationship(remote_side='Comment.id', back_populates='children')
    children: Mapped[list['Comment']] = relationship(back_populates='parent')
