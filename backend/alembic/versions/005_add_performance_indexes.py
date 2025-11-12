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
    # Channel streams indexes
    op.create_index('idx_channel_streams_channel_id', 'channel_streams', ['channel_id'])
    op.create_index('idx_channel_streams_provider_id', 'channel_streams', ['provider_id'])
    op.create_index('idx_channel_streams_is_active', 'channel_streams', ['is_active'])
    op.create_index('idx_channel_streams_last_check', 'channel_streams', ['last_check'])
    
    # VOD indexes
    op.create_index('idx_vod_movies_provider_id', 'vod_movies', ['provider_id'])
    op.create_index('idx_vod_episodes_series_id', 'vod_episodes', ['series_id'])
    op.create_index('idx_vod_series_provider_id', 'vod_series', ['provider_id'])
    
    # Analytics indexes
    op.create_index('idx_viewing_history_user_id', 'viewing_history', ['user_id'])
    op.create_index('idx_viewing_history_channel_id', 'viewing_history', ['channel_id'])
    
    # EPG indexes
    op.create_index('idx_epg_programs_channel_id', 'epg_programs', ['channel_id'])
    op.create_index('idx_epg_programs_start_time', 'epg_programs', ['start_time'])
    
    # User favorites index
    op.create_index('idx_user_favorites_user_id', 'user_favorites', ['user_id'])


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('idx_user_favorites_user_id')
    op.drop_index('idx_epg_programs_start_time')
    op.drop_index('idx_epg_programs_channel_id')
    op.drop_index('idx_viewing_history_channel_id')
    op.drop_index('idx_viewing_history_user_id')
    op.drop_index('idx_vod_series_provider_id')
    op.drop_index('idx_vod_episodes_series_id')
    op.drop_index('idx_vod_movies_provider_id')
    op.drop_index('idx_channel_streams_last_check')
    op.drop_index('idx_channel_streams_is_active')
    op.drop_index('idx_channel_streams_provider_id')
    op.drop_index('idx_channel_streams_channel_id')
