import re

MEDIA_TYPE_STR_MAP = {
    1: "Song",
    6: "Music Video",
    21: "Podcast",
}

MEDIA_RATING_STR_MAP = {
    0: "None",
    1: "Explicit",
    2: "Clean",
}

URL_INFO_RE = re.compile(
    r"https://open\.spotify\.com(?:/intl-(?P<intl>[a-z]{2}))?/(?P<media_type>album|playlist|track|show|episode|artist)/(?P<media_id>\w{22})"
)

COVER_SIZE_ID_MAP_SONG = {
    "small": "ab67616d00004851",
    "medium": "ab67616d00001e02",
    "large": "ab67616d0000b273",
    "extra-large": "ab67616d000082c1",
}

COVER_SIZE_ID_MAP_EPISODE = {
    "small": "ab6765630000f68d",
    "medium": "ab67656300005f1f",
    "large": "ab6765630000ba8a",
    "extra-large": "ab6765630000ba8a",
}

COVER_SIZE_ID_MAP_VIDEO = {
    "small": "ab6742d3000052b7",
    "medium": "ab6742d3000052b7",
    "large": "ab6742d3000053b7",
    "extra-large": "ab6742d3000053b7",
}

DEFAULT_EPISODE_DECRYPTION_KEY = (
    b"\xde\xad\xbe\xef\xde\xad\xbe\xef\xde\xad\xbe\xef\xde\xad\xbe\xef"  # lmao wtf
)

FORMAT_ID_MAP = {
    "vorbis-low": "0",
    "vorbis-medium": "1",
    "vorbis-high": "2",
    "aac-medium": "10",
    "aac-high": "11",
    "flac-flac": "16",
    "flac-mp4": "17",
}

FORMAT_NAME_MAP = {
    "vorbis-low": "OGG_VORBIS_96",
    "vorbis-medium": "OGG_VORBIS_160",
    "vorbis-high": "OGG_VORBIS_320",
    "aac-medium": "MP4_128",
    "aac-high": "MP4_256",
    "flac-flac": "FLAC_FLAC",
    "flac-mp4": "MP4_FLAC",
}

MP4_AUDIO_QUALITIES = {"aac-high", "aac-medium", "flac-mp4"}
VORBIS_AUDIO_QUALITIES = {"vorbis-high", "vorbis-medium", "vorbis-low"}
FLAC_AUDIO_QUALITIES = {"flac-flac"}
PREMIUM_AUDIO_QUALITIES = {"aac-high", "vorbis-high", "flac-flac", "flac-mp4"}
