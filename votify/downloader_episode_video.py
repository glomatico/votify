from __future__ import annotations

import logging

from .downloader_episode import DownloaderEpisode
from .downloader_video import DownloaderVideo

logger = logging.getLogger("votify")


class DownloaderEpisodeVideo(DownloaderVideo):
    def __init__(
        self,
        downloader_video: DownloaderVideo,
        downloader_episode: DownloaderEpisode,
    ):
        self.__dict__.update(downloader_video.__dict__)
        self.downloader_episode = downloader_episode

    def get_video_gid(self, gid_metadata: dict) -> str | None:
        if not gid_metadata.get("video"):
            return None
        return gid_metadata["video"][0]["file_id"]

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
        playlist_metadata: dict = None,
        playlist_track: int = None,
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
        video_gid = self.get_video_gid(gid_metadata)
        if not video_gid:
            logger.warning("Episode has no video, skipping")
            return
        stream_info = self.get_stream_info(video_gid)
        if (
            stream_info.encryption_data_widevine
            and not self.downloader.wvd_path.exists()
        ):
            logger.warning(
                "Podcast video has Widevine encryption, but no .wvd file was found at "
                f'"{self.downloader.wvd_path}", skipping'
            )
            return
        tags = self.downloader_episode.get_tags(
            episode_metadata,
            show_metadata,
        )
        file_extension = self.get_file_extension(
            stream_info.file_type_video,
            stream_info.file_type_audio,
        )
        final_path = self.downloader.get_final_path(
            "episode",
            tags,
            file_extension,
        )
        cover_path = self.get_cover_path(final_path)
        cover_url = self.downloader_episode.get_cover_url(show_metadata)
        remuxed_path = None
        if final_path.exists() and not self.downloader.overwrite:
            logger.warning(f'Episode already exists at "{final_path}", skipping')
            return
        else:
            key_id, decryption_key = (
                self.downloader.get_widevine_decryption_key(
                    stream_info.encryption_data_widevine,
                    "video",
                )
                if stream_info.encryption_data_widevine
                else (None, None)
            )
            encrypted_path_video = self.downloader.get_file_temp_path(
                episode_id,
                "_video_encrypted",
                file_extension,
            )
            encrypted_path_audio = self.downloader.get_file_temp_path(
                episode_id,
                "_audio_encrypted",
                file_extension,
            )
            decrypted_path_video = self.downloader.get_file_temp_path(
                episode_id,
                "_video_decrypted",
                file_extension,
            )
            decrypted_path_audio = self.downloader.get_file_temp_path(
                episode_id,
                "_audio_decrypted",
                file_extension,
            )
            remuxed_path = self.downloader.get_file_temp_path(
                episode_id,
                "_remuxed",
                file_extension,
            )
            temp_path_video = encrypted_path_video if key_id else decrypted_path_video
            temp_path_audio = encrypted_path_audio if key_id else decrypted_path_audio
            logger.debug(f'Downloading video to "{temp_path_video}"')
            self.download_segments(stream_info.segment_urls_video, temp_path_video)
            logger.debug(f'Downloading audio to "{temp_path_audio}"')
            self.download_segments(stream_info.segment_urls_audio, temp_path_audio)
            logger.debug(f'Remuxing to "{remuxed_path}"')
            self.remux(
                decrypted_path_video,
                decrypted_path_audio,
                remuxed_path,
                key_id,
                decryption_key,
                encrypted_path_video,
                encrypted_path_audio,
            )
        self.downloader._final_processing(
            cover_path,
            cover_url,
            remuxed_path,
            final_path,
            tags,
            playlist_metadata,
            playlist_track,
        )
