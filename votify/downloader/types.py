from dataclasses import dataclass
import uuid

from ..interface.types import SpotifyMedia


@dataclass
class DownloadItem:
    media: SpotifyMedia
    uuid_: str = uuid.uuid4().hex[:8]
    final_path: str | None = None
    staged_path: str | None = None
    playlist_file_path: str | None = None
    synced_lyrics_path: str | None = None
    cover_path: str | None = None
