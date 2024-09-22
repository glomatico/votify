from __future__ import annotations

from .enums import AudioQuality, VideoFormat

EXCLUDED_CONFIG_FILE_PARAMS = (
    "urls",
    "config_path",
    "read_urls_as_txt",
    "no_config_file",
    "version",
    "help",
)

VORBIS_TAGS_MAPPING = {
    "album": "ALBUM",
    "album_artist": "ALBUMARTIST",
    "artist": "ARTIST",
    "composer": "COMPOSER",
    "copyright": "COPYRIGHT",
    "description": "DESCRIPTION",
    "disc": "DISC",
    "disc_total": "DISCTOTAL",
    "isrc": "ISRC",
    "label": "LABEL",
    "lyrics": "LYRICS",
    "publisher": "PUBLISHER",
    "producer": "PRODUCER",
    "release_date": "YEAR",
    "title": "TITLE",
    "track": "TRACKNUMBER",
    "track_total": "TRACKTOTAL",
    "url": "URL",
}

MP4_TAGS_MAP = {
    "album": "\xa9alb",
    "album_artist": "aART",
    "artist": "\xa9ART",
    "composer": "\xa9wrt",
    "copyright": "cprt",
    "lyrics": "\xa9lyr",
    "publisher": "\xa9pub",
    "producer": "\xa9prd",
    "rating": "rtng",
    "release_date": "\xa9day",
    "title": "\xa9nam",
    "url": "\xa9url",
}

AUDIO_QUALITY_X_FORMAT_ID_MAPPING = {
    AudioQuality.VORBIS_HIGH: "OGG_VORBIS_320",
    AudioQuality.VORBIS_MEDIUM: "OGG_VORBIS_160",
    AudioQuality.VORBIS_LOW: "OGG_VORBIS_96",
}

X_NOT_FOUND_STRING = "{} not found at {}"

PREMIUM_SONG_QUALITIES = (AudioQuality.VORBIS_HIGH,)
