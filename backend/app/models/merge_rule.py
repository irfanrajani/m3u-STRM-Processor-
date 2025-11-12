"""
Merge Rules Model
Allows users to create custom rules for channel merging
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MergeRule(Base):
    """Custom rules for controlling automatic channel merging"""
    
    __tablename__ = "merge_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule configuration
    rule_type = Column(String(50), nullable=False)  # 'never_merge', 'always_merge', 'custom'
    pattern1 = Column(String(500), nullable=False, index=True)  # First channel pattern (regex or exact)
    pattern2 = Column(String(500), nullable=True)  # Second channel pattern (for never_merge)
    region1 = Column(String(100), nullable=True)  # Optional region filter
    region2 = Column(String(100), nullable=True)  # Optional region filter for pattern2
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=True)
    
    # Priority and status
    priority = Column(Integer, default=0)  # Higher priority rules are checked first
    enabled = Column(Boolean, default=True, index=True)
    
    # Metadata
    reason = Column(Text, nullable=True)  # User's explanation for the rule
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("Provider")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<MergeRule(id={self.id}, type='{self.rule_type}', pattern='{self.pattern1}')>"
    
    def matches(self, channel1_name: str, channel2_name: str, 
                channel1_region: str = None, channel2_region: str = None) -> bool:
        """Check if this rule applies to the given channel pair"""
        import re
        
        # Check pattern1 against channel1
        if self.pattern1:
            if not re.search(self.pattern1, channel1_name, re.IGNORECASE):
                return False
        
        # Check pattern2 against channel2 (for never_merge rules)
        if self.pattern2:
            if not re.search(self.pattern2, channel2_name, re.IGNORECASE):
                return False
        
        # Check region filters
        if self.region1 and channel1_region and self.region1 != channel1_region:
            return False
        
        if self.region2 and channel2_region and self.region2 != channel2_region:
            return False
        
        return True
