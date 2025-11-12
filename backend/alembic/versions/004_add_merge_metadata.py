"""Add merge metadata tracking

Revision ID: 004_add_merge_metadata
Revises: 003_add_value_type_to_app_settings
Create Date: 2025-11-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_merge_metadata'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add merge metadata columns to channel_streams
    op.add_column('channel_streams', sa.Column('merge_confidence', sa.Float(), nullable=True))
    op.add_column('channel_streams', sa.Column('merge_method', sa.String(50), nullable=True))
    op.add_column('channel_streams', sa.Column('merge_reason', sa.Text(), nullable=True))
    op.add_column('channel_streams', sa.Column('manual_override', sa.Boolean(), server_default='false'))
    
    # Create merge_rules table
    op.create_table(
        'merge_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),  # 'never_merge', 'always_merge', 'custom'
        sa.Column('pattern1', sa.String(500), nullable=False),
        sa.Column('pattern2', sa.String(500), nullable=True),
        sa.Column('region1', sa.String(100), nullable=True),
        sa.Column('region2', sa.String(100), nullable=True),
        sa.Column('provider_id', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('enabled', sa.Boolean(), server_default='true'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    op.create_index('idx_merge_rules_pattern1', 'merge_rules', ['pattern1'])
    op.create_index('idx_merge_rules_enabled', 'merge_rules', ['enabled'])


def downgrade() -> None:
    op.drop_index('idx_merge_rules_enabled')
    op.drop_index('idx_merge_rules_pattern1')
    op.drop_table('merge_rules')
    
    op.drop_column('channel_streams', 'manual_override')
    op.drop_column('channel_streams', 'merge_reason')
    op.drop_column('channel_streams', 'merge_method')
    op.drop_column('channel_streams', 'merge_confidence')
