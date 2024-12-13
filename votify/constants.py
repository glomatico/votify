from __future__ import annotations

from .enums import AudioQuality, CoverSize

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
    AudioQuality.AAC_HIGH: "MP4_256",
    AudioQuality.AAC_MEDIUM: "MP4_128",
}

VORBIS_AUDIO_QUALITIES = (
    AudioQuality.VORBIS_HIGH,
    AudioQuality.VORBIS_MEDIUM,
    AudioQuality.VORBIS_LOW,
)
AAC_AUDIO_QUALITIES = (AudioQuality.AAC_HIGH, AudioQuality.AAC_MEDIUM)

X_NOT_FOUND_STRING = "{} not found at {}"

PREMIUM_AUDIO_QUALITIES = (AudioQuality.VORBIS_HIGH, AudioQuality.AAC_HIGH)

MEDIA_TYPE_MP4_MAPPING = {
    "Song": 1,
    "Podcast": 21,
    "Music video": 6,
}

COVER_SIZE_X_KEY_MAPPING_AUDIO = {
    CoverSize.SMALL: "ab67616d00004851",
    CoverSize.MEDIUM: "ab67616d00001e02",
    CoverSize.LARGE: "ab67616d0000b273",
    CoverSize.EXTRA_LARGE: "ab67616d000082c1",
}

COVER_SIZE_X_KEY_MAPPING_VIDEO = {
    CoverSize.SMALL: "ab6742d3000052b7",
    CoverSize.MEDIUM: "ab6742d3000052b7",
    CoverSize.LARGE: "ab6742d3000053b7",
    CoverSize.EXTRA_LARGE: "ab6742d3000053b7",
}
