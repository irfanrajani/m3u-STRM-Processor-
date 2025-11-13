"""add must_change_password field

Revision ID: 006
Revises: 005
Create Date: 2025-01-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add must_change_password field to users table (idempotent)."""
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if users table exists
    tables = inspector.get_table_names()
    if 'users' not in tables:
        return  # Skip if users table doesn't exist yet

    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'must_change_password' not in columns:
        op.add_column(
            'users',
            sa.Column('must_change_password', sa.Boolean(), nullable=True, server_default='false')
        )

        # Set default value for existing users
        op.execute("UPDATE users SET must_change_password = false WHERE must_change_password IS NULL")

        # Make column not nullable after setting defaults
        op.alter_column('users', 'must_change_password', nullable=False)


def downgrade() -> None:
    """Remove must_change_password field from users table."""
    op.drop_column('users', 'must_change_password')
