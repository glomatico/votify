from __future__ import annotations

import subprocess
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from yt_dlp.downloader.fragment import FragmentFD
from yt_dlp.YoutubeDL import YoutubeDL

from .constants import COVER_SIZE_X_KEY_MAPPING_VIDEO
from .downloader import Downloader
from .enums import RemuxModeAudio, RemuxModeVideo, VideoFormat
from .models import StreamInfoVideo


class DownloaderVideo:
    def __init__(
        self,
        downloader: Downloader,
        video_format: VideoFormat = VideoFormat.MP4,
        remux_mode: RemuxModeVideo = RemuxModeVideo.FFMPEG,
    ):
        self.downloader = downloader
        self.video_format = video_format
        self.remux_mode = remux_mode
        self._adjust_remux_mode()

    def get_cover_url(self, metadata: dict) -> str | None:
        if not metadata.get("images"):
            return None
        return self._get_cover_url(metadata["images"])

    def _get_cover_url(self, images_dict: list[dict]) -> str:
        original_cover_url = images_dict[0]["url"]
        original_cover_id = original_cover_url.split("/")[-1]
        cover_key = COVER_SIZE_X_KEY_MAPPING_VIDEO[self.downloader.cover_size]
        cover_id = cover_key + original_cover_id[len(cover_key) :]
        cover_url = f"{original_cover_url.rpartition('/')[0]}/{cover_id}"
        return cover_url

    def _adjust_remux_mode(self):
        if self.video_format == VideoFormat.WEBM:
            self.remux_mode = RemuxModeVideo.FFMPEG

    def get_cover_path(self, final_path: Path) -> Path:
        return final_path.with_suffix(".jpg")

    def get_file_extension(
        self,
        file_type_video: str,
        file_type_audio: str,
    ) -> str:
        if file_type_video == file_type_audio:
            return "." + file_type_video
        else:
            return ".mp4"

    def get_encryption_info(
        self,
        encryption_infos: list[dict],
        key_system: str,
    ) -> tuple[int, str]:
        for index, encryption_info in enumerate(encryption_infos):
            if encryption_info["key_system"] == key_system:
                return index, encryption_info

    def get_stream_info(
        self,
        gid: str,
    ) -> StreamInfoVideo:
        stream_info = StreamInfoVideo()
        manifest = self.downloader.spotify_api.get_video_manifest(gid)
        base_url = manifest["base_urls"][0]
        initialization_template = manifest["initialization_template"]
        segment_template = manifest["segment_template"]
        end_time_millis = manifest["end_time_millis"]
        segment_length = manifest["contents"][0]["segment_length"]
        encryption_index = None
        if manifest["contents"][0].get("encryption_infos"):
            encryption_index, encryption_info = self.get_encryption_info(
                manifest["contents"][0]["encryption_infos"],
                "widevine",
            )
            stream_info.encryption_data_widevine = encryption_info["encryption_data"]
        video_profiles = list(
            filter(
                lambda x: x["mime_type"].startswith("video")
                and encryption_index
                in (x.get("encryption_indices", [encryption_index])),
                manifest["contents"][0]["profiles"],
            )
        )
        audio_profiles = list(
            filter(
                lambda x: x["mime_type"].startswith("audio")
                and encryption_index
                in (x.get("encryption_indices", [encryption_index])),
                manifest["contents"][0]["profiles"],
            )
        )
        if not video_profiles or not audio_profiles:
            return stream_info
        if self.video_format == VideoFormat.ASK:
            profile_video, profile_audio = (
                self.get_video_profile_from_user(
                    video_profiles,
                ),
                self.get_audio_profile_from_user(
                    audio_profiles,
                ),
            )
        else:
            profile_video, profile_audio = (
                self.get_best_profile_by_bitrate(
                    video_profiles,
                    f"video/{self.video_format.value}",
                ),
                self.get_best_profile_by_bitrate(
                    audio_profiles,
                    f"audio/{self.video_format.value}",
                ),
            )
        profile_id_video = profile_video["id"]
        file_type_video = profile_video["file_type"]
        profile_id_audio = profile_audio["id"]
        file_type_audio = profile_audio["file_type"]
        stream_info.segment_urls_video = self.get_segment_urls(
            base_url,
            initialization_template,
            segment_template,
            end_time_millis,
            segment_length,
            profile_id_video,
            file_type_video,
        )
        stream_info.segment_urls_audio = self.get_segment_urls(
            base_url,
            initialization_template,
            segment_template,
            end_time_millis,
            segment_length,
            profile_id_audio,
            file_type_audio,
        )
        stream_info.file_type_video = file_type_video
        stream_info.file_type_audio = file_type_audio
        return stream_info

    def get_best_profile_by_bitrate(
        self,
        profiles: list[dict],
        mime_type: str,
    ) -> str:
        profiles_filtered = list(
            filter(
                lambda x: x["mime_type"] == mime_type,
                profiles,
            )
        )
        bitrate_key = f"{mime_type.split('/')[0]}_bitrate"
        best_profile = max(profiles_filtered, key=lambda x: x[bitrate_key])
        return best_profile

    def get_video_profile_from_user(
        self,
        video_profiles: list[dict],
    ) -> str:
        choices = [
            Choice(
                name=" | ".join(
                    [
                        profile["video_codec"],
                        f"{profile['video_width']}x{profile['video_height']}",
                        str(profile["video_bitrate"]),
                    ]
                ),
                value=profile,
            )
            for profile in video_profiles
        ]
        selected = inquirer.select(
            message="Select which video codec to download: (Codec | Resolution | Bitrate)",
            choices=choices,
        ).execute()
        return selected

    def get_audio_profile_from_user(
        self,
        audio_profiles: list[dict],
    ) -> str:
        choices = [
            Choice(
                name=" | ".join(
                    [
                        profile["audio_codec"],
                        str(profile["audio_bitrate"]),
                    ]
                ),
                value=profile,
            )
            for profile in audio_profiles
        ]
        selected = inquirer.select(
            message="Select which audio codec to download: (Codec | Bitrate)",
            choices=choices,
        ).execute()
        return selected

    def get_segment_urls(
        self,
        base_url: str,
        initialization_template: str,
        segment_template: str,
        end_time_millis: int,
        segment_length: int,
        profile_id: int,
        file_type: str,
    ) -> list[str]:
        initialization_template_formatted = initialization_template.replace(
            "{{profile_id}}", str(profile_id)
        ).replace("{{file_type}}", file_type)
        segment_urls = []
        first_segment = base_url + initialization_template_formatted
        segment_urls.append(first_segment)
        for i in range(0, int(end_time_millis / 1000) + 5, segment_length):
            segment_template_url_formatted = (
                segment_template.replace("{{profile_id}}", str(profile_id))
                .replace("{{segment_timestamp}}", str(i))
                .replace("{{file_type}}", file_type)
            )
            segment_urls.append(base_url + segment_template_url_formatted)
        return segment_urls

    def download_segments(
        self,
        segment_urls: list[str],
        input_path: Path,
    ):
        input_path.parent.mkdir(parents=True, exist_ok=True)
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
                "noprogress": self.downloader.silence,
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

    def remux(
        self,
        decrypted_path_video: Path,
        decrypted_path_audio: Path,
        remuxed_path: Path,
        key_id: str | None = None,
        decryption_key: str | None = None,
        encrypted_path_video: Path | None = None,
        encrypted_path_audio: Path | None = None,
    ):
        if decryption_key:
            if remuxed_path.suffix == ".webm":
                self.decrypt_packager(
                    key_id,
                    decryption_key,
                    encrypted_path_video,
                    decrypted_path_video,
                )
                self.decrypt_packager(
                    key_id,
                    decryption_key,
                    encrypted_path_audio,
                    decrypted_path_audio,
                )
            else:
                self.decrypt_mp4decrypt(
                    decryption_key,
                    encrypted_path_video,
                    decrypted_path_video,
                )
                self.decrypt_mp4decrypt(
                    decryption_key,
                    encrypted_path_audio,
                    decrypted_path_audio,
                )
        if self.remux_mode == RemuxModeAudio.MP4BOX:
            self.remux_mp4box(
                decrypted_path_video,
                decrypted_path_audio,
                remuxed_path,
            )
        else:
            self.remux_ffmpeg(
                decrypted_path_video,
                decrypted_path_audio,
                remuxed_path,
            )

    def decrypt_packager(
        self,
        key_id: str,
        decryption_key: str,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        subprocess.run(
            [
                self.downloader.packager_path_full,
                "--quiet",
                f"stream=0,in={encrypted_path},output={decrypted_path}",
                "-enable_raw_key_decryption",
                "-keys",
                f"key_id={key_id}:key={decryption_key}",
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )

    def decrypt_mp4decrypt(
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

    def remux_ffmpeg(
        self,
        input_path_video: Path,
        input_path_audio: Path,
        output_path: Path,
    ):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                self.downloader.ffmpeg_path_full,
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
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )

    def remux_mp4box(
        self,
        decrypted_path_video: Path,
        decrypted_path_audio: Path,
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
                decrypted_path_video,
                "-add",
                decrypted_path_audio,
                "-new",
                remuxed_path,
            ],
            check=True,
            **self.downloader.subprocess_additional_args,
        )
