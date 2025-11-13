"""User authentication models."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Role-based access control
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x], name='userrole'), default=UserRole.VIEWER.value, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)  # Legacy field, kept for compatibility

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    viewing_history = relationship("ViewingHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN or self.is_superuser


class UserFavorite(Base):
    """User favorite channels."""

    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=True)
    vod_movie_id = Column(Integer, ForeignKey("vod_movies.id", ondelete="CASCADE"), nullable=True)
    vod_series_id = Column(Integer, ForeignKey("vod_series.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="favorites")
    channel = relationship("Channel")
    vod_movie = relationship("VODMovie")
    vod_series = relationship("VODSeries")

    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, channel_id={self.channel_id})>"


class ViewingHistory(Base):
    """User viewing history for analytics."""

    __tablename__ = "viewing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="SET NULL"), nullable=True)
    vod_movie_id = Column(Integer, ForeignKey("vod_movies.id", ondelete="SET NULL"), nullable=True)
    vod_series_id = Column(Integer, ForeignKey("vod_series.id", ondelete="SET NULL"), nullable=True)

    # Viewing details
    stream_url = Column(String(2048), nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # How long they watched
    completed = Column(Boolean, default=False)  # Did they finish?

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="viewing_history")
    channel = relationship("Channel")
    vod_movie = relationship("VODMovie")
    vod_series = relationship("VODSeries")

    def __repr__(self):
        return f"<ViewingHistory(user_id={self.user_id}, channel_id={self.channel_id}, started_at={self.started_at})>"
