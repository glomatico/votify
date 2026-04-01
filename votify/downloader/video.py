import asyncio
import logging
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.downloader.fragment import FragmentFD

from ..interface.types import SpotifyMedia
from .base import SpotifyBaseDownloader
from .enums import VideoRemuxMode
from .types import DownloadItem

logger = logging.getLogger(__name__)


class SpotifyVideoDownloader(SpotifyBaseDownloader):
    def __init__(
        self,
        base: SpotifyBaseDownloader,
        remux_mode: VideoRemuxMode = VideoRemuxMode.FFMPEG,
    ) -> None:
        self.__dict__.update(base.__dict__)

        self.remux_mode = remux_mode

    def _download_stream(
        self,
        input_path: str,
        segment_urls: list[str],
    ):
        logger.debug(f"Downloading video stream to '{input_path}'")

        Path(input_path).parent.mkdir(parents=True, exist_ok=True)
        segments_dict = [
            {"url": url, "frag_index": idx + 1} for idx, url in enumerate(segment_urls)
        ]
        ctx = {
            "filename": str(input_path),
            "total_frags": len(segments_dict),
        }
        info_dict = {}
        with YoutubeDL(
            {
                "quiet": True,
                "no_warnings": True,
                "noprogress": self.silent,
            },
        ) as ydl:
            try:
                fragment_downloader = FragmentFD(ydl, ydl.params)
                fragment_downloader._prepare_and_start_frag_download(
                    ctx,
                    info_dict,
                )
                fragment_downloader.download_and_append_fragments(
                    ctx,
                    segments_dict,
                    info_dict,
                )
            finally:
                fragment_downloader._finish_multiline_status()

    async def stage(
        self,
        encrypted_video_path: str,
        encrypted_audio_path: str,
        decrypted_video_path: str,
        decrypted_audio_path: str,
        staged_path: str,
        decryption_key: str | None,
        key_id: str | None,
    ) -> None:
        logger.debug(f"Staging video: {staged_path}")

        if decryption_key:
            if encrypted_video_path.lower().endswith(".webm"):
                await self._shaka_packager_decrypt(
                    encrypted_video_path,
                    decrypted_video_path,
                    decryption_key,
                    key_id,
                )
            else:
                await self._mp4decrypt_decrypt(
                    encrypted_video_path,
                    decrypted_video_path,
                    decryption_key,
                )

            if encrypted_audio_path.lower().endswith(".webm"):
                await self._shaka_packager_decrypt(
                    encrypted_audio_path,
                    decrypted_audio_path,
                    decryption_key,
                    key_id,
                )
            else:
                await self._mp4decrypt_decrypt(
                    encrypted_audio_path,
                    decrypted_audio_path,
                    decryption_key,
                )

        if self.remux_mode == VideoRemuxMode.FFMPEG:
            await self._ffmpeg_remux(
                decrypted_video_path,
                decrypted_audio_path,
                staged_path,
            )
        else:
            await self._mp4box_remux(
                decrypted_video_path,
                decrypted_audio_path,
                staged_path,
            )

    async def _shaka_packager_decrypt(
        self,
        input_path: str,
        output_path: str,
        decryption_key: str,
        key_id: str,
    ):
        await self.run_async_command(
            self.shaka_packager_full_path,
            "--quiet",
            f"stream=0,in={input_path},output={output_path}",
            "-enable_raw_key_decryption",
            "-keys",
            f"key_id={key_id}:key={decryption_key}",
            silent=self.silent,
        )

    async def _mp4decrypt_decrypt(
        self,
        input_path: Path,
        output_path: Path,
        decryption_key: str,
    ):
        await self.run_async_command(
            self.mp4decrypt_full_path,
            "--key",
            f"1:{decryption_key}",
            input_path,
            output_path,
            silent=self.silent,
        )

    async def _ffmpeg_remux(
        self,
        input_path_video: str,
        input_path_audio: str,
        output_path: str,
    ):
        await self.run_async_command(
            self.ffmpeg_full_path,
            "-loglevel",
            "error",
            "-y",
            "-i",
            input_path_video,
            "-i",
            input_path_audio,
            "-c",
            "copy",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            output_path,
            silent=self.silent,
        )

    async def _mp4box_remux(
        self,
        input_path_video: str,
        input_path_audio: str,
        output_path: str,
    ):
        await self.run_async_command(
            self.mp4box_full_path,
            "-quiet",
            "-itags",
            "artist=placeholder",
            "-keep-utc",
            "-add",
            input_path_video,
            "-add",
            input_path_audio,
            "-new",
            output_path,
            silent=self.silent,
        )

    async def download(self, item: DownloadItem) -> None:
        encrypted_video_path = self.get_temp_path(
            item.media.media_id,
            item.uuid_,
            f"{item.uuid_}_video_encrypted",
            "." + item.media.stream_info.video_track.file_format,
        )
        encrypted_audio_path = self.get_temp_path(
            item.media.media_id,
            item.uuid_,
            f"{item.uuid_}_audio_encrypted",
            "." + item.media.stream_info.audio_track.file_format,
        )
        decrypted_video_path = self.get_temp_path(
            item.media.media_id,
            item.uuid_,
            f"{item.uuid_}_video_decrypted",
            "." + item.media.stream_info.video_track.file_format,
        )
        decrypted_audio_path = self.get_temp_path(
            item.media.media_id,
            item.uuid_,
            f"{item.uuid_}_audio_decrypted",
            "." + item.media.stream_info.audio_track.file_format,
        )

        decryption_key, key_id = (
            (
                item.media.decryption_key.decryption_key,
                item.media.decryption_key.key_id,
            )
            if item.media.decryption_key
            else (None, None)
        )

        await asyncio.to_thread(
            self._download_stream,
            encrypted_video_path if decryption_key else decrypted_video_path,
            item.media.stream_info.video_track.stream_url,
        )
        await asyncio.to_thread(
            self._download_stream,
            encrypted_audio_path if decryption_key else decrypted_audio_path,
            item.media.stream_info.audio_track.stream_url,
        )

        await self.stage(
            encrypted_video_path=encrypted_video_path,
            encrypted_audio_path=encrypted_audio_path,
            decrypted_video_path=decrypted_video_path,
            decrypted_audio_path=decrypted_audio_path,
            staged_path=item.staged_path,
            decryption_key=decryption_key,
            key_id=key_id,
        )
        await self.apply_tags(
            item.staged_path,
            item.media.tags,
            item.media.cover_url,
        )

    def parse_item(self, media: SpotifyMedia) -> DownloadItem:
        item = DownloadItem(media=media)

        item.staged_path = self.get_temp_path(
            media.media_id,
            item.uuid_,
            "staged",
            ".mp4",
        )
        item.final_path = self.get_final_path(
            media.tags,
            ".mp4",
            media.playlist_tags,
        )
        if media.playlist_tags:
            item.playlist_file_path = self.get_playlist_file_path(media.playlist_tags)
        item.cover_path = str(Path(item.final_path).with_suffix(".jpg"))

        logger.debug(f"Parsed video item: {item}")

        return item
