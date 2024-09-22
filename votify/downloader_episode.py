from __future__ import annotations

import logging
from pathlib import Path

from .downloader import Downloader
from .models import StreamInfo

logger = logging.getLogger("votify")


class DownloaderEpisode:
    def __init__(
        self,
        downloader: Downloader,
    ):
        self.downloader = downloader

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
            if self.downloader.temp_path.exists():
                logger.debug(f'Cleaning up "{self.downloader.temp_path}"')
                self.downloader.cleanup_temp_path()

    def _download(
        self,
        episode_id: str = None,
        episode_metadata: dict = None,
        show_metadata: dict = None,
        gid_metadata: dict = None,
        stream_info: StreamInfo = None,
        playlist_metadata: dict = None,
        playlist_track: int = None,
        decryption_key: bytes = None,
    ):
        if not episode_id:
            raise RuntimeError("Episode ID is required")
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
            stream_info = self.downloader.get_stream_info(gid_metadata, "episode")
        if not stream_info.file_id:
            logger.warning(
                "Episode is not available on Spotify's "
                "servers and no alternative found, skipping"
            )
            return
        if stream_info.quality != self.downloader.quality:
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
        final_path = self.downloader.get_final_path(
            "episode",
            tags,
            ".ogg",
        )
        cover_path = self.get_cover_path(final_path)
        cover_url = self.downloader.get_cover_url(episode_metadata)
        decrypted_path = None
        if final_path.exists() and not self.downloader.overwrite:
            logger.warning(f'Track already exists at "{final_path}", skipping')
            return
        else:
            if not decryption_key:
                logger.debug("Getting decryption key")
                decryption_key = self.downloader.get_decryption_key(stream_info.file_id)
            encrypted_path = self.downloader.get_encrypted_path(episode_id)
            decrypted_path = self.downloader.get_decrypted_path(episode_id)
            logger.debug(f'Downloading to "{encrypted_path}"')
            self.downloader.download_stream_url(encrypted_path, stream_info.stream_url)
            logger.debug(f'Decrypting to "{decrypted_path}"')
            self.downloader.decrypt(
                decryption_key,
                encrypted_path,
                decrypted_path,
            )
        if (
            self.downloader.save_cover
            and cover_path.exists()
            and not self.downloader.overwrite
        ):
            logger.debug(f'Cover already exists at "{cover_path}", skipping')
            return
        elif self.downloader.save_cover and cover_url is not None:
            logger.debug(f'Saving cover to "{cover_path}"')
            self.downloader.save_cover_file(cover_path, cover_url)
            return
        if decrypted_path:
            logger.debug("Applying tags")
            self.downloader.apply_tags(decrypted_path, tags, cover_url)
            logger.debug(f'Moving to "{final_path}"')
            self.downloader.move_to_final_path(decrypted_path, final_path)
        if self.downloader.save_playlist and playlist_metadata:
            playlist_file_path = self.downloader.get_playlist_file_path(tags)
            logger.debug(f'Updating M3U8 playlist from "{playlist_file_path}"')
            self.downloader.update_playlist_file(
                playlist_file_path,
                final_path,
                playlist_track,
            )
