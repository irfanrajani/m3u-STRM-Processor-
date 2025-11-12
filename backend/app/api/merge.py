"""
Channel Merge Management API
View merge details, split channels, manage merge rules
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
import re

from app.core.database import get_db
from app.models.channel import Channel, ChannelStream
from app.models.merge_rule import MergeRule
from app.models.provider import Provider
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


class MergeDetailResponse(BaseModel):
    """Details about streams merged into a channel"""
    channel_id: int
    channel_name: str
    total_streams: int
    merge_methods: dict  # Count by merge method
    streams: List[dict]


class SplitChannelRequest(BaseModel):
    """Request to split streams into new channel"""
    stream_ids: List[int]
    new_channel_name: Optional[str] = None
    reason: Optional[str] = None


class MergeRuleCreate(BaseModel):
    """Create a new merge rule"""
    rule_type: str  # 'never_merge', 'always_merge'
    pattern1: str
    pattern2: Optional[str] = None
    region1: Optional[str] = None
    region2: Optional[str] = None
    provider_id: Optional[int] = None
    priority: int = 0
    reason: Optional[str] = None


@router.get("/channels/{channel_id}/merge-details")
async def get_merge_details(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
) -> MergeDetailResponse:
    """
    Get detailed information about streams merged into this channel
    Shows confidence scores, merge methods, and original names
    """
    # Get channel with all streams
    result = await db.execute(
        select(Channel)
        .options(selectinload(Channel.streams).selectinload(ChannelStream.provider))
        .where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Count merge methods
    merge_methods = {}
    streams_data = []
    
    for stream in channel.streams:
        # Count methods
        method = stream.merge_method or 'unknown'
        merge_methods[method] = merge_methods.get(method, 0) + 1
        
        # Build stream data
        streams_data.append({
            'stream_id': stream.id,
            'provider_id': stream.provider_id,
            'provider_name': stream.provider.name if stream.provider else 'Unknown',
            'original_name': stream.original_name or channel.name,
            'stream_url': stream.stream_url,
            'resolution': stream.resolution,
            'quality_score': stream.quality_score,
            'is_active': stream.is_active,
            'priority_order': stream.priority_order,
            'merge_confidence': stream.merge_confidence,
            'merge_method': stream.merge_method,
            'merge_reason': stream.merge_reason,
            'manual_override': stream.manual_override,
            'last_check': stream.last_check.isoformat() if stream.last_check else None,
            'consecutive_failures': stream.consecutive_failures,
        })
    
    return MergeDetailResponse(
        channel_id=channel.id,
        channel_name=channel.name,
        total_streams=len(streams_data),
        merge_methods=merge_methods,
        streams=streams_data
    )


@router.post("/channels/{channel_id}/split")
async def split_channel(
    channel_id: int,
    request: SplitChannelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Split selected streams into a new channel
    This effectively "unmerges" incorrectly grouped streams
    """
    if not request.stream_ids:
        raise HTTPException(status_code=400, detail="No streams selected")
    
    # Get original channel
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    original_channel = result.scalar_one_or_none()
    if not original_channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Get streams to split
    result = await db.execute(
        select(ChannelStream).where(
            ChannelStream.id.in_(request.stream_ids),
            ChannelStream.channel_id == channel_id
        )
    )
    streams_to_split = result.scalars().all()
    
    if not streams_to_split:
        raise HTTPException(status_code=404, detail="No streams found to split")
    
    # Determine new channel name
    if request.new_channel_name:
        new_channel_name = request.new_channel_name
    else:
        # Use the original name from the first stream
        new_channel_name = streams_to_split[0].original_name or f"{original_channel.name} (Split)"
    
    # Create new channel
    new_channel = Channel(
        name=new_channel_name,
        normalized_name=Channel.normalize_name(new_channel_name),
        category=original_channel.category,
        region=original_channel.region,
        variant=original_channel.variant,
        logo_url=original_channel.logo_url,
        enabled=True,
        stream_count=len(streams_to_split)
    )
    db.add(new_channel)
    await db.flush()
    
    # Move streams to new channel
    await db.execute(
        update(ChannelStream)
        .where(ChannelStream.id.in_(request.stream_ids))
        .values(
            channel_id=new_channel.id,
            manual_override=True,
            merge_method='manual_split',
            merge_reason=request.reason or f"Split by user {current_user.username}"
        )
    )
    
    # Update stream counts
    original_channel.stream_count = len([s for s in original_channel.streams if s.id not in request.stream_ids])
    
    await db.commit()
    await db.refresh(new_channel)
    
    return {
        'success': True,
        'original_channel_id': channel_id,
        'new_channel_id': new_channel.id,
        'new_channel_name': new_channel.name,
        'streams_moved': len(streams_to_split),
        'message': f"Created new channel '{new_channel.name}' with {len(streams_to_split)} streams"
    }


@router.post("/channels/{channel_id}/merge-with/{target_channel_id}")
async def merge_channels(
    channel_id: int,
    target_channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually merge all streams from channel_id into target_channel_id
    Opposite of split - combines two channels
    """
    if channel_id == target_channel_id:
        raise HTTPException(status_code=400, detail="Cannot merge channel with itself")
    
    # Get both channels
    result = await db.execute(
        select(Channel).where(Channel.id.in_([channel_id, target_channel_id]))
    )
    channels = {c.id: c for c in result.scalars().all()}
    
    if len(channels) != 2:
        raise HTTPException(status_code=404, detail="One or both channels not found")
    
    source_channel = channels[channel_id]
    target_channel = channels[target_channel_id]
    
    # Move all streams
    await db.execute(
        update(ChannelStream)
        .where(ChannelStream.channel_id == channel_id)
        .values(
            channel_id=target_channel_id,
            manual_override=True,
            merge_method='manual_merge',
            merge_reason=f"Manually merged by user {current_user.username}"
        )
    )
    
    # Update stream count
    stream_count = await db.scalar(
        select(func.count(ChannelStream.id))
        .where(ChannelStream.channel_id == target_channel_id)
    )
    target_channel.stream_count = stream_count
    
    # Delete source channel
    await db.delete(source_channel)
    
    await db.commit()
    
    return {
        'success': True,
        'target_channel_id': target_channel_id,
        'streams_merged': stream_count,
        'message': f"Merged '{source_channel.name}' into '{target_channel.name}'"
    }


# ===== MERGE RULES MANAGEMENT =====

@router.get("/merge-rules")
async def get_merge_rules(
    db: AsyncSession = Depends(get_db),
    enabled_only: bool = Query(True)
):
    """Get all merge rules"""
    query = select(MergeRule).order_by(MergeRule.priority.desc(), MergeRule.created_at.desc())
    
    if enabled_only:
        query = query.where(MergeRule.enabled == True)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return [
        {
            'id': rule.id,
            'rule_type': rule.rule_type,
            'pattern1': rule.pattern1,
            'pattern2': rule.pattern2,
            'region1': rule.region1,
            'region2': rule.region2,
            'provider_id': rule.provider_id,
            'priority': rule.priority,
            'enabled': rule.enabled,
            'reason': rule.reason,
            'created_at': rule.created_at.isoformat() if rule.created_at else None
        }
        for rule in rules
    ]


@router.post("/merge-rules")
async def create_merge_rule(
    rule_data: MergeRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new merge rule
    Examples:
    - Never merge "ABC East" with "ABC West"
    - Always merge "HBO" streams regardless of variant
    """
    # Validate regex patterns
    try:
        re.compile(rule_data.pattern1)
        if rule_data.pattern2:
            re.compile(rule_data.pattern2)
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {e}")
    
    # Create rule
    new_rule = MergeRule(
        rule_type=rule_data.rule_type,
        pattern1=rule_data.pattern1,
        pattern2=rule_data.pattern2,
        region1=rule_data.region1,
        region2=rule_data.region2,
        provider_id=rule_data.provider_id,
        priority=rule_data.priority,
        reason=rule_data.reason,
        created_by=current_user.id,
        enabled=True
    )
    
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    
    return {
        'success': True,
        'rule_id': new_rule.id,
        'message': 'Merge rule created successfully'
    }


@router.delete("/merge-rules/{rule_id}")
async def delete_merge_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a merge rule"""
    result = await db.execute(
        select(MergeRule).where(MergeRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db.delete(rule)
    await db.commit()
    
    return {
        'success': True,
        'message': 'Merge rule deleted successfully'
    }


@router.put("/merge-rules/{rule_id}/toggle")
async def toggle_merge_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Enable/disable a merge rule"""
    result = await db.execute(
        select(MergeRule).where(MergeRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.enabled = not rule.enabled
    await db.commit()
    
    return {
        'success': True,
        'enabled': rule.enabled,
        'message': f"Rule {'enabled' if rule.enabled else 'disabled'}"
    }
