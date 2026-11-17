from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)

    user: Mapped['User'] = relationship(back_populates='roles')
    role: Mapped['Role'] = relationship(back_populates='users')


class RolePermission(Base):
    __tablename__ = 'role_permissions'
    __table_args__ = (UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True)

    role: Mapped['Role'] = relationship(back_populates='permissions')
    permission: Mapped['Permission'] = relationship(back_populates='roles')
