from __future__ import annotations

import subprocess
from pathlib import Path

from Crypto.Cipher import AES
from yt_dlp.downloader.http import HttpFD
from yt_dlp.YoutubeDL import YoutubeDL

from .constants import (
    AAC_AUDIO_QUALITIES,
    AUDIO_QUALITY_X_FORMAT_ID_MAPPING,
    COVER_SIZE_X_KEY_MAPPING_AUDIO,
    VORBIS_AUDIO_QUALITIES,
)
from .downloader import Downloader
from .enums import AudioQuality, DownloadMode, RemuxModeAudio
from .models import StreamInfoAudio


class DownloaderAudio:
    DEFAULT_EPISODE_DECRYPTION_KEY = (
        b"\xde\xad\xbe\xef\xde\xad\xbe\xef\xde\xad\xbe\xef\xde\xad\xbe\xef"  # lmao wtf
    )

    def __init__(
        self,
        downloader: Downloader,
        audio_quality: AudioQuality = AudioQuality.AAC_MEDIUM,
        download_mode: DownloadMode = DownloadMode.YTDLP,
        remux_mode: RemuxModeAudio = RemuxModeAudio.FFMPEG,
    ):
        self.downloader = downloader
        self.audio_quality = audio_quality
        self.download_mode = download_mode
        self.remux_mode = remux_mode

    def get_cover_url(self, metadata: dict) -> str | None:
        if not metadata.get("images"):
            return None
        return self._get_cover_url(metadata["images"])

    def _get_cover_url(self, images_dict: list[dict]) -> str:
        original_cover_url = images_dict[0]["url"]
        original_cover_id = original_cover_url.split("/")[-1]
        cover_key = COVER_SIZE_X_KEY_MAPPING_AUDIO[self.downloader.cover_size]
        cover_id = cover_key + original_cover_id[len(cover_key) :]
        cover_url = f"{original_cover_url.rpartition('/')[0]}/{cover_id}"
        return cover_url

    def get_file_extension(
        self,
    ) -> str:
        if self.audio_quality in AAC_AUDIO_QUALITIES:
            return ".m4a"
        else:
            return ".ogg"

    def get_audio_file(
        self,
        audio_files: list[dict],
    ) -> tuple[AudioQuality, dict] | tuple[None, None]:
        if self.audio_quality in AAC_AUDIO_QUALITIES:
            qualities = AAC_AUDIO_QUALITIES
        else:
            qualities = VORBIS_AUDIO_QUALITIES
        start_index = qualities.index(self.audio_quality)
        for quality in qualities[start_index:]:
            for audio_file in audio_files:
                if audio_file["format"] == AUDIO_QUALITY_X_FORMAT_ID_MAPPING[quality]:
                    return quality, audio_file
        return None, None

    def get_stream_info(
        self,
        gid_metadata: dict,
        media_type: str,
    ) -> StreamInfoAudio:
        stream_info = StreamInfoAudio()
        if media_type == "track":
            audio_files = gid_metadata.get("file")
        elif media_type == "episode":
            audio_files = gid_metadata.get("audio")
        else:
            raise RuntimeError()
        audio_files = audio_files or gid_metadata.get("alternative")
        if not audio_files:
            return stream_info
        if audio_files[0].get("gid"):
            audio_files = audio_files[0]["file"]
        quality, audio_file = self.get_audio_file(audio_files)
        if not audio_file:
            return stream_info
        file_id = audio_file["file_id"]
        stream_url = self.downloader.spotify_api.get_stream_urls(file_id)["cdnurl"][0]
        stream_info.stream_url = stream_url
        stream_info.file_id = file_id
        stream_info.quality = quality
        if self.audio_quality in AAC_AUDIO_QUALITIES:
            seek_table = self.downloader.spotify_api.get_seek_table(file_id)
            pssh = seek_table["pssh"]
            stream_info.widevine_pssh = pssh
        return stream_info

    def get_decryption_key(self, stream_info: StreamInfoAudio) -> str:
        if self.audio_quality in AAC_AUDIO_QUALITIES:
            _, decryption_key = self.downloader.get_widevine_decryption_key(
                stream_info.widevine_pssh,
                "audio",
            )
        else:
            decryption_key = self.downloader.get_playplay_decryption_key(
                stream_info.file_id
            )
        return decryption_key

    def download_stream_url(self, input_path: Path, stream_url: str):
        if self.download_mode == DownloadMode.YTDLP:
            self.download_stream_url_ytdlp(input_path, stream_url)
        elif self.download_mode == DownloadMode.ARIA2C:
            self.download_stream_url_aria2c(input_path, stream_url)

    def download_stream_url_ytdlp(self, input_path: Path, stream_url: str) -> None:
        input_path.parent.mkdir(parents=True, exist_ok=True)
        with YoutubeDL(
            {
                "quiet": True,
                "no_warnings": True,
                "noprogress": self.downloader.silence,
            }
        ) as ydl:
            http_downloader = HttpFD(ydl, ydl.params)
            http_downloader.download(
                str(input_path),
                {
                    "url": stream_url,
                },
            )

    def download_stream_url_aria2c(self, input_path: Path, stream_url: str) -> None:
        input_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                self.downloader.aria2c_path_full,
                "--no-conf",
                "--download-result=hide",
                "--console-log-level=error",
                "--summary-interval=0",
                "--file-allocation=none",
                stream_url,
                "--out",
                input_path,
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )
        print("\r", end="")

    def decrypt(
        self,
        decryption_key: bytes | str,
        encrypted_path: Path,
        decrypted_path: Path,
        remuxed_path: Path,
    ):
        if self.audio_quality in AAC_AUDIO_QUALITIES:
            if self.remux_mode == RemuxModeAudio.FFMPEG:
                self.decrypt_widevine_ffmpeg(
                    decryption_key,
                    encrypted_path,
                    decrypted_path,
                )
            else:
                self.decrypt_widevine_mp4decrypt(
                    decryption_key,
                    encrypted_path,
                    decrypted_path,
                )
                if self.remux_mode == RemuxModeAudio.MP4BOX:
                    self.remux_mp4box(decrypted_path, remuxed_path)
        else:
            self.decrypt_playplay(
                decryption_key,
                encrypted_path,
                decrypted_path,
            )

    def decrypt_playplay(
        self,
        decryption_key: bytes,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        cipher = AES.new(
            decryption_key,
            AES.MODE_CTR,
            nonce=bytes.fromhex("72e067fbddcbcf77"),
            initial_value=bytes.fromhex("ebe8bc643f630d93"),
        )

        with encrypted_path.open("rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        with decrypted_path.open("wb") as decrypted_file:
            decrypted_data = cipher.decrypt(encrypted_data)

            offset = decrypted_data.find(b"OggS")
            if offset == -1:
                msg = "Unable to find ogg header"
                raise ValueError(msg)

            decrypted_file.write(decrypted_data[offset:])

    def decrypt_widevine_ffmpeg(
        self,
        decryption_key: str,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        subprocess.run(
            [
                self.downloader.ffmpeg_path_full,
                "-loglevel",
                "error",
                "-y",
                "-decryption_key",
                decryption_key,
                "-i",
                encrypted_path,
                "-c",
                "copy",
                decrypted_path,
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )

    def decrypt_widevine_mp4decrypt(
        self,
        decryption_key: str,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        subprocess.run(
            [
                self.downloader.mp4decrypt_path_full,
                "--key",
                f"1:{decryption_key}",
                encrypted_path,
                decrypted_path,
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )

    def remux_mp4box(
        self,
        decrypted_path: Path,
        remuxed_path: Path,
    ):
        subprocess.run(
            [
                self.downloader.mp4box_path_full,
                "-quiet",
                "-itags",
                "artist=placeholder",
                "-keep-utc",
                "-add",
                decrypted_path,
                "-new",
                remuxed_path,
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )
