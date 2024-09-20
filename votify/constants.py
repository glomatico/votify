from __future__ import annotations

from .enums import Quality

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

QUALITY_X_FORMAT_ID_MAPPING = {
    Quality.HIGH: "OGG_VORBIS_320",
    Quality.MEDIUM: "OGG_VORBIS_160",
    Quality.LOW: "OGG_VORBIS_96",
}

X_NOT_FOUND_STRING = "{} not found at {}"
