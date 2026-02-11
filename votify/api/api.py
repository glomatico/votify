import base64
import logging
import time
from http.cookiejar import MozillaCookieJar

import base62
import httpx

from ..utils import safe_json
from .constants import (
    CLIENT_TOKEN_URL,
    CLIENT_VERSION,
    COOKIE_DOMAIN,
    GID_METADATA_URL,
    HOME_PAGE_URL,
    LYRICS_API_URL,
    PATHFINDER_API_URL,
    SEEK_TABLE_API_URL,
    SERVER_TIME_URL,
    SESSION_TOKEN_URL,
    AUDIO_STREAM_URLS_API_URL,
    TRACK_CREDITS_API_URL,
    TRACK_PLAYBACK_API_URL,
    VIDEO_MANIFEST_API_URL,
    WIDEVINE_LICENSE_API_URL,
)
from .exceptions import VotifyRequestException
from .totp import Totp

logger = logging.getLogger(__name__)


class SpotifyApi:
    def __init__(
        self,
        sp_dc: str | None = None,
    ) -> None:
        self.sp_dc = sp_dc

    @property
    def premium_session(self) -> bool:
        return (
            getattr(self, "user_profile", {})
            .get("data", {})
            .get("account", {})
            .get("product")
            == "PREMIUM"
        )

    @property
    def anonymous_session(self) -> bool:
        return self.user_profile is None

    @staticmethod
    def _parse_cookies(cookies_path: str) -> dict[str, str]:
        cookies = MozillaCookieJar(cookies_path)
        cookies.load(ignore_discard=True, ignore_expires=True)

        cookie_dict = {
            cookie.name: cookie.value
            for cookie in cookies
            if cookie.domain == COOKIE_DOMAIN
        }

        logger.debug(f"Parsed cookies: {cookie_dict}")

        return cookie_dict

    @classmethod
    async def create_from_netscape_cookies(cls, cookies_path: str) -> "SpotifyApi":
        cookies = cls._parse_cookies(cookies_path)
        sp_dc = cookies.get("sp_dc")
        if sp_dc is None:
            raise ValueError(
                "'sp_dc' cookie not found in cookies. "
                "Make sure you have exported the cookies "
                "from the Spotify homepage and are logged in."
            )

        return await cls.create(sp_dc=sp_dc)

    @classmethod
    async def create(
        cls,
        *args,
        **kwargs,
    ) -> "SpotifyApi":
        api = cls(*args, **kwargs)

        await api._initialize()

        return api

    async def _initialize(self) -> None:
        self._initialize_client()
        await self._initialize_totp()
        await self._initialize_authorization()
        await self._initialize_user_profile()

    def _initialize_client(self) -> None:
        self.client = httpx.AsyncClient()

        self.client.headers.update(
            {
                "accept": "application/json",
                "accept-language": "en-US",
                "content-type": "application/json",
                "origin": HOME_PAGE_URL,
                "priority": "u=1, i",
                "referer": HOME_PAGE_URL,
                "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "spotify-app-version": CLIENT_VERSION,
                "app-platform": "WebPlayer",
            }
        )

        if self.sp_dc:
            self.client.cookies.update({"sp_dc": self.sp_dc})

    async def _initialize_totp(self) -> Totp:
        self.totp = await Totp.initialize()

    async def _initialize_authorization(self) -> None:
        session_info = await self._get_session_token()
        client_token = await self._get_client_token(session_info["clientId"])

        access_token = session_info["accessToken"]
        granted_token = client_token["granted_token"]["token"]

        self._authorization_expire_time = (
            session_info["accessTokenExpirationTimestampMs"] / 1000
        )

        self.client.headers.update(
            {
                "authorization": f"Bearer {access_token}",
                "client-token": granted_token,
            }
        )

    async def _initialize_user_profile(self) -> None:
        self.user_profile = await self._get_user_profile() if self.sp_dc else None

    async def _get_server_time(self) -> int:
        response = await self.client.get(SERVER_TIME_URL)
        server_time = safe_json(response)
        if response.status_code != 200 or not server_time:
            raise VotifyRequestException(
                name="Server time",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received server time: {server_time}")

        return 1e3 * server_time["serverTime"]

    async def _get_session_token(self) -> None:
        server_time = await self._get_server_time()

        generated_totp = self.totp.generate(timestamp=server_time)

        response = await self.client.get(
            SESSION_TOKEN_URL,
            params={
                "reason": "init",
                "productType": "web-player",
                "totp": generated_totp,
                "totpServer": generated_totp,
                "totpVer": self.totp.version,
            },
        )
        session_info = safe_json(response)
        if response.status_code != 200 or not session_info:
            raise VotifyRequestException(
                name="Session info",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received session info: {session_info}")

        return session_info

    async def _get_client_token(self, client_id: str) -> None:
        response = await self.client.post(
            CLIENT_TOKEN_URL,
            json={
                "client_data": {
                    "client_version": CLIENT_VERSION,
                    "client_id": client_id,
                    "js_sdk_data": {},
                }
            },
            headers={
                "Accept": "application/json",
            },
        )
        client_token = safe_json(response)
        if response.status_code != 200 or not client_token:
            raise VotifyRequestException(
                name="Client token",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received client token: {client_token}")

        return client_token

    async def _refresh_authorization_if_needed(self) -> None:
        timestamp_session_expire = int(self._authorization_expire_time)
        timestamp_now = time.time()
        if timestamp_now < timestamp_session_expire:
            return
        await self._initialize_authorization()

    @staticmethod
    def media_id_to_gid(media_id: str) -> str:
        return hex(base62.decode(media_id, base62.CHARSET_INVERTED))[2:].zfill(32)

    @staticmethod
    def gid_to_media_id(gid: str) -> str:
        return base62.encode(int(gid, 16), charset=base62.CHARSET_INVERTED).zfill(22)

    async def _pathfinder_request(
        self,
        operation_name: str,
        persisted_query_hash: str,
        variables: dict = {},
    ) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.post(
            PATHFINDER_API_URL,
            json={
                "variables": variables,
                "operationName": operation_name,
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": persisted_query_hash,
                    }
                },
            },
        )
        response_json = safe_json(response)

        if (
            response.status_code != 200
            or not response_json
            or "errors" in response_json
        ):
            raise VotifyRequestException(
                name="Pathfinder",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        return response_json

    async def _get_user_profile(self) -> dict:
        user_profile = await self._pathfinder_request(
            operation_name="accountAttributes",
            persisted_query_hash="24aaa3057b69fa91492de26841ad199bd0b330ca95817b7a4d6715150de01827",
        )

        logger.debug(f"Received user profile: {user_profile}")

        return user_profile

    async def get_track(self, track_id: str) -> dict:
        result = await self._pathfinder_request(
            operation_name="getTrack",
            persisted_query_hash="612585ae06ba435ad26369870deaae23b5c8800a256cd8a57e08eddc25a37294",
            variables={"uri": f"spotify:track:{track_id}"},
        )

        logger.debug(f"Received track: {result}")

        return result

    async def get_album(
        self,
        album_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        album = await self._pathfinder_request(
            operation_name="getAlbum",
            persisted_query_hash="b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10",
            variables={
                "uri": f"spotify:album:{album_id}",
                "offset": offset,
                "limit": limit,
            },
        )

        logger.debug(f"Received album: {album}")

        return album

    async def get_playlist(
        self,
        playlist_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        playlist = await self._pathfinder_request(
            operation_name="fetchPlaylist",
            persisted_query_hash="bb67e0af06e8d6f52b531f97468ee4acd44cd0f82b988e15c2ea47b1148efc77",
            variables={
                "uri": f"spotify:playlist:{playlist_id}",
                "offset": offset,
                "limit": limit,
                "enableWatchFeedEntrypoint": True,
            },
        )

        logger.debug(f"Received playlist: {playlist}")

        return playlist

    async def get_episode(self, episode_id: str) -> dict:
        episode = await self._pathfinder_request(
            operation_name="getEpisodeOrChapter",
            persisted_query_hash="8a62dbdeb7bd79605d7d68b01bcdf83f08bc6c6287ee1665ba012c748a4cf1f3",
            variables={"uri": f"spotify:episode:{episode_id}"},
        )

        logger.debug(f"Received episode: {episode}")

        return episode

    async def get_show(
        self,
        show_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        show = await self._pathfinder_request(
            operation_name="queryPodcastEpisodes",
            persisted_query_hash="8e2826c5993383566cc08bf9f5d3301b69513c3f6acb8d706286855e57bf44b2",
            variables={
                "uri": f"spotify:show:{show_id}",
                "offset": offset,
                "limit": limit,
            },
        )

        logger.debug(f"Received show: {show}")

        return show

    async def _get_artist_discography(
        self,
        artist_id: str,
        type: str,
        offeset: int,
        limit: int,
    ) -> dict:
        result = await self._pathfinder_request(
            operation_name=f"queryArtistDiscography{type.capitalize()}s",
            persisted_query_hash="5e07d323febb57b4a56a42abbf781490e58764aa45feb6e3dc0591564fc56599",
            variables={
                "uri": f"spotify:artist:{artist_id}",
                "offset": offeset,
                "limit": limit,
                "order": "DATE_DESC",
            },
        )

        logger.debug(f"Received artist {type}s: {result}")

        return result

    async def get_artist_albums(
        self,
        artist_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        return await self._get_artist_discography(
            artist_id=artist_id,
            type="album",
            offeset=offset,
            limit=limit,
        )

    async def get_artist_singles(
        self,
        artist_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        return await self._get_artist_discography(
            artist_id=artist_id,
            type="single",
            offeset=offset,
            limit=limit,
        )

    async def get_artist_compilations(
        self,
        artist_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        return await self._get_artist_discography(
            artist_id=artist_id,
            type="compilation",
            offeset=offset,
            limit=limit,
        )

    async def get_artist_videos(
        self,
        artist_id: str,
        offset: int = 0,
        limit: int = 300,
    ) -> dict:
        artist_videos = await self._pathfinder_request(
            operation_name="queryArtistRelatedVideos",
            persisted_query_hash="8958042d3dd127ec7882a7117fafa4df21af27ff1560af51e55061e8451de67b",
            variables={
                "uri": f"spotify:artist:{artist_id}",
                "showMapped": True,
                "showUnmapped": True,
                "offset": offset,
                "limit": limit,
            },
        )

        logger.debug(f"Received artist videos: {artist_videos}")

        return artist_videos

    async def get_video_manifest(
        self,
        file_id: str,
    ) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.get(VIDEO_MANIFEST_API_URL.format(file_id=file_id))
        video_manifest = safe_json(response)

        if response.status_code != 200 or not video_manifest:
            raise VotifyRequestException(
                name="Video manifest",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received video manifest: {video_manifest}")

        return video_manifest

    async def get_seek_table(self, file_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                SEEK_TABLE_API_URL.format(file_id=file_id),
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Origin": HOME_PAGE_URL,
                    "Pragma": "no-cache",
                    "Priority": "u=4",
                    "Referer": HOME_PAGE_URL,
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "User-Agent": self.client.headers["user-agent"],
                },
            )
        seek_table = safe_json(response)

        if response.status_code != 200 or not seek_table:
            raise VotifyRequestException(
                name="Seek table",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received seek table: {seek_table}")

        return seek_table

    async def get_track_playback_info(
        self,
        media_id: str,
        media_type: str,
        file_formats: list[str] = ["file_ids_mp4", "manifest_ids_video"],
    ) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.get(
            TRACK_PLAYBACK_API_URL.format(
                media_id=media_id,
                media_type=media_type,
            ),
            params={
                "manifestFileFormat": file_formats,
            },
        )
        track_playback_info = safe_json(response)

        if response.status_code != 200 or not track_playback_info:
            raise VotifyRequestException(
                name="Track playback info",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received track playback info: {track_playback_info}")

        return track_playback_info

    async def get_gid_metadata(
        self,
        media_id: str,
        media_type: str,
    ) -> dict:
        return await self._get_gid_metadata(
            gid=self.media_id_to_gid(media_id),
            media_type=media_type,
        )

    async def _get_gid_metadata(
        self,
        gid: str,
        media_type: str,
    ) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.get(
            GID_METADATA_URL.format(
                gid=gid,
                media_type=media_type,
            )
        )
        gid_metadata = safe_json(response)

        if response.status_code != 200 or not gid_metadata:
            raise VotifyRequestException(
                name="GID metadata",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received GID metadata: {gid_metadata}")

        return gid_metadata

    async def get_lyrics(self, track_id: str) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.get(LYRICS_API_URL.format(track_id=track_id))
        lyrics = safe_json(response)

        if response.status_code != 200 or not lyrics:
            raise VotifyRequestException(
                name="Lyrics",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received lyrics: {lyrics}")

        return lyrics

    async def get_track_credits(self, track_id: str) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.get(
            TRACK_CREDITS_API_URL.format(track_id=track_id)
        )
        track_credits = safe_json(response)

        if response.status_code != 200 or not track_credits:
            raise VotifyRequestException(
                name="Track credits",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received track credits: {track_credits}")

        return track_credits

    async def get_widevine_license(self, challenge: bytes, media_type: str) -> bytes:
        await self._refresh_authorization_if_needed()

        response = await self.client.post(
            WIDEVINE_LICENSE_API_URL.format(type=media_type),
            data=challenge,
        )
        widevine_license = response.content

        if response.status_code != 200 or not widevine_license:
            raise VotifyRequestException(
                name="Widevine license",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(
            f"Received Widevine license: {base64.b64encode(widevine_license).decode()}"
        )

        return widevine_license

    async def get_audio_stream_urls(self, file_id: str) -> dict:
        await self._refresh_authorization_if_needed()

        response = await self.client.get(
            AUDIO_STREAM_URLS_API_URL.format(file_id=file_id),
        )
        audio_stream_urls = safe_json(response)

        if response.status_code != 200 or not audio_stream_urls:
            raise VotifyRequestException(
                name="Audio stream URLs",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received audio stream URLs: {audio_stream_urls}")

        return audio_stream_urls
