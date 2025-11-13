"""Database models."""
from app.models.provider import Provider
from app.models.channel import Channel, ChannelStream
from app.models.vod import VODMovie, VODSeries, VODEpisode
from app.models.epg import EPGProgram
from app.models.settings import AppSettings
from app.models.user import User, UserFavorite, ViewingHistory
from app.models.merge_rule import MergeRule

__all__ = [
    "Provider",
    "Channel",
    "ChannelStream",
    "VODMovie",
    "VODSeries",
    "VODEpisode",
    "EPGProgram",
    "AppSettings",
    "User",
    "UserFavorite",
    "ViewingHistory",
    "MergeRule",
]
