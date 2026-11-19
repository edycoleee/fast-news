from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = 'comments'
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name='ck_comments_status',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    news_id: Mapped[int] = mapped_column(ForeignKey('news.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)
    author_name: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending', index=True)
    moderation_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    moderated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    moderated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    news: Mapped['News'] = relationship(back_populates='comments')
    user: Mapped['User | None'] = relationship(
        foreign_keys=[user_id],
        back_populates='comments',
    )
    moderated_by: Mapped['User | None'] = relationship(foreign_keys=[moderated_by_id])
    parent: Mapped['Comment | None'] = relationship(remote_side='Comment.id', back_populates='children')
    children: Mapped[list['Comment']] = relationship(back_populates='parent')
