"""Application settings database model."""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AppSettings(Base):
    """Application settings model - stores user preferences."""

    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)  # Text to match migration, can store JSON as string
    value_type = Column(String(50), nullable=True)  # 'string', 'integer', 'boolean', etc.
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AppSettings(key='{self.key}')>"
