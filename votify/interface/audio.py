import logging

from .base import SpotifyBaseInterface
from .enums import AudioQuality
from .exceptions import VotifyMediaFormatNotAvailableException
from .types import DecryptionKey, StreamInfo, StreamInfoAv

logger = logging.getLogger(__name__)


class SpotifyAudioInterface(SpotifyBaseInterface):
    def __init__(
        self,
        base: SpotifyBaseInterface,
        audio_quality_priority: list[AudioQuality] = [AudioQuality.AAC_MEDIUM],
    ):
        self.__dict__.update(base.__dict__)

        self.audio_quality_priority = audio_quality_priority

    async def _get_playback_info(
        self,
        media_id: str,
        media_type: str,
        flac: bool = False,
    ) -> dict:
        playback_info_response = await self.api.get_playback_info(
            media_id=media_id,
            media_type=media_type,
            file_formats=[
                "file_ids_mp4flac" if flac else "file_ids_mp4",
            ],
        )

        playback_info_key = next(iter(playback_info_response.get("media", {})), None)
        playback_info = playback_info_response["media"][playback_info_key]

        return playback_info["item"]

    async def get_stream_info(
        self,
        media_id: str,
        media_type: str,
        skip_pssh: bool,
    ) -> StreamInfoAv:
        for audio_quality in self.audio_quality_priority:
            stream_info = await self._get_stream_info(
                media_id=media_id,
                media_type=media_type,
                skip_pssh=skip_pssh,
                audio_quality=audio_quality,
            )
            if stream_info:
                return stream_info

        raise VotifyMediaFormatNotAvailableException(
            media_id=media_id,
        )

    async def _get_stream_info(
        self,
        media_id: str,
        media_type: str,
        audio_quality: AudioQuality,
        skip_pssh: bool,
    ) -> StreamInfoAv | None:
        playback_info = await self._get_playback_info(
            media_id=media_id,
            media_type=media_type,
            flac=audio_quality == AudioQuality.FLAC,
        )

        if (
            audio_quality.file_format not in {"mp4", "flac"}
            or audio_quality.premium
            and not self.api.premium_session
        ):
            return None

        file_id = self._parse_file_id(
            playback_info=playback_info,
            format_id=audio_quality.format_id,
            flac=audio_quality == AudioQuality.FLAC,
        )
        if not file_id:
            return None

        stream_url = await self._get_stream_url(audio_quality.format_id, file_id)
        pssh = None if skip_pssh else await self._get_pssh(file_id)

        stream_info = StreamInfoAv(
            audio_track=StreamInfo(
                stream_url=stream_url,
                widevine_pssh=pssh,
                file_format=audio_quality.file_format,
                actual_file_format=audio_quality.actual_file_format,
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
        flac: bool = False,
    ) -> str | None:
        manifest_key = "file_ids_mp4flac" if flac else "file_ids_mp4"
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
        format_id: str,
        file_id: str,
    ) -> str:
        streams_url_response = await self.api.get_audio_stream_urls(
            format_id,
            file_id,
        )
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
