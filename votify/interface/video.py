import logging

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .base import SpotifyBaseInterface
from .constants import COVER_SIZE_ID_MAP_VIDEO
from .enums import VideoFormat, VideoResolution
from .types import DecryptionKey, StreamInfo, StreamInfoAv

logger = logging.getLogger(__name__)


class SpotifyVideoInterface(SpotifyBaseInterface):
    def __init__(
        self,
        base: SpotifyBaseInterface,
        video_format: VideoFormat = VideoFormat.MP4,
        resolution: VideoResolution = VideoResolution.R1080P,
    ):
        self.__dict__.update(base.__dict__)
        self.video_format = video_format
        self.resolution = resolution

    async def _get_playback_info(
        self,
        media_id: str,
        media_type: str,
    ) -> dict:
        playback_info_response = await self.api.get_playback_info(
            media_id=media_id,
            media_type=media_type,
            file_formats=["manifest_ids_video"],
        )

        playback_info_key = next(iter(playback_info_response.get("media", {})), None)
        playback_info = playback_info_response["media"][playback_info_key]

        if playback_info.get("video_version_uri"):
            playback_info = playback_info_response["media"][
                playback_info["video_version_uri"]
            ]

        return playback_info["item"]

    def _get_encryption_info(
        self,
        encryption_infos: list[dict],
        key_system: str,
    ) -> tuple[int, dict] | None:
        for index, encryption_info in enumerate(encryption_infos):
            if encryption_info["key_system"] == key_system:
                return index, encryption_info
        return None

    def _filter_profiles_by_type(
        self,
        profiles: list[dict],
        mime_type_prefix: str,
        encryption_index: int,
    ) -> list[dict]:
        return list(
            filter(
                lambda x: x["mime_type"].startswith(mime_type_prefix)
                and encryption_index
                in (x.get("encryption_indices", [encryption_index])),
                profiles,
            )
        )

    def _get_best_profile(
        self,
        profiles: list[dict],
        mime_type: str,
    ) -> dict:
        profiles_filtered = list(
            filter(lambda x: x["mime_type"] == mime_type, profiles)
        )
        bitrate_key = f"{mime_type.split('/')[0]}_bitrate"
        return max(profiles_filtered, key=lambda x: x.get(bitrate_key, 0))

    def _get_best_video_profile_by_resolution(
        self,
        profiles: list[dict],
        mime_type: str,
    ) -> dict:
        profiles_filtered = list(
            filter(lambda x: x["mime_type"] == mime_type, profiles)
        )

        available_resolutions = sorted(
            set(p.get("video_height") for p in profiles_filtered),
            reverse=True,
        )

        for res in available_resolutions:
            if res <= int(self.resolution):
                return max(
                    (p for p in profiles_filtered if p.get("video_height") == res),
                    key=lambda x: x.get("video_bitrate", 0),
                )

        return min(profiles_filtered, key=lambda x: x.get("video_height", 0))

    async def _select_profiles_interactive(
        self,
        video_profiles: list[dict],
        audio_profiles: list[dict],
    ) -> tuple[dict, dict]:
        profile_video = await self._get_video_profile_from_user(video_profiles)
        profile_audio = await self._get_audio_profile_from_user(audio_profiles)
        return profile_video, profile_audio

    async def _get_video_profile_from_user(
        self,
        video_profiles: list[dict],
    ) -> dict:
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
        return await inquirer.select(
            message="Select which video codec to download: (Codec | Resolution | Bitrate)",
            choices=choices,
        ).execute_async()

    async def _get_audio_profile_from_user(
        self,
        audio_profiles: list[dict],
    ) -> dict:
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
        return await inquirer.select(
            message="Select which audio codec to download: (Codec | Bitrate)",
            choices=choices,
        ).execute_async()

    def _generate_segment_urls(
        self,
        base_url: str,
        initialization_template: str,
        segment_template: str,
        end_time_millis: int,
        segment_length: int,
        profile_id: int,
        file_type: str,
    ) -> list[str]:
        initialization_url = initialization_template.replace(
            "{{profile_id}}", str(profile_id)
        ).replace("{{file_type}}", file_type)
        segment_urls = [base_url + initialization_url]

        for timestamp in range(0, int(end_time_millis / 1000) + 5, segment_length):
            segment_url = (
                segment_template.replace("{{profile_id}}", str(profile_id))
                .replace("{{segment_timestamp}}", str(timestamp))
                .replace("{{file_type}}", file_type)
            )
            segment_urls.append(base_url + segment_url)

        return segment_urls

    def _parse_file_id(
        self,
        playback_info: dict,
    ) -> str:
        manifest_ids_video = playback_info.get("manifest", {}).get("manifest_ids_video")
        return manifest_ids_video[0]["file_id"]

    async def get_stream_info(
        self,
        media_id: str,
        media_type: str,
    ) -> StreamInfoAv | None:
        playback_info = await self._get_playback_info(
            media_id=media_id,
            media_type=media_type,
        )

        file_id = self._parse_file_id(playback_info)

        manifest = await self.api.get_video_manifest(file_id)
        content = manifest["contents"][0]

        base_url = manifest["base_urls"][0]
        initialization_template = manifest["initialization_template"]
        segment_template = manifest["segment_template"]
        end_time_millis = content["end_time_millis"]
        segment_length = content["segment_length"]

        encryption_result = None
        widevine_pssh = None
        if content.get("encryption_infos"):
            encryption_result = self._get_encryption_info(
                content["encryption_infos"], "widevine"
            )
            if encryption_result:
                encryption_index, encryption_info = encryption_result
                widevine_pssh = encryption_info.get("encryption_data")
            else:
                encryption_index = None
        else:
            encryption_index = None

        video_profiles = self._filter_profiles_by_type(
            content["profiles"],
            "video",
            encryption_index,
        )
        audio_profiles = self._filter_profiles_by_type(
            content["profiles"],
            "audio",
            encryption_index,
        )

        if self.video_format == VideoFormat.ASK:
            profile_video, profile_audio = await self._select_profiles_interactive(
                video_profiles,
                audio_profiles,
            )
        else:
            profile_video = self._get_best_video_profile_by_resolution(
                video_profiles,
                f"video/{self.video_format.value}",
            )
            profile_audio = self._get_best_profile(
                audio_profiles,
                f"audio/{self.video_format.value}",
            )

        video_urls = self._generate_segment_urls(
            base_url,
            initialization_template,
            segment_template,
            end_time_millis,
            segment_length,
            profile_video["id"],
            profile_video["file_type"],
        )

        audio_urls = self._generate_segment_urls(
            base_url,
            initialization_template,
            segment_template,
            end_time_millis,
            segment_length,
            profile_audio["id"],
            profile_audio["file_type"],
        )

        is_webm = lambda profile: profile["mime_type"].endswith("webm")

        stream_info = StreamInfoAv(
            audio_track=StreamInfo(
                stream_url=audio_urls,
                widevine_pssh=widevine_pssh,
                file_format="webm" if is_webm(profile_audio) else "mp4",
            ),
            video_track=StreamInfo(
                stream_url=video_urls,
                widevine_pssh=widevine_pssh,
                file_format="webm" if is_webm(profile_video) else "mp4",
            ),
        )

        logger.debug(f"Generated stream info: {stream_info}")

        return stream_info

    def parse_cover_url(self, base_cover_url: str) -> str:
        cover_url = self._transform_cover_url(base_cover_url, COVER_SIZE_ID_MAP_VIDEO)

        logger.debug(f"Parsed episode cover URL: {cover_url}")

        return cover_url

    async def get_widevine_decryption_key(self, pssh: str) -> DecryptionKey:
        return await self._get_widevine_decryption_key(pssh, "video")
