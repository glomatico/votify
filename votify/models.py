from __future__ import annotations

from dataclasses import dataclass

from .enums import Quality


@dataclass
class Lyrics:
    synced: str = None
    unsynced: str = None


@dataclass
class UrlInfo:
    type: str = None
    id: str = None


@dataclass
class DownloadQueueItem:
    playlist_metadata: dict = None
    album_metadata: dict = None
    show_metadata: dict = None
    media_metadata: dict = None


@dataclass
class StreamInfo:
    stream_url: str = None
    file_id: str = None
    quality: Quality = None
