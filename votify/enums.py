from enum import Enum


class AudioQuality(Enum):
    VORBIS_HIGH = "vorbis-high"
    VORBIS_MEDIUM = "vorbis-medium"
    VORBIS_LOW = "vorbis-low"
    AAC_MEDIUM = "aac-medium"
    AAC_HIGH = "aac-high"


class VideoFormat(Enum):
    MP4 = "mp4"
    WEBM = "webm"
    ASK = "ask"


class DownloadMode(Enum):
    YTDLP = "ytdlp"
    ARIA2C = "aria2c"


class RemuxModeAudio(Enum):
    FFMPEG = "ffmpeg"
    MP4BOX = "mp4box"
    MP4DECRYPT = "mp4decrypt"


class RemuxModeVideo(Enum):
    FFMPEG = "ffmpeg"
    MP4BOX = "mp4box"


class CoverSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra-large"
