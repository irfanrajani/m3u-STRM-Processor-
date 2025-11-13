"""Add value_type to app_settings

Revision ID: 003
Revises: 002
Create Date: 2025-01-10 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add value_type column to app_settings table (idempotent)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('app_settings')]

    if 'value_type' not in columns:
        op.add_column('app_settings', sa.Column('value_type', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove value_type column
    op.drop_column('app_settings', 'value_type')
