import datetime
from dataclasses import dataclass
from typing import Any

from mutagen.mp4 import MP4FreeForm

from .enums import MediaRating, MediaType


@dataclass
class SpotifyUrlInfo:
    media_type: str
    media_id: str
    intl: str | None = None


@dataclass
class DecryptionKey:
    decryption_key: str | bytes
    key_id: str = "0" * 32


@dataclass
class StreamInfo:
    stream_url: str | list[str]
    widevine_pssh: str
    file_format: str
    actual_file_format: str | None = None
    file_id: str | bytes | None = None


@dataclass
class StreamInfoAv:
    audio_track: StreamInfo
    video_track: StreamInfo = None


@dataclass
class PlaylistTags:
    id: str = None
    artist: str = None
    title: str = None
    track: int = None
    track_total: int = None


@dataclass
class MediaTags:
    media_id: str = None
    album: str = None
    album_artist: str = None
    artist: str = None
    compilation: bool = None
    composer: str = None
    copyright: str = None
    date: datetime.date | str = None
    description: str = None
    disc: int = None
    disc_total: int = None
    isrc: str = None
    label: str = None
    lyrics: str = None
    media_type: MediaType = None
    producer: str = None
    publisher: str = None
    rating: MediaRating = None
    title: str = None
    track: int = None
    track_total: int = None
    url: str = None

    def as_mp4_tags(self, date_format: str = None) -> dict[str, list[Any]]:
        disc_mp4 = [
            [
                self.disc if self.disc is not None else 0,
                self.disc_total if self.disc_total is not None else 0,
            ]
        ]
        if disc_mp4[0][0] == 0 and disc_mp4[0][1] == 0:
            disc_mp4 = None

        track_mp4 = [
            [
                self.track if self.track is not None else 0,
                self.track_total if self.track_total is not None else 0,
            ]
        ]
        if track_mp4[0][0] == 0 and track_mp4[0][1] == 0:
            track_mp4 = None

        if isinstance(self.date, datetime.date):
            if date_format is None:
                date_mp4 = self.date.isoformat()
            else:
                date_mp4 = self.date.strftime(date_format)
        elif isinstance(self.date, str):
            date_mp4 = self.date
        else:
            date_mp4 = None

        mp4_tags = {
            "\xa9alb": self.album,
            "aART": self.album_artist,
            "\xa9ART": self.artist,
            "\xa9wrt": self.composer,
            "cpil": bool(self.compilation) if self.compilation is not None else None,
            "cprt": self.copyright,
            "\xa9day": date_mp4,
            "desc": self.description,
            "disk": disc_mp4,
            "----:com.apple.iTunes:ISRC": (
                MP4FreeForm(self.isrc.encode("utf-8"))
                if self.isrc is not None
                else None
            ),
            "----:com.apple.iTunes:LABEL": (
                MP4FreeForm(self.label.encode("utf-8"))
                if self.label is not None
                else None
            ),
            "\xa9lyr": self.lyrics,
            "stik": int(self.media_type) if self.media_type is not None else None,
            "\xa9prd": self.producer,
            "\xa9pub": self.publisher,
            "rtng": int(self.rating) if self.rating is not None else None,
            "\xa9nam": self.title,
            "trkn": track_mp4,
            "\xa9url": self.url,
        }
        return {
            k: ([v] if not isinstance(v, (list, bool)) else v)
            for k, v in mp4_tags.items()
            if v is not None
        }

    def as_vorbis_tags(self, date_format: str = None) -> dict[str, list[Any]]:
        if isinstance(self.date, datetime.date):
            if date_format is None:
                date_flac = self.date.isoformat()
            else:
                date_flac = self.date.strftime(date_format)
        elif isinstance(self.date, str):
            date_flac = self.date
        else:
            date_flac = None

        flac_tags = {
            "ALBUM": [self.album],
            "ALBUMARTIST": [self.album_artist],
            "ARTIST": [self.artist],
            "COMPOSER": [self.composer],
            "COPYRIGHT": [self.copyright],
            "DESCRIPTION": [self.description],
            "YEAR": [date_flac],
            "DISCNUMBER": [str(self.disc)],
            "DISCTOTAL": [str(self.disc_total)],
            "ISRC": [self.isrc],
            "LABEL": [self.label],
            "LYRICS": [self.lyrics],
            "PRODUCER": [self.producer],
            "PUBLISHER": [self.publisher],
            "TITLE": [self.title],
            "TRACKNUMBER": [str(self.track)],
            "TRACKTOTAL": [str(self.track_total)],
            "URL": [self.url],
        }
        return {k: v for k, v in flac_tags.items() if v[0] is not None}


@dataclass
class MediaLyrics:
    synced: str
    unsynced: str


@dataclass
class SpotifyMedia:
    media_id: str
    media_metadata: dict | None = None
    album_metadata: dict | None = None
    show_metadata: dict | None = None
    playlist_metadata: dict | None = None
    tags: MediaTags | None = None
    playlist_tags: PlaylistTags | None = None
    cover_url: str | None = None
    lyrics: MediaLyrics | None = None
    stream_info: StreamInfoAv | None = None
    decryption_key: DecryptionKey | None = None
    flat_filter_result: Any = None
