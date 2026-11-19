"""add security settings and rate limits

Revision ID: d91e7a2c4b6f
Revises: a1b2c3d4e5f6
Create Date: 2026-11-18 04:05:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd91e7a2c4b6f'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=120), nullable=False),
        sa.Column('category', sa.String(length=60), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('value_type', sa.String(length=20), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
    )
    op.create_index(op.f('ix_app_settings_category'), 'app_settings', ['category'], unique=False)
    op.create_index(op.f('ix_app_settings_id'), 'app_settings', ['id'], unique=False)
    op.create_index(op.f('ix_app_settings_key'), 'app_settings', ['key'], unique=True)
    op.create_index(op.f('ix_app_settings_updated_by_id'), 'app_settings', ['updated_by_id'], unique=False)

    op.create_table(
        'rate_limit_buckets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scope', sa.String(length=80), nullable=False),
        sa.Column('identifier', sa.String(length=128), nullable=False),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'scope',
            'identifier',
            'window_start',
            name='uq_rate_limit_bucket',
        ),
    )
    op.create_index(op.f('ix_rate_limit_buckets_id'), 'rate_limit_buckets', ['id'], unique=False)
    op.create_index(op.f('ix_rate_limit_buckets_identifier'), 'rate_limit_buckets', ['identifier'], unique=False)
    op.create_index(op.f('ix_rate_limit_buckets_scope'), 'rate_limit_buckets', ['scope'], unique=False)
    op.create_index(op.f('ix_rate_limit_buckets_window_start'), 'rate_limit_buckets', ['window_start'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_rate_limit_buckets_window_start'), table_name='rate_limit_buckets')
    op.drop_index(op.f('ix_rate_limit_buckets_scope'), table_name='rate_limit_buckets')
    op.drop_index(op.f('ix_rate_limit_buckets_identifier'), table_name='rate_limit_buckets')
    op.drop_index(op.f('ix_rate_limit_buckets_id'), table_name='rate_limit_buckets')
    op.drop_table('rate_limit_buckets')
    op.drop_index(op.f('ix_app_settings_updated_by_id'), table_name='app_settings')
    op.drop_index(op.f('ix_app_settings_key'), table_name='app_settings')
    op.drop_index(op.f('ix_app_settings_id'), table_name='app_settings')
    op.drop_index(op.f('ix_app_settings_category'), table_name='app_settings')
    op.drop_table('app_settings')
