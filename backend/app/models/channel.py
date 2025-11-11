"""Channel database models."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Channel(Base):
    """Merged channel model - represents a logical channel with multiple streams."""

    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    normalized_name = Column(String(500), nullable=False, index=True)  # For matching
    category = Column(String(255), nullable=True, index=True)
    country = Column(String(100), nullable=True)
    language = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)  # e.g., "West", "East", "Ontario"
    variant = Column(String(100), nullable=True)  # e.g., "+", "HD", "4K"

    # Logo
    logo_url = Column(String(1000), nullable=True)
    logo_hash = Column(String(64), nullable=True)  # For image-based matching

    # EPG
    epg_id = Column(String(255), nullable=True, index=True)
    tvg_id = Column(String(255), nullable=True)

    # Status
    enabled = Column(Boolean, default=True)
    stream_count = Column(Integer, default=0)  # Number of active streams
    last_watched = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    tags = Column(JSON, nullable=True)  # Additional metadata
    custom_order = Column(Integer, nullable=True)  # User-defined ordering

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    streams = relationship("ChannelStream", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Channel(id={self.id}, name='{self.name}', streams={self.stream_count})>"


class ChannelStream(Base):
    """Individual stream from a provider - multiple streams can belong to one channel."""

    __tablename__ = "channel_streams"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stream info
    stream_url = Column(Text, nullable=False)
    stream_id = Column(String(255), nullable=True)  # Provider's stream ID
    stream_format = Column(String(50), nullable=True)  # ts, m3u8, etc.

    # Quality info
    resolution = Column(String(20), nullable=True)  # 1080p, 720p, 4K, etc.
    bitrate = Column(Integer, nullable=True)  # in kbps
    codec = Column(String(50), nullable=True)
    fps = Column(Float, nullable=True)
    quality_score = Column(Integer, default=0)  # Calculated score for prioritization

    # Health status
    is_active = Column(Boolean, default=True)
    last_check = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(Integer, default=0)
    response_time = Column(Float, nullable=True)  # in milliseconds
    last_success = Column(DateTime(timezone=True), nullable=True)
    last_failure = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Prioritization
    priority_order = Column(Integer, default=0)  # 0 = highest quality, 1 = second best, etc.

    # Original metadata from provider
    original_name = Column(String(500), nullable=True)
    original_category = Column(String(255), nullable=True)
    provider_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    channel = relationship("Channel", back_populates="streams")
    provider = relationship("Provider", back_populates="streams")

    def __repr__(self):
        return (
            f"<ChannelStream(id={self.id}, channel_id={self.channel_id}, "
            f"resolution='{self.resolution}', active={self.is_active})>"
        )
