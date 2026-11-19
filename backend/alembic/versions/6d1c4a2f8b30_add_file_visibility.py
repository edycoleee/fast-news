"""add file visibility

Revision ID: 6d1c4a2f8b30
Revises: 2f6b3d8a9c10
Create Date: 2026-11-18 01:50:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6d1c4a2f8b30'
down_revision: Union[str, None] = '2f6b3d8a9c10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'file_assets',
        sa.Column('is_public', sa.Boolean(), server_default=sa.true(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('file_assets', 'is_public')
