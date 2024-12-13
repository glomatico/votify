from __future__ import annotations

import logging
from pathlib import Path

from .constants import AAC_AUDIO_QUALITIES
from .downloader_audio import DownloaderAudio
from .models import StreamInfoAudio

logger = logging.getLogger("votify")


class DownloaderEpisode(DownloaderAudio):
    def __init__(
        self,
        downloader_audio: DownloaderAudio,
    ):
        self.__dict__.update(downloader_audio.__dict__)

    def get_tags(
        self,
        episode_metadata: dict,
        show_metadata: dict,
    ) -> dict:
        release_date_datetime_obj = self.downloader.get_release_date_datetime_obj(
            episode_metadata["release_date"],
            episode_metadata["release_date_precision"],
        )
        tags = {
            "album": show_metadata["name"],
            "description": episode_metadata["description"],
            "media_type": "Podcast",
            "publisher": show_metadata.get("publisher"),
            "rating": "Explicit" if episode_metadata.get("explicit") else "Unknown",
            "release_date": self.downloader.get_release_date_tag(
                release_date_datetime_obj
            ),
            "release_year": str(release_date_datetime_obj.year),
            "title": episode_metadata["name"],
            "track": next(
                index
                for index in range(1, len(show_metadata["episodes"]["items"]) + 1)
                if show_metadata["episodes"]["items"][
                    len(show_metadata["episodes"]["items"]) - index
                ]["id"]
                == episode_metadata["id"]
            ),
            "url": f"https://open.spotify.com/episode/{episode_metadata['id']}",
        }
        return tags

    def get_cover_path(self, final_path: Path) -> Path:
        return final_path.with_suffix(".jpg")

    def download(
        self,
        *args,
        **kwargs,
    ):
        try:
            self._download(*args, **kwargs)
        finally:
            self.downloader.cleanup_temp_path()

    def _download(
        self,
        episode_id: str,
        episode_metadata: dict = None,
        show_metadata: dict = None,
        gid_metadata: dict = None,
        stream_info: StreamInfoAudio = None,
        playlist_metadata: dict = None,
        playlist_track: int = None,
        decryption_key: bytes = None,
    ):
        if not episode_metadata:
            logger.debug("Getting episode metadata")
            episode_metadata = self.downloader.spotify_api.get_episode(episode_id)
        if not show_metadata:
            logger.debug("Getting show metadata")
            show_metadata = self.downloader.spotify_api.get_show(
                episode_metadata["show"]["id"]
            )
        if not gid_metadata:
            logger.debug("Getting GID metadata")
            gid_metadata = self.downloader.get_gid_metadata(episode_id, "episode")
        if not stream_info:
            logger.debug("Getting stream info")
            stream_info = self.get_stream_info(gid_metadata, "episode")
        if not stream_info.file_id:
            logger.warning(
                "Episode is not available on Spotify's "
                "servers and no alternative found, skipping"
            )
            return
        if stream_info.quality != self.audio_quality:
            logger.warning(f"Quality has been changed to {stream_info.quality.value}")
        tags = self.get_tags(
            episode_metadata,
            show_metadata,
        )
        if playlist_metadata:
            tags = {
                **tags,
                **self.downloader.get_playlist_tags(
                    playlist_metadata,
                    playlist_track,
                ),
            }
        file_extension = self.get_file_extension()
        final_path = self.downloader.get_final_path(
            "episode",
            tags,
            file_extension,
        )
        cover_path = self.get_cover_path(final_path)
        cover_url = self.get_cover_url(episode_metadata)
        decrypted_path = None
        remuxed_path = None
        if final_path.exists() and not self.downloader.overwrite:
            logger.warning(f'Track already exists at "{final_path}", skipping')
        else:
            decryption_key = (
                self.DEFAULT_EPISODE_DECRYPTION_KEY.hex()
                if self.audio_quality in AAC_AUDIO_QUALITIES
                else self.DEFAULT_EPISODE_DECRYPTION_KEY
            )
            encrypted_path = self.downloader.get_file_temp_path(
                episode_id,
                "_encrypted",
                file_extension,
            )
            decrypted_path = self.downloader.get_file_temp_path(
                episode_id,
                "_decrypted",
                file_extension,
            )
            remuxed_path = self.downloader.get_file_temp_path(
                episode_id,
                "_remuxed",
                file_extension,
            )
            logger.debug(f'Downloading to "{encrypted_path}"')
            self.download_stream_url(encrypted_path, stream_info.stream_url)
            logger.debug(
                f'Decrypting to "{decrypted_path}" and remuxing to "{remuxed_path}"'
            )
            self.decrypt(
                decryption_key,
                encrypted_path,
                decrypted_path,
                remuxed_path,
            )
        media_temp_path = (
            remuxed_path
            if remuxed_path is not None and remuxed_path.exists()
            else decrypted_path
        )
        self.downloader._final_processing(
            cover_path,
            cover_url,
            media_temp_path,
            final_path,
            tags,
            playlist_metadata,
            playlist_track,
        )
