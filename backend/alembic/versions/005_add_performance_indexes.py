"""Add performance indexes

Revision ID: 005_add_performance_indexes
Revises: 004_add_merge_metadata
Create Date: 2025-01-12

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '005_add_performance_indexes'
down_revision = '004_add_merge_metadata'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing performance indexes."""
    # Most indexes already created in migration 001, only add truly missing ones

    # Channel streams - additional indexes not in 001
    op.create_index('idx_channel_streams_is_active', 'channel_streams', ['is_active'])
    op.create_index('idx_channel_streams_last_check', 'channel_streams', ['last_check'])

    # Analytics indexes (viewing_history table created in 002)
    op.create_index('idx_viewing_history_channel_id', 'viewing_history', ['channel_id'])


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('idx_viewing_history_channel_id')
    op.drop_index('idx_channel_streams_last_check')
    op.drop_index('idx_channel_streams_is_active')
