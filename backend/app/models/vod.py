"""VOD (Video on Demand) database models."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class VODMovie(Base):
    """VOD Movie model."""

    __tablename__ = "vod_movies"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Movie info
    title = Column(String(500), nullable=False, index=True)
    normalized_title = Column(String(500), nullable=False, index=True)
    year = Column(Integer, nullable=True, index=True)
    tmdb_id = Column(String(50), nullable=True, index=True)
    imdb_id = Column(String(50), nullable=True, index=True)

    # Classification
    genre = Column(String(255), nullable=True, index=True)
    rating = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes

    # Media info
    stream_url = Column(Text, nullable=False)
    stream_id = Column(String(255), nullable=True)
    cover_url = Column(String(1000), nullable=True)
    backdrop_url = Column(String(1000), nullable=True)
    quality = Column(String(50), nullable=True)  # 1080p, 4K, etc.

    # Description
    plot = Column(Text, nullable=True)
    director = Column(String(255), nullable=True)
    cast = Column(JSON, nullable=True)  # List of actors

    # Status
    is_active = Column(Boolean, default=True)
    strm_file_path = Column(String(1000), nullable=True)  # Path to generated .strm file
    last_check = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional provider metadata

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    provider = relationship("Provider", back_populates="vod_movies")

    def __repr__(self):
        return f"<VODMovie(id={self.id}, title='{self.title}', year={self.year})>"


class VODSeries(Base):
    """VOD TV Series model."""

    __tablename__ = "vod_series"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Series info
    title = Column(String(500), nullable=False, index=True)
    normalized_title = Column(String(500), nullable=False, index=True)
    year = Column(Integer, nullable=True, index=True)
    tmdb_id = Column(String(50), nullable=True, index=True)
    imdb_id = Column(String(50), nullable=True, index=True)

    # Classification
    genre = Column(String(255), nullable=True, index=True)
    rating = Column(Float, nullable=True)

    # Media info
    series_id = Column(String(255), nullable=True)
    cover_url = Column(String(1000), nullable=True)
    backdrop_url = Column(String(1000), nullable=True)

    # Description
    plot = Column(Text, nullable=True)
    cast = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    episode_count = Column(Integer, default=0)
    season_count = Column(Integer, default=0)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    provider = relationship("Provider", back_populates="vod_series")
    episodes = relationship("VODEpisode", back_populates="series", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VODSeries(id={self.id}, title='{self.title}', seasons={self.season_count})>"


class VODEpisode(Base):
    """VOD TV Episode model."""

    __tablename__ = "vod_episodes"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("vod_series.id", ondelete="CASCADE"), nullable=False, index=True)

    # Episode info
    title = Column(String(500), nullable=True)
    season_number = Column(Integer, nullable=False, index=True)
    episode_number = Column(Integer, nullable=False, index=True)
    episode_id = Column(String(255), nullable=True)

    # Media info
    stream_url = Column(Text, nullable=False)
    cover_url = Column(String(1000), nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    quality = Column(String(50), nullable=True)

    # Description
    plot = Column(Text, nullable=True)
    air_date = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    strm_file_path = Column(String(1000), nullable=True)
    last_check = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    series = relationship("VODSeries", back_populates="episodes")

    def __repr__(self):
        return f"<VODEpisode(id={self.id}, series_id={self.series_id}, S{self.season_number:02d}E{self.episode_number:02d})>"
