"""EPG (Electronic Program Guide) database models."""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EPGProgram(Base):
    """EPG Program model."""

    __tablename__ = "epg_programs"

    id = Column(Integer, primary_key=True, index=True)
    channel_epg_id = Column(String(255), nullable=False, index=True)  # EPG channel ID
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Time
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    category = Column(String(255), nullable=True)
    icon = Column(String(1000), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EPGProgram(channel_epg_id='{self.channel_epg_id}', title='{self.title}', start={self.start_time})>"
