from __future__ import annotations

import subprocess
from pathlib import Path

import requests
import tqdm
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .downloader import Downloader
from .enums import VideoFormat
from .models import StreamInfoVideo
from .utils import check_response


class DownloaderVideo:
    def __init__(
        self,
        downloader: Downloader,
    ):
        self.downloader = downloader

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
            profile
            for profile in manifest["contents"][0]["profiles"]
            if profile["mime_type"].startswith("video")
            and encryption_index
            in (profile.get("encryption_indices", [encryption_index]))
        )
        audio_profiles = list(
            profile
            for profile in manifest["contents"][0]["profiles"]
            if profile["mime_type"].startswith("audio")
            and encryption_index
            in (profile.get("encryption_indices", [encryption_index]))
        )
        if not video_profiles or not audio_profiles:
            return stream_info
        if self.downloader.video_format == VideoFormat.ASK:
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
                    manifest["contents"][0]["profiles"],
                    f"video/{self.downloader.video_format.value}",
                    encryption_info,
                ),
                self.get_best_profile_by_bitrate(
                    manifest["contents"][0]["profiles"],
                    f"audio/{self.downloader.video_format.value}",
                    encryption_index,
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
        bitrate_key = f"{mime_type.split('/')[0]}_bitrate"
        best_profile = max(profiles, key=lambda x: x[bitrate_key])
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
        for i in range(0, int(end_time_millis / 1000), segment_length):
            segment_template_url_formatted = (
                segment_template.replace("{{profile_id}}", str(profile_id))
                .replace("{{segment_timestamp}}", str(i))
                .replace("{{file_type}}", file_type)
            )
            segment_urls.append(base_url + segment_template_url_formatted)
        return segment_urls

    def download_segment(
        self,
        segment_url: str,
        input_path: Path,
    ):
        response = requests.get(segment_url, stream=True)
        check_response(response)
        chunk_size = 1024
        input_path.parent.mkdir(parents=True, exist_ok=True)
        with input_path.open("ab") as file:
            for chunk in response.iter_content(chunk_size):
                if chunk:
                    file.write(chunk)

    def download_segments(
        self,
        segment_urls: list[str],
        input_path: Path,
    ):
        for segment_url in tqdm.tqdm(segment_urls, leave=False):
            self.download_segment(segment_url, input_path)

    def get_file_extension(
        self,
        file_type_video: str,
        file_type_audio: str,
    ) -> str:
        if file_type_video == file_type_audio:
            return "." + file_type_video
        else:
            return ".mp4"

    def remux(
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
