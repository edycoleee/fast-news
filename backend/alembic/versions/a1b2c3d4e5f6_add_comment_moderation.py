"""add comment moderation

Revision ID: a1b2c3d4e5f6
Revises: 6d1c4a2f8b30
Create Date: 2026-11-18 02:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6d1c4a2f8b30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('comments') as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=True)
        batch_op.drop_constraint('comments_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'comments_user_id_fkey',
            'users',
            ['user_id'],
            ['id'],
            ondelete='SET NULL',
        )
        batch_op.add_column(
            sa.Column(
                'author_name',
                sa.String(length=80),
                server_default='Anonymous',
                nullable=False,
            )
        )
        batch_op.add_column(sa.Column('moderation_note', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('moderated_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('moderated_at', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key(
            'comments_moderated_by_id_fkey',
            'users',
            ['moderated_by_id'],
            ['id'],
            ondelete='SET NULL',
        )
        batch_op.create_index(
            op.f('ix_comments_moderated_by_id'),
            ['moderated_by_id'],
            unique=False,
        )
        batch_op.create_check_constraint(
            'ck_comments_status',
            "status IN ('pending', 'approved', 'rejected')",
        )


def downgrade() -> None:
    with op.batch_alter_table('comments') as batch_op:
        batch_op.drop_constraint('ck_comments_status', type_='check')
        batch_op.drop_index(op.f('ix_comments_moderated_by_id'))
        batch_op.drop_constraint(
            'comments_moderated_by_id_fkey',
            type_='foreignkey',
        )
        batch_op.drop_column('moderated_at')
        batch_op.drop_column('moderated_by_id')
        batch_op.drop_column('moderation_note')
        batch_op.drop_column('author_name')
        batch_op.drop_constraint('comments_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'comments_user_id_fkey',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE',
        )
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
