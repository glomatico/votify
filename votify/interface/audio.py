import asyncio
import logging

from pywidevine.license_protocol_pb2 import WidevinePsshData

from ..api.enums import SessionType
from ..api.proto.audio_files_extension_pb2 import AudioFilesExtensionResponse
from ..api.proto.extendedmetadata_pb2 import (
    BatchedEntityRequest,
    BatchedEntityRequestHeader,
    EntityRequest,
    ExtensionKind,
    ExtensionQuery,
)
from ..api.proto.playplay_pb2 import ContentType, Interactivity, PlayPlayLicenseRequest
from .base import SpotifyBaseInterface
from .enums import AudioQuality
from .exceptions import (
    VotifyMediaFormatNotAvailableException,
    VotifyMediaFormatNotAvailableForSessionTypeException,
    VotifyNoKeyEmuException,
)
from .types import DecryptionKey, StreamInfo, StreamInfoAv

try:
    from unplayplay.consts import EMULATOR_SIZES, PLAYPLAY_TOKEN
except ImportError:
    EMULATOR_SIZES = None
    PLAYPLAY_TOKEN = None

logger = logging.getLogger(__name__)


class SpotifyAudioInterface(SpotifyBaseInterface):
    def __init__(
        self,
        base: SpotifyBaseInterface,
        audio_quality_priority: list[AudioQuality] = [AudioQuality.VORBIS_MEDIUM],
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
        session_type_skipped = False
        for audio_quality in self.audio_quality_priority:
            stream_info = None

            if audio_quality.mp4:
                if self.api.session_type not in {
                    SessionType.LIBRESPOT,
                    SessionType.WEB,
                }:
                    session_type_skipped = True
                    continue
                session_type_skipped = False
                stream_info = await self._get_stream_info_web(
                    media_id=media_id,
                    media_type=media_type,
                    skip_pssh=skip_pssh,
                    audio_quality=audio_quality,
                )

            elif audio_quality.ogg:
                if self.api.session_type == SessionType.LIBRESPOT:
                    session_type_skipped = False
                    stream_info = await self._get_stream_info_librespot(
                        media_id=media_id,
                        media_type=media_type,
                        audio_quality=audio_quality,
                    )
                elif self.api.session_type == SessionType.DESKTOP:
                    session_type_skipped = False
                    stream_info = await self._get_stream_info_desktop(
                        media_id=media_id,
                        media_type=media_type,
                        audio_quality=audio_quality,
                    )
                else:
                    session_type_skipped = True
                    continue

            elif audio_quality.flac:
                if self.api.session_type == SessionType.DESKTOP:
                    session_type_skipped = False
                    stream_info = await self._get_stream_info_desktop(
                        media_id=media_id,
                        media_type=media_type,
                        audio_quality=audio_quality,
                    )
                else:
                    session_type_skipped = True
                    continue

            if stream_info:
                return stream_info

        if session_type_skipped:
            raise VotifyMediaFormatNotAvailableForSessionTypeException(
                media_id=media_id,
                session_type=self.api.session_type,
            )

        raise VotifyMediaFormatNotAvailableException(
            media_id=media_id,
        )

    async def _get_stream_info_web(
        self,
        media_id: str,
        media_type: str,
        audio_quality: AudioQuality,
        skip_pssh: bool,
    ) -> StreamInfoAv | None:
        playback_info = await self._get_playback_info(
            media_id=media_id,
            media_type=media_type,
            flac=audio_quality in {AudioQuality.FLAC_MP4, AudioQuality.FLAC_MP4_24},
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
            flac=audio_quality in {AudioQuality.FLAC_MP4, AudioQuality.FLAC_MP4_24},
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

        logger.debug(f"Parsed stream info from web method: {stream_info}")

        return stream_info

    async def _get_stream_info_librespot(
        self,
        media_id: str,
        media_type: str,
        audio_quality: AudioQuality,
    ) -> StreamInfoAv | None:
        if not self.api.librespot:
            return None

        def media_id_wrapper(
            media_id: str,
            media_type: str,
        ):
            class SpotifyUri:
                def to_spotify_uri(self):
                    return f"spotify:{media_type}:{media_id}"

            return SpotifyUri()

        if media_type == "track":
            metadata = await asyncio.to_thread(
                self.api.librespot.session.api().get_metadata_4_track,
                media_id_wrapper(media_id, media_type),
            )
        elif media_type == "episode":
            metadata = await asyncio.to_thread(
                self.api.librespot.session.api().get_metadata_4_episode,
                media_id_wrapper(media_id, media_type),
            )
        else:
            return None

        audio_quality_int = int(audio_quality.format_id)
        file_id = next(
            (
                file.file_id
                for file in metadata.file
                if file.format == audio_quality_int
            ),
            None,
        )
        if not file_id:
            return None
        stream_url = await self._get_stream_url(audio_quality.format_id, file_id.hex())

        stream_info = StreamInfoAv(
            audio_track=StreamInfo(
                stream_url=stream_url,
                widevine_pssh=None,
                file_format=audio_quality.file_format,
                actual_file_format=audio_quality.actual_file_format,
                file_id=file_id,
            ),
        )

        logger.debug(f"Parsed stream info from librespot: {stream_info}")

        return stream_info

    async def _get_stream_info_desktop(
        self,
        media_id: str,
        media_type: str,
        audio_quality: AudioQuality,
    ) -> StreamInfoAv | None:
        extended_metadata_request = BatchedEntityRequest(
            header=BatchedEntityRequestHeader(),
            entity_request=[
                EntityRequest(
                    entity_uri=f"spotify:{media_type}:{media_id}",
                    query=[
                        ExtensionQuery(extension_kind=ExtensionKind.TRACK_V4),
                        ExtensionQuery(extension_kind=ExtensionKind.AUDIO_FILES),
                    ],
                ),
            ],
        )
        extended_metadata = await self.api.get_extended_metadata(
            extended_metadata_request
        )
        audio_files_data_array = next(
            (
                ext
                for ext in extended_metadata.extended_metadata
                if ext.extension_kind == ExtensionKind.AUDIO_FILES
            ),
            None,
        )
        if not audio_files_data_array:
            return

        audio_files_data_bytes = audio_files_data_array.extension_data[
            0
        ].extension_data.value
        audio_files = AudioFilesExtensionResponse()
        audio_files.ParseFromString(audio_files_data_bytes)

        audio_file_info = next(
            (
                (extended_audio_file, extended_audio_file.average_bitrate)
                for extended_audio_file in audio_files.files
                if extended_audio_file.file.format == int(audio_quality.format_id)
            ),
            None,
        )
        if not audio_file_info:
            return

        stream_url = await self._get_stream_url(
            audio_quality.format_id,
            audio_file_info[0].file.file_id.hex(),
        )

        stream_info = StreamInfoAv(
            audio_track=StreamInfo(
                stream_url=stream_url,
                widevine_pssh=None,
                file_id=audio_file_info[0].file.file_id,
                file_format=audio_quality.file_format,
                actual_file_format=audio_quality.actual_file_format,
            ),
        )

        logger.debug(f"Parsed stream info from desktop method: {stream_info}")

        return stream_info

    async def get_widevine_decryption_key(self, pssh: str) -> DecryptionKey:
        return await self._get_widevine_decryption_key(pssh, "audio")

    async def get_librespot_decryption_key(
        self,
        media_id: str,
        file_id: bytes,
    ) -> DecryptionKey:
        if not self.api.librespot:
            raise Exception("Librespot is not initialized")

        decryption_key = await asyncio.to_thread(
            self.api.librespot.session.audio_key().get_audio_key,
            bytes.fromhex(self.api.media_id_to_gid(media_id)),
            file_id,
        )

        decryption_key_obj = DecryptionKey(
            decryption_key=decryption_key,
        )

        logger.debug(f"Received decryption key from librespot: {decryption_key.hex()}")

        return decryption_key_obj

    async def _get_desktop_decryption_key(self, file_id: bytes) -> DecryptionKey:
        if not self.key_emu:
            raise VotifyNoKeyEmuException()

        request = PlayPlayLicenseRequest(
            version=5,
            token=PLAYPLAY_TOKEN.VALUE,
            interactivity=Interactivity.INTERACTIVE,
            content_type=ContentType.AUDIO_TRACK,
        )
        license = await self.api.get_playplay_license(
            file_id=file_id.hex(),
            request=request,
        )
        decryption_key = self.key_emu.get_aes_key(
            obfuscated_key=license.obfuscated_key,
            content_id=file_id[: EMULATOR_SIZES.CONTENT_ID],
        )

        logger.debug(
            f"Received decryption key from desktop method: {decryption_key.hex()}"
        )

        return DecryptionKey(
            decryption_key=decryption_key,
        )

    async def get_decryption_key(
        self,
        stream_info: StreamInfoAv,
        media_id: str,
    ):
        if (
            self.api.session_type in {SessionType.LIBRESPOT, SessionType.WEB}
            and stream_info.audio_track.widevine_pssh
        ):
            return await self.get_widevine_decryption_key(
                stream_info.audio_track.widevine_pssh
            )
        elif (
            stream_info.audio_track.file_id
            and self.api.session_type == SessionType.LIBRESPOT
        ):
            return await self.get_librespot_decryption_key(
                media_id=media_id,
                file_id=stream_info.audio_track.file_id,
            )
        elif (
            stream_info.audio_track.file_id
            and self.api.session_type == SessionType.DESKTOP
        ):
            return await self._get_desktop_decryption_key(
                file_id=stream_info.audio_track.file_id,
            )
        else:
            raise Exception("No method available to get decryption key")

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
        pssh_obj = WidevinePsshData()
        pssh_obj.algorithm = WidevinePsshData.AESCTR
        pssh_obj.key_ids.append(bytes.fromhex(file_id[:32]))
        pssh_obj.provider = "spotify"
        pssh_obj.content_id = bytes.fromhex(file_id)
        pssh_obj.protection_scheme = 1667591779

        return pssh_obj.SerializeToString()
