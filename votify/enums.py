from enum import Enum


class Quality(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DownloadMode(Enum):
    YTDLP = "ytdlp"
    ARIA2C = "aria2c"
