"""add signatures

Revision ID: 2f6b3d8a9c10
Revises: 99bd62ccbb73
Create Date: 2026-11-18 01:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2f6b3d8a9c10'
down_revision: Union[str, None] = '99bd62ccbb73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signer_id', sa.Integer(), nullable=True),
        sa.Column('news_id', sa.Integer(), nullable=True),
        sa.Column('file_asset_id', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('revocation_reason', sa.Text(), nullable=True),
        sa.Column('revoked_by_id', sa.Integer(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("status IN ('active', 'revoked')", name='ck_signatures_status'),
        sa.ForeignKeyConstraint(['file_asset_id'], ['file_assets.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['revoked_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['signer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_signatures_file_asset_id'), 'signatures', ['file_asset_id'], unique=True)
    op.create_index(op.f('ix_signatures_id'), 'signatures', ['id'], unique=False)
    op.create_index(op.f('ix_signatures_news_id'), 'signatures', ['news_id'], unique=False)
    op.create_index(op.f('ix_signatures_revoked_by_id'), 'signatures', ['revoked_by_id'], unique=False)
    op.create_index(op.f('ix_signatures_signer_id'), 'signatures', ['signer_id'], unique=False)
    op.create_index(op.f('ix_signatures_status'), 'signatures', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_signatures_status'), table_name='signatures')
    op.drop_index(op.f('ix_signatures_signer_id'), table_name='signatures')
    op.drop_index(op.f('ix_signatures_revoked_by_id'), table_name='signatures')
    op.drop_index(op.f('ix_signatures_news_id'), table_name='signatures')
    op.drop_index(op.f('ix_signatures_id'), table_name='signatures')
    op.drop_index(op.f('ix_signatures_file_asset_id'), table_name='signatures')
    op.drop_table('signatures')
