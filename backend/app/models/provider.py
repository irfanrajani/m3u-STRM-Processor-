"""Provider database models."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Provider(Base):
    """IPTV Provider model."""

    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    provider_type = Column(String(50), nullable=False)  # 'xstream' or 'm3u'
    enabled = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher = more preferred

    # Xstream API fields
    xstream_host = Column(String(500), nullable=True)
    xstream_username = Column(String(255), nullable=True)
    xstream_password = Column(String(255), nullable=True)
    xstream_backup_hosts = Column(JSON, nullable=True)  # List of backup DNS

    # M3U fields
    m3u_url = Column(String(1000), nullable=True)
    m3u_backup_urls = Column(JSON, nullable=True)  # List of backup URLs

    # EPG
    epg_url = Column(String(1000), nullable=True)

    # Health check settings
    last_sync = Column(DateTime(timezone=True), nullable=True)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    health_check_enabled = Column(Boolean, default=True)
    health_check_timeout = Column(Integer, default=10)  # seconds

    # Metadata
    total_channels = Column(Integer, default=0)
    active_channels = Column(Integer, default=0)
    total_vod_movies = Column(Integer, default=0)
    total_vod_series = Column(Integer, default=0)
    status = Column(String(50), nullable=True)  # e.g., 'active', 'error', 'syncing'
    status_message = Column(Text, nullable=True)  # Detailed status message

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    streams = relationship("ChannelStream", back_populates="provider", cascade="all, delete-orphan")
    vod_movies = relationship("VODMovie", back_populates="provider", cascade="all, delete-orphan")
    vod_series = relationship("VODSeries", back_populates="provider", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Provider(id={self.id}, name='{self.name}', type='{self.provider_type}')>"
