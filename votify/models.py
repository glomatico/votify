from __future__ import annotations

from dataclasses import dataclass

from .enums import AudioQuality


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
class StreamInfoAudio:
    stream_url: str = None
    file_id: str = None
    widevine_pssh: str = None
    quality: AudioQuality = None


@dataclass
class StreamInfoVideo:
    segment_urls_video: list[str] = None
    segment_urls_audio: list[str] = None
    file_type_video: str = None
    file_type_audio: str = None
    encryption_data_widevine: str = None
