"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-11-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create providers table
    op.create_table('providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),

        # M3U provider fields
        sa.Column('m3u_url', sa.String(length=1000), nullable=True),
        sa.Column('backup_m3u_urls', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Xstream provider fields
        sa.Column('host', sa.String(length=500), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('backup_hosts', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # EPG
        sa.Column('epg_url', sa.String(length=1000), nullable=True),

        # Stats
        sa.Column('total_channels', sa.Integer(), nullable=True),
        sa.Column('active_channels', sa.Integer(), nullable=True),
        sa.Column('last_sync', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_health_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('status_message', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_providers_name'), 'providers', ['name'], unique=False)
    op.create_index(op.f('ix_providers_type'), 'providers', ['type'], unique=False)

    # Create channels table
    op.create_table('channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('normalized_name', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('language', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('variant', sa.String(length=100), nullable=True),

        # Logo
        sa.Column('logo_url', sa.String(length=1000), nullable=True),
        sa.Column('logo_hash', sa.String(length=64), nullable=True),

        # EPG
        sa.Column('epg_id', sa.String(length=255), nullable=True),
        sa.Column('tvg_id', sa.String(length=255), nullable=True),

        # Status
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('stream_count', sa.Integer(), nullable=True),
        sa.Column('last_watched', sa.DateTime(timezone=True), nullable=True),

        # Metadata
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_order', sa.Integer(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_channels_name'), 'channels', ['name'], unique=False)
    op.create_index(op.f('ix_channels_normalized_name'), 'channels', ['normalized_name'], unique=False)
    op.create_index(op.f('ix_channels_category'), 'channels', ['category'], unique=False)
    op.create_index(op.f('ix_channels_epg_id'), 'channels', ['epg_id'], unique=False)

    # Create channel_streams table
    op.create_table('channel_streams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),

        # Stream info
        sa.Column('stream_url', sa.Text(), nullable=False),
        sa.Column('stream_id', sa.String(length=255), nullable=True),
        sa.Column('stream_format', sa.String(length=50), nullable=True),

        # Quality info
        sa.Column('resolution', sa.String(length=20), nullable=True),
        sa.Column('bitrate', sa.Integer(), nullable=True),
        sa.Column('codec', sa.String(length=50), nullable=True),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Integer(), nullable=True),

        # Health status
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('last_success', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),

        # Prioritization
        sa.Column('priority_order', sa.Integer(), nullable=True),

        # Original metadata from provider
        sa.Column('original_name', sa.String(length=500), nullable=True),
        sa.Column('original_category', sa.String(length=255), nullable=True),
        sa.Column('provider_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_channel_streams_channel_id'), 'channel_streams', ['channel_id'], unique=False)
    op.create_index(op.f('ix_channel_streams_provider_id'), 'channel_streams', ['provider_id'], unique=False)

    # Create vod_movies table
    op.create_table('vod_movies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),

        # Movie info
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('normalized_title', sa.String(length=500), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('tmdb_id', sa.String(length=50), nullable=True),
        sa.Column('imdb_id', sa.String(length=50), nullable=True),

        # Classification
        sa.Column('genre', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),

        # Media info
        sa.Column('stream_url', sa.Text(), nullable=False),
        sa.Column('stream_id', sa.String(length=255), nullable=True),
        sa.Column('cover_url', sa.String(length=1000), nullable=True),
        sa.Column('backdrop_url', sa.String(length=1000), nullable=True),
        sa.Column('quality', sa.String(length=50), nullable=True),

        # Description
        sa.Column('plot', sa.Text(), nullable=True),
        sa.Column('director', sa.String(length=255), nullable=True),
        sa.Column('cast', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('strm_file_path', sa.String(length=1000), nullable=True),
        sa.Column('last_check', sa.DateTime(timezone=True), nullable=True),

        # Metadata
        sa.Column('provider_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vod_movies_title'), 'vod_movies', ['title'], unique=False)
    op.create_index(op.f('ix_vod_movies_normalized_title'), 'vod_movies', ['normalized_title'], unique=False)
    op.create_index(op.f('ix_vod_movies_year'), 'vod_movies', ['year'], unique=False)
    op.create_index(op.f('ix_vod_movies_genre'), 'vod_movies', ['genre'], unique=False)
    op.create_index(op.f('ix_vod_movies_tmdb_id'), 'vod_movies', ['tmdb_id'], unique=False)
    op.create_index(op.f('ix_vod_movies_imdb_id'), 'vod_movies', ['imdb_id'], unique=False)

    # Create vod_series table
    op.create_table('vod_series',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),

        # Series info
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('normalized_title', sa.String(length=500), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('tmdb_id', sa.String(length=50), nullable=True),
        sa.Column('imdb_id', sa.String(length=50), nullable=True),

        # Classification
        sa.Column('genre', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),

        # Media info
        sa.Column('series_id', sa.String(length=255), nullable=True),
        sa.Column('cover_url', sa.String(length=1000), nullable=True),
        sa.Column('backdrop_url', sa.String(length=1000), nullable=True),

        # Description
        sa.Column('plot', sa.Text(), nullable=True),
        sa.Column('cast', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('episode_count', sa.Integer(), nullable=True),
        sa.Column('season_count', sa.Integer(), nullable=True),

        # Metadata
        sa.Column('provider_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vod_series_title'), 'vod_series', ['title'], unique=False)
    op.create_index(op.f('ix_vod_series_normalized_title'), 'vod_series', ['normalized_title'], unique=False)
    op.create_index(op.f('ix_vod_series_year'), 'vod_series', ['year'], unique=False)
    op.create_index(op.f('ix_vod_series_genre'), 'vod_series', ['genre'], unique=False)
    op.create_index(op.f('ix_vod_series_tmdb_id'), 'vod_series', ['tmdb_id'], unique=False)
    op.create_index(op.f('ix_vod_series_imdb_id'), 'vod_series', ['imdb_id'], unique=False)

    # Create vod_episodes table
    op.create_table('vod_episodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('series_id', sa.Integer(), nullable=False),

        # Episode info
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('season_number', sa.Integer(), nullable=False),
        sa.Column('episode_number', sa.Integer(), nullable=False),
        sa.Column('episode_id', sa.String(length=255), nullable=True),

        # Media info
        sa.Column('stream_url', sa.Text(), nullable=False),
        sa.Column('cover_url', sa.String(length=1000), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('quality', sa.String(length=50), nullable=True),

        # Description
        sa.Column('plot', sa.Text(), nullable=True),
        sa.Column('air_date', sa.DateTime(timezone=True), nullable=True),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('strm_file_path', sa.String(length=1000), nullable=True),
        sa.Column('last_check', sa.DateTime(timezone=True), nullable=True),

        # Metadata
        sa.Column('provider_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['series_id'], ['vod_series.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vod_episodes_series_id'), 'vod_episodes', ['series_id'], unique=False)
    op.create_index(op.f('ix_vod_episodes_season_number'), 'vod_episodes', ['season_number'], unique=False)
    op.create_index(op.f('ix_vod_episodes_episode_number'), 'vod_episodes', ['episode_number'], unique=False)

    # Create epg_programs table
    op.create_table('epg_programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_epg_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('icon', sa.String(length=1000), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_epg_programs_channel_epg_id'), 'epg_programs', ['channel_epg_id'], unique=False)
    op.create_index(op.f('ix_epg_programs_start_time'), 'epg_programs', ['start_time'], unique=False)

    # Create app_settings table
    op.create_table('app_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_app_settings_key'), 'app_settings', ['key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_app_settings_key'), table_name='app_settings')
    op.drop_table('app_settings')

    op.drop_index(op.f('ix_epg_programs_start_time'), table_name='epg_programs')
    op.drop_index(op.f('ix_epg_programs_channel_epg_id'), table_name='epg_programs')
    op.drop_table('epg_programs')

    op.drop_index(op.f('ix_vod_episodes_episode_number'), table_name='vod_episodes')
    op.drop_index(op.f('ix_vod_episodes_season_number'), table_name='vod_episodes')
    op.drop_index(op.f('ix_vod_episodes_series_id'), table_name='vod_episodes')
    op.drop_table('vod_episodes')

    op.drop_index(op.f('ix_vod_series_imdb_id'), table_name='vod_series')
    op.drop_index(op.f('ix_vod_series_tmdb_id'), table_name='vod_series')
    op.drop_index(op.f('ix_vod_series_genre'), table_name='vod_series')
    op.drop_index(op.f('ix_vod_series_year'), table_name='vod_series')
    op.drop_index(op.f('ix_vod_series_normalized_title'), table_name='vod_series')
    op.drop_index(op.f('ix_vod_series_title'), table_name='vod_series')
    op.drop_table('vod_series')

    op.drop_index(op.f('ix_vod_movies_imdb_id'), table_name='vod_movies')
    op.drop_index(op.f('ix_vod_movies_tmdb_id'), table_name='vod_movies')
    op.drop_index(op.f('ix_vod_movies_genre'), table_name='vod_movies')
    op.drop_index(op.f('ix_vod_movies_year'), table_name='vod_movies')
    op.drop_index(op.f('ix_vod_movies_normalized_title'), table_name='vod_movies')
    op.drop_index(op.f('ix_vod_movies_title'), table_name='vod_movies')
    op.drop_table('vod_movies')

    op.drop_index(op.f('ix_channel_streams_provider_id'), table_name='channel_streams')
    op.drop_index(op.f('ix_channel_streams_channel_id'), table_name='channel_streams')
    op.drop_table('channel_streams')

    op.drop_index(op.f('ix_channels_epg_id'), table_name='channels')
    op.drop_index(op.f('ix_channels_category'), table_name='channels')
    op.drop_index(op.f('ix_channels_normalized_name'), table_name='channels')
    op.drop_index(op.f('ix_channels_name'), table_name='channels')
    op.drop_table('channels')

    op.drop_index(op.f('ix_providers_type'), table_name='providers')
    op.drop_index(op.f('ix_providers_name'), table_name='providers')
    op.drop_table('providers')
