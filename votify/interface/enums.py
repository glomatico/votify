from __future__ import annotations

from enum import Enum

from .constants import (
    FORMAT_ID_MAP,
    MEDIA_RATING_STR_MAP,
    MEDIA_TYPE_STR_MAP,
    MP4_AUDIO_QUALITIES,
    PREMIUM_AUDIO_QUALITIES,
    VORBIS_AUDIO_QUALITIES,
)


class MediaRating(Enum):
    NONE = 0
    EXPLICIT = 1
    CLEAN = 2

    def __str__(self) -> str:
        return MEDIA_RATING_STR_MAP[self.value]

    def __int__(self) -> int:
        return self.value


class MediaType(Enum):
    SONG = 1
    MUSIC_VIDEO = 6
    PODCAST = 21
    PODCAST_VIDEO = 0

    def __str__(self) -> str:
        return MEDIA_TYPE_STR_MAP[self.value]

    def __int__(self) -> int:
        if self.value == 0:
            return 21
        return self.value


class CoverSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra-large"


class AudioQuality(Enum):
    VORBIS_HIGH = "vorbis-high"
    VORBIS_MEDIUM = "vorbis-medium"
    VORBIS_LOW = "vorbis-low"
    AAC_MEDIUM = "aac-medium"
    AAC_HIGH = "aac-high"
    FLAC = "flac"

    @property
    def premium(self) -> bool:
        return self.value in PREMIUM_AUDIO_QUALITIES

    @property
    def mp4(self) -> bool:
        return self.value in MP4_AUDIO_QUALITIES

    @property
    def file_format(self) -> str | None:
        if self.value in MP4_AUDIO_QUALITIES:
            return "mp4"
        elif self.value in VORBIS_AUDIO_QUALITIES:
            return "ogg"
        return None

    @property
    def actual_file_format(self) -> str | None:
        if self.value == "flac":
            return "flac"
        elif self.value in MP4_AUDIO_QUALITIES:
            return "m4a"
        elif self.value in VORBIS_AUDIO_QUALITIES:
            return "ogg"
        return None

    @property
    def format_id(self) -> str | None:
        return FORMAT_ID_MAP.get(self.value)

    @property
    def previous_quality(self) -> "AudioQuality" | None:
        if not self.mp4:
            if self.value == "vorbis-high":
                return AudioQuality.VORBIS_MEDIUM
            elif self.value == "vorbis-medium":
                return AudioQuality.VORBIS_LOW
            elif self.value == "flac":
                return AudioQuality.AAC_HIGH
        else:
            if self.value == "aac-high":
                return AudioQuality.AAC_MEDIUM
        return None


class VideoFormat(Enum):
    MP4 = "mp4"
    WEBM = "webm"
    ASK = "ask"


class VideoResolution(Enum):
    R144P = "144p"
    R240P = "240p"
    R360P = "360p"
    R480P = "480p"
    R576P = "576p"
    R720P = "720p"
    R1080P = "1080p"

    def __int__(self) -> int:
        return int(self.value[:-1])


class ArtistMediaOption(Enum):
    ALBUMS = "albums"
    COMPILATIONS = "compilations"
    SINGLES = "singles"
    VIDEOS = "videos"
