"""Add user roles and analytics

Revision ID: 002
Revises: 001
Create Date: 2025-01-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for user roles
    user_role_enum = postgresql.ENUM('admin', 'viewer', name='userrole', create_type=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'viewer', name='userrole'), nullable=False, server_default='viewer'))

    # Create user_favorites table
    op.create_table('user_favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=True),
        sa.Column('vod_movie_id', sa.Integer(), nullable=True),
        sa.Column('vod_series_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vod_movie_id'], ['vod_movies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vod_series_id'], ['vod_series.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_favorites_id'), 'user_favorites', ['id'], unique=False)
    op.create_index(op.f('ix_user_favorites_user_id'), 'user_favorites', ['user_id'], unique=False)

    # Create viewing_history table
    op.create_table('viewing_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=True),
        sa.Column('vod_movie_id', sa.Integer(), nullable=True),
        sa.Column('vod_series_id', sa.Integer(), nullable=True),
        sa.Column('stream_url', sa.String(length=2048), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vod_movie_id'], ['vod_movies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['vod_series_id'], ['vod_series.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_viewing_history_id'), 'viewing_history', ['id'], unique=False)
    op.create_index('ix_viewing_history_user_started', 'viewing_history', ['user_id', 'started_at'], unique=False)
    op.create_index('ix_viewing_history_channel', 'viewing_history', ['channel_id'], unique=False)

    # Update existing users to admin role if they are superuser
    op.execute("UPDATE users SET role = 'admin' WHERE is_superuser = TRUE")


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_viewing_history_channel', table_name='viewing_history')
    op.drop_index('ix_viewing_history_user_started', table_name='viewing_history')
    op.drop_index(op.f('ix_viewing_history_id'), table_name='viewing_history')
    op.drop_table('viewing_history')

    op.drop_index(op.f('ix_user_favorites_user_id'), table_name='user_favorites')
    op.drop_index(op.f('ix_user_favorites_id'), table_name='user_favorites')
    op.drop_table('user_favorites')

    # Drop role column
    op.drop_column('users', 'role')

    # Drop enum type
    user_role_enum = postgresql.ENUM('admin', 'viewer', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
