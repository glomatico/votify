import asyncio
import logging
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util import Counter
from yt_dlp import YoutubeDL
from yt_dlp.downloader.http import HttpFD

from ..interface.types import SpotifyMedia
from .base import SpotifyBaseDownloader
from .enums import AudioDownloadMode, AudioRemuxMode
from .types import DownloadItem

logger = logging.getLogger(__name__)


class SpotifyAudioDownloader(SpotifyBaseDownloader):
    def __init__(
        self,
        base: SpotifyBaseDownloader,
        download_mode: AudioDownloadMode = AudioDownloadMode.YTDLP,
        remux_mode: AudioRemuxMode = AudioRemuxMode.FFMPEG,
    ) -> None:
        self.__dict__.update(base.__dict__)

        self.download_mode = download_mode
        self.remux_mode = remux_mode

    async def download_stream(
        self,
        output_path: str,
        stream_url: str,
    ) -> None:
        logger.debug(f"Downloading audio stream from '{stream_url}' to '{output_path}'")

        if self.download_mode == AudioDownloadMode.YTDLP:
            await asyncio.to_thread(self._download_with_ytdlp, stream_url, output_path)
        elif self.download_mode == AudioDownloadMode.ARIA2C:
            await self._download_with_aria2c(stream_url, output_path)
        else:
            await self._download_with_curl(stream_url, output_path)

    def _download_with_ytdlp(self, stream_url: str, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with YoutubeDL(
            {
                "quiet": True,
                "no_warnings": True,
                "noprogress": self.silent,
            }
        ) as ydl:
            http_downloader = HttpFD(ydl, ydl.params)
            http_downloader.download(
                output_path,
                {
                    "url": stream_url,
                },
            )

    async def _download_with_aria2c(self, stream_url: str, output_path: str) -> None:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        await self.run_async_command(
            self.aria2c_full_path,
            "--no-conf",
            "--download-result=hide",
            "--console-log-level=error",
            "--summary-interval=0",
            "--file-allocation=none",
            stream_url,
            "--dir",
            output_path_obj.parent,
            "--out",
            output_path_obj.name,
            silent=self.silent,
        )

        print("\r", end="")

    async def _download_with_curl(self, stream_url: str, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        await self.run_async_command(
            self.curl_full_path,
            "-sSL",
            "-o",
            output_path,
            stream_url,
            silent=self.silent,
        )

        print("\r", end="")

    async def stage(
        self,
        encrypted_path: str,
        decrypted_path: str,
        staged_path: str,
        decryption_key: bytes | str,
    ) -> None:
        logger.debug(f"Staging audio: {staged_path}")
        decryption_key_hex = (
            decryption_key.hex()
            if isinstance(decryption_key, bytes)
            else decryption_key
        )

        if encrypted_path.lower().endswith(".ogg") or encrypted_path.lower().endswith(
            ".flac"
        ):
            await asyncio.to_thread(
                self._decrypt_playplay,
                decryption_key,
                encrypted_path,
                staged_path,
            )
        elif self.remux_mode == AudioRemuxMode.FFMPEG or staged_path.lower().endswith(
            ".flac"
        ):
            await self._ffmpeg_remux(
                encrypted_path,
                staged_path,
                decryption_key_hex,
            )
        else:
            await self._decrypt_mp4decrypt(
                encrypted_path,
                decrypted_path,
                decryption_key_hex,
            )
            if self.remux_mode == AudioRemuxMode.MP4BOX:
                await self._mp4box_remux(
                    decrypted_path,
                    staged_path,
                )

    def _decrypt_playplay(
        self,
        decryption_key: bytes,
        input_path: str,
        output_path: str,
    ):
        cipher = AES.new(
            key=decryption_key,
            mode=AES.MODE_CTR,
            counter=Counter.new(
                128,
                initial_value=int.from_bytes(
                    bytes.fromhex("72e067fbddcbcf77ebe8bc643f630d93"), "big"
                ),
            ),
        )

        with open(input_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        with open(output_path, "wb") as decrypted_file:
            decrypted_file.write(decrypted_data[167:])

    async def _decrypt_mp4decrypt(
        self,
        input_path: str,
        output_path: str,
        decryption_key: str,
    ) -> None:
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
        input_path: str,
        output_path: str,
        decryption_key: str,
    ) -> None:
        await self.run_async_command(
            self.ffmpeg_full_path,
            "-loglevel",
            "error",
            "-hide_banner",
            "-y",
            "-decryption_key",
            decryption_key,
            "-i",
            input_path,
            "-c",
            "copy",
            output_path,
            silent=self.silent,
        )

    async def _mp4box_remux(
        self,
        input_path: str,
        output_path: str,
    ) -> None:
        await self.run_async_command(
            self.mp4box_full_path,
            "-quiet",
            "-itags",
            "artist=placeholder",
            "-keep-utc",
            "-add",
            input_path,
            "-new",
            output_path,
            silent=self.silent,
        )

    async def download(self, item: DownloadItem) -> None:
        encrypted_path = self.get_temp_path(
            item.media.media_id,
            item.uuid_,
            "encrypted",
            "." + item.media.stream_info.audio_track.file_format,
        )
        decrypted_path = self.get_temp_path(
            item.media.media_id,
            item.uuid_,
            "decrypted",
            "." + item.media.stream_info.audio_track.file_format,
        )
        await self.download_stream(
            encrypted_path,
            item.media.stream_info.audio_track.stream_url,
        )
        await self.stage(
            encrypted_path,
            decrypted_path,
            item.staged_path,
            item.media.decryption_key.decryption_key,
        )
        await self.apply_tags(
            item.staged_path,
            item.media.tags,
            item.media.cover_url,
        )

    def parse_item(self, media: SpotifyMedia) -> DownloadItem:
        item = DownloadItem(media=media)

        if not media.stream_info:
            actual_file_format = self.interface.song.audio_quality_priority[
                0
            ].actual_file_format
        else:
            actual_file_format = media.stream_info.audio_track.actual_file_format

        item.staged_path = self.get_temp_path(
            media.media_id,
            item.uuid_,
            "staged",
            "." + actual_file_format,
        )
        item.final_path = self.get_final_path(
            media.tags,
            "." + actual_file_format,
            media.playlist_tags,
        )
        if media.playlist_tags:
            item.playlist_file_path = self.get_playlist_file_path(media.playlist_tags)
        item.synced_lyrics_path = str(Path(item.final_path).with_suffix(".lrc"))
        item.cover_path = str(Path(item.final_path).parent / "Cover.jpg")

        logger.debug(f"Parsed audio item: {item}")

        return item
