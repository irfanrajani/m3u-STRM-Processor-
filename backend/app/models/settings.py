"""Application settings database model."""
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AppSettings(Base):
    """Application settings model - stores user preferences."""

    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=True)
    value_type = Column(String(50), nullable=True)  # 'string', 'integer', 'boolean', etc.
    description = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AppSettings(key='{self.key}')>"
