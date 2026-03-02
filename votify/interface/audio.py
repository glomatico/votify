import logging

from .base import SpotifyBaseInterface
from .enums import AudioQuality
from .exceptions import VotifyMediaAudioQualityNotAvailableException
from .types import DecryptionKey, StreamInfo, StreamInfoAv

logger = logging.getLogger(__name__)


class SpotifyAudioInterface(SpotifyBaseInterface):
    def __init__(
        self,
        base: SpotifyBaseInterface,
        audio_quality: AudioQuality = AudioQuality.AAC_MEDIUM,
    ):
        self.__dict__.update(base.__dict__)

        self.audio_quality = audio_quality

    async def get_stream_info(
        self,
        playback_info: dict,
        skip_pssh: bool,
    ) -> StreamInfoAv | None:
        if (
            not self.audio_quality.mp4
            or self.audio_quality.premium
            and not self.api.premium_session
        ):
            raise VotifyMediaAudioQualityNotAvailableException(
                media_id=playback_info["metadata"]["uri"].split(":")[-1],
            )

        file_id = None
        audio_quality = self.audio_quality
        while True:
            file_id = self._parse_file_id(playback_info, audio_quality.format_id)
            if not file_id:
                assert (
                    audio_quality.previous_quality
                ), "No more audio qualities to fallback to"
                audio_quality = audio_quality.previous_quality
            else:
                break

        stream_url = await self._get_stream_url(file_id)
        pssh = None if skip_pssh else await self._get_pssh(file_id)

        stream_info = StreamInfoAv(
            audio_track=StreamInfo(
                stream_url=stream_url,
                widevine_pssh=pssh,
                file_format="flac" if audio_quality == AudioQuality.FLAC else "mp4",
            ),
        )

        logger.debug(f"Parsed stream info: {stream_info}")

        return stream_info

    async def get_widevine_decryption_key(self, pssh: str) -> DecryptionKey:
        return await self._get_widevine_decryption_key(pssh, "audio")

    def _parse_file_id(
        self,
        playback_info: dict,
        format_id: str,
    ) -> str | None:
        manifest_key = (
            "file_ids_mp4flac"
            if self.audio_quality == AudioQuality.FLAC
            else "file_ids_mp4"
        )
        file_id = next(
            (
                file_info["file_id"]
                for file_info in playback_info.get("manifest", {}).get(manifest_key, [])
                if file_info["format"] == format_id
            ),
            None,
        )
        return file_id

    async def _get_stream_url(
        self,
        file_id: str,
    ) -> str:
        streams_url_response = await self.api.get_audio_stream_urls(file_id)
        stream_url = streams_url_response["cdnurl"][0]

        logger.debug(f"Received stream URL: {stream_url}")

        return stream_url

    async def _get_pssh(
        self,
        file_id: str,
    ) -> str:
        seek_table_response = await self.api.get_seek_table(file_id)
        pssh = seek_table_response.get("pssh", seek_table_response.get("widevine_pssh"))

        logger.debug(f"Received PSSH: {pssh}")

        return pssh
