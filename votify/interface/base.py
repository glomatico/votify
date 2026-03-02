import datetime
import logging

from async_lru import alru_cache
from pywidevine import PSSH, Cdm, Device

from ..api import SpotifyApi
from .constants import URL_INFO_RE
from .enums import CoverSize, MediaRating
from .exceptions import VotifyUrlParseException
from .types import DecryptionKey, PlaylistTags, SpotifyUrlInfo

logger = logging.getLogger(__name__)


class SpotifyBaseInterface:
    def __init__(
        self,
        api: SpotifyApi,
        cover_size: CoverSize = CoverSize.EXTRA_LARGE,
        prefer_video: bool = False,
        no_drm: bool = False,
        skip_stream_info: bool = False,
        wvd_path: str | None = "./device.wvd",
        disallowed_media_types: list[str] | None = None,
    ) -> None:
        self.api = api
        self.cover_size = cover_size
        self.prefer_video = prefer_video
        self.no_drm = no_drm
        self.skip_stream_info = skip_stream_info
        self.wvd_path = wvd_path
        self.disallowed_media_types = disallowed_media_types or []

        self._initialize_cdm()

    @alru_cache()
    async def get_album_data_cached(self, album_id: str) -> tuple[dict, list[dict]]:
        album_response = await self.api.get_album(album_id)
        album_data = album_response["data"]["albumUnion"]
        album_items = album_data.get("tracksV2", {}).get("items", [])
        while len(album_items) < album_data.get("tracksV2", {}).get("totalCount", 0):
            album_tracks_response = await self.api.get_album(
                album_id,
                offset=len(album_items),
            )
            album_items.extend(
                album_tracks_response["data"]["albumUnion"]["tracksV2"]["items"]
            )
        return album_data, album_items

    @alru_cache()
    async def get_show_data_cached(self, show_id: str) -> tuple[dict, list[dict]]:
        show_response = await self.api.get_show(show_id)
        show_data = show_response["data"]["podcastUnionV2"]
        show_items = show_data.get("episodesV2", {}).get("items", [])
        while len(show_items) < show_data.get("episodesV2", {}).get("totalCount", 0):
            show_episodes_response = await self.api.get_show(
                show_id,
                offset=len(show_items),
            )
            show_items.extend(
                show_episodes_response["data"]["podcastUnionV2"]["episodesV2"]["items"]
            )
        return show_data, show_items

    def _initialize_cdm(self) -> None:
        if self.wvd_path and not self.no_drm:
            self.cdm = Cdm.from_device(Device.load(self.wvd_path))
            self.cdm.MAX_NUM_OF_SESSIONS = float("inf")
        else:
            self.cdm = None
            self.no_drm = True

    def parse_url_info(self, url: str) -> SpotifyUrlInfo:
        match = URL_INFO_RE.match(url)
        if not match:
            raise VotifyUrlParseException(url)

        logger.debug(f"Parsed URL info: {match.groupdict()}")

        return SpotifyUrlInfo(**match.groupdict())

    async def _get_widevine_decryption_key(
        self,
        pssh: str,
        media_type: str,
    ) -> DecryptionKey:
        try:
            cdm_session = self.cdm.open()
            pssh = PSSH(pssh)
            challenge = self.cdm.get_license_challenge(cdm_session, pssh)
            license = await self.api.get_widevine_license(challenge, media_type)
            self.cdm.parse_license(cdm_session, license)
            keys = next(
                i for i in self.cdm.get_keys(cdm_session) if i.type == "CONTENT"
            )
            decryption_key = keys.key.hex()
            key_id = keys.kid.hex
        finally:
            self.cdm.close(cdm_session)

        logger.debug(f"Received decryption key: {key_id}:{decryption_key}")

        return DecryptionKey(key_id=key_id, decryption_key=decryption_key)

    def is_video(self, playback_info: dict) -> bool:
        return bool(playback_info["manifest"].get("manifest_ids_video"))

    async def get_playback_info(
        self,
        media_id: str,
        media_type: str,
        flac: bool = False,
    ) -> dict | None:
        playback_info_response = await self.api.get_playback_info(
            media_id=media_id,
            media_type=media_type,
            file_formats=[
                "manifest_ids_video",
                "file_ids_mp4flac" if flac else "file_ids_mp4",
            ],
        )

        playback_info_key = next(iter(playback_info_response.get("media", {})), None)
        if not playback_info_key:
            return None
        playback_info = playback_info_response["media"][playback_info_key]

        if self.prefer_video and playback_info.get("video_version_uri"):
            playback_info = playback_info_response["media"][
                playback_info["video_version_uri"]
            ]

        return playback_info["item"]

    def _transform_cover_url(self, url: str, cover_map: dict[str, str]) -> str:
        cover_url, _, cover_id = url.rpartition("/")
        return f"{cover_url}/{cover_map[self.cover_size.value]}{cover_id[16:]}"

    def get_playlist_tags(self, playlist_data: dict, track: int) -> PlaylistTags:
        return PlaylistTags(
            id=playlist_data["uri"].split(":")[-1],
            artist=playlist_data["ownerV2"]["data"]["name"],
            title=playlist_data["name"],
            track=track,
            track_total=playlist_data["content"]["totalCount"],
        )

    @staticmethod
    def format_names(names: list[str]) -> str | None:
        if not names:
            return None
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} & {names[1]}"
        return ", ".join(names[:-1]) + " & " + names[-1]

    @staticmethod
    def parse_rating(label: str) -> MediaRating:
        if label == "EXPLICIT":
            return MediaRating.EXPLICIT
        elif label == "NONE":
            return MediaRating.NONE
        else:
            return MediaRating.CLEAN

    @staticmethod
    def parse_date(iso_date: str) -> datetime.date:
        return datetime.datetime.fromisoformat(iso_date.replace("Z", "+00:00")).date()
