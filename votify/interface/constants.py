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
    "aac-high": "11",
    "aac-medium": "10",
    "flac": "17",
}

MP4_AUDIO_QUALITIES = {"aac-high", "aac-medium", "flac"}
VORBIS_AUDIO_QUALITIES = {"vorbis-high", "vorbis-medium", "vorbis-low"}
PREMIUM_AUDIO_QUALITIES = {"aac-high", "vorbis-high"}
