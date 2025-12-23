"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'short_urls',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('short_id', sa.String(length=20), nullable=False),
        sa.Column('full_url', sa.String(length=2048), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_short_urls_short_id'), 'short_urls', ['short_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_short_urls_short_id'), table_name='short_urls')
    op.drop_table('short_urls')

