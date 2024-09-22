from enum import Enum


class AudioQuality(Enum):
    VORBIS_HIGH = "high"
    VORBIS_MEDIUM = "medium"
    VORBIS_LOW = "low"


class VideoFormat(Enum):
    MP4 = "mp4"
    WEBM = "webm"
    ASK = "ask"


class DownloadMode(Enum):
    YTDLP = "ytdlp"
    ARIA2C = "aria2c"
