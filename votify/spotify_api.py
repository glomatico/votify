from __future__ import annotations

import functools
import json
import time
import typing
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlparse, parse_qs
from pathlib import Path

import base62
import requests

from .totp import TOTP
from .utils import check_response

import logging
logger = logging.getLogger("votify")

class SpotifyApi:
    SPOTIFY_HOME_PAGE_URL = "https://open.spotify.com/"
    SPOTIFY_COOKIE_DOMAIN = ".spotify.com"
    CLIENT_VERSION = "1.2.70.61.g856ccd63"
    LYRICS_API_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
    METADATA_API_URL = "https://api.spotify.com/v1/{type}/{item_id}"
    GID_METADATA_API_URL = "https://spclient.wg.spotify.com/metadata/4/{media_type}/{gid}?market=from_token"
    PATHFINDER_API_URL = "https://api-partner.spotify.com/pathfinder/v1/query"
    VIDEO_MANIFEST_API_URL = "https://gue1-spclient.spotify.com/manifests/v7/json/sources/{gid}/options/supports_drm"
    PLAYPLAY_LICENSE_API_URL = (
        "https://gew4-spclient.spotify.com/playplay/v1/key/{file_id}"
    )
    WIDEVINE_LICENSE_API_URL = (
        "https://gue1-spclient.spotify.com/widevine-license/v1/{type}/license"
    )
    SEEK_TABLE_API_URL = "https://seektables.scdn.co/seektable/{file_id}.json"
    TRACK_CREDITS_API_URL = "https://spclient.wg.spotify.com/track-credits-view/v0/experimental/{track_id}/credits"
    STREAM_URLS_API_URL = (
        "https://gue1-spclient.spotify.com/storage-resolve/v2/files/audio/interactive/11/"
        "{file_id}?version=10000000&product=9&platform=39&alt=json"
    )
    EXTEND_TRACK_COLLECTION_WAIT_TIME = 0.5
    SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
    SESSION_TOKEN_URL = "https://open.spotify.com/api/token"
    DEVICE_AUTH_URL = "https://accounts.spotify.com/oauth2/device/authorize"
    DEVICE_TOKEN_URL = "https://accounts.spotify.com/api/token"
    DEVICE_RESOLVE_URL = "https://accounts.spotify.com/pair/api/resolve"
    DEVICE_CLIENT_ID = "65b708073fc0480ea92a077233ca87bd" # Spotify for Desktop
    DEVICE_SCOPE = "app-remote-control,playlist-modify,playlist-modify-private,playlist-modify-public,playlist-read,playlist-read-collaborative,playlist-read-private,streaming,transfer-auth-session,ugc-image-upload,user-follow-modify,user-follow-read,user-library-modify,user-library-read,user-modify,user-modify-playback-state,user-modify-private,user-personalized,user-read-birthdate,user-read-currently-playing,user-read-email,user-read-play-history,user-read-playback-position,user-read-playback-state,user-read-private,user-read-recently-played,user-top-read"
    DEVICE_FLOW_USER_AGENT = "Spotify/126600447 Win32_x86_64/0 (PC laptop)"

    def __init__(
        self,
        sp_dc: str | None = None,
    ):
        self.sp_dc = sp_dc
        self._set_session()

    @classmethod
    def from_cookies_file(cls, cookies_path: Path) -> SpotifyApi:
        cookies = MozillaCookieJar(cookies_path)
        cookies.load(ignore_discard=True, ignore_expires=True)
        parse_cookie = lambda name: next(
            (
                cookie.value
                for cookie in cookies
                if cookie.name == name and cookie.domain == cls.SPOTIFY_COOKIE_DOMAIN
            ),
            None,
        )
        sp_dc = parse_cookie("sp_dc")
        if sp_dc is None:
            raise ValueError(
                '"sp_dc" cookie not found in cookies. '
                "Make sure you have exported the cookies from the Spotify homepage and are logged in."
            )
        return cls(sp_dc=sp_dc)

    def _set_session(self):
        self.totp = TOTP()
        self.session = requests.Session()
        self._setup_session_headers()
        self._set_session_info()
        self._set_user_profile()

    def _setup_session_headers(self):
        headers = {
            "accept": "application/json",
            "accept-language": "en-US",
            "content-type": "application/json",
            "origin": self.SPOTIFY_HOME_PAGE_URL,
            "priority": "u=1, i",
            "referer": self.SPOTIFY_HOME_PAGE_URL,
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "spotify-app-version": self.CLIENT_VERSION,
            "app-platform": "WebPlayer",
        }
        self.session.headers.update(headers)
        
        if self.sp_dc:
            self.session.cookies.update({"sp_dc": self.sp_dc})

    def _set_session_info(self):
        try:
            self._set_session_info_with_totp()
        except (KeyError, requests.exceptions.HTTPError):
            self._handle_totp_failure()

    def _set_session_info_with_totp(self):
        server_time = self._get_server_time()
        totp = self.totp.generate(timestamp=server_time)
        
        params = {
            "reason": "init",
            "productType": "web-player",
            "totp": totp,
            "totpVer": str(self.totp.version),
            "ts": str(server_time),
        }
        
        session_info_response = self.session.get(self.SESSION_TOKEN_URL, params=params)
        self._update_session_token(session_info_response.json())

    def _get_server_time(self):
        server_time_response  = self.session.get(self.SERVER_TIME_URL)
        check_response(server_time_response)
        return 1e3 * server_time_response.json()["serverTime"]

    def _update_session_token(self, session_info):
        self.session_info = session_info
        self.session.headers.update({
            "authorization": f"Bearer {self.session_info['accessToken']}",
        })

    def _handle_totp_failure(self):
        logger.warning("Failed to obtain the access token with the current TOTP secret.")
        token_data = self._get_token_via_device_flow()
        
        if not token_data or "access_token" not in token_data:
            logger.error("Could not obtain access token by any method.")
        
        self.session_info = {
            "accessToken": token_data["access_token"],
            "accessTokenExpirationTimestampMs": (int(time.time()) + token_data["expires_in"]) * 1000,
        }
        
        logger.info("Access token obtained using the desktop endpoint.")
        self.session.headers.update({
            "authorization": f"Bearer {self.session_info['accessToken']}",
        })

    def _get_token_via_device_flow(self):
        auth_data = self._initiate_device_authorization()
        device_code = auth_data["device_code"]
        user_code = auth_data["user_code"]
        verification_url = auth_data["verification_uri_complete"]
        
        flow_ctx, csrf_token = self._parse_verification_page(verification_url)
        if not flow_ctx:
            logger.error("Could not extract flow_ctx.")
            return None

        if not csrf_token:
            logger.error("Could not extract CSRF token.")
            return None
            
        if not self._submit_user_code(user_code, flow_ctx, csrf_token, verification_url):
            logger.error("Device pairing was unsuccessful.")
            return None
            
        return self._exchange_device_code(device_code)

    def _initiate_device_authorization(self):
        response = requests.post(
            self.DEVICE_AUTH_URL,
            data={'client_id': self.DEVICE_CLIENT_ID, 'scope': self.DEVICE_SCOPE},
            headers={
                'User-Agent': self.DEVICE_FLOW_USER_AGENT,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )
        response.raise_for_status()
        return response.json()

    def _parse_verification_page(self, verification_url):
        try:
            response = self.session.get(verification_url, allow_redirects=True)
            response.raise_for_status()

            parsed_url = urlparse(response.url)
            flow_ctx_full = parse_qs(parsed_url.query).get("flow_ctx", [None])[0]
            flow_ctx = flow_ctx_full.split(":")[0] if flow_ctx_full else None

            csrf_token = self._extract_csrf_token(response.text)
            return flow_ctx, csrf_token
            
        except Exception as e:
            logger.error(f"ERROR (Parsing verification page): {e}")
            return None, None

    def _extract_csrf_token(self, html_content):
        start_marker = '<script id="__NEXT_DATA__" type="application/json"'
        start_index = html_content.find(start_marker)
        if start_index == -1:
            return None

        start_index = html_content.find(">", start_index) + 1
        end_index = html_content.find("</script>", start_index)
        json_data = json.loads(html_content[start_index:end_index])
        return json_data.get("props", {}).get("initialToken")

    def _submit_user_code(self, user_code, flow_ctx, csrf_token, referer_url):
        try:
            current_ts = int(time.time())
            response = self.session.post(
                self.DEVICE_RESOLVE_URL,
                params={"flow_ctx": f"{flow_ctx}:{current_ts}"},
                json={"code": user_code},
                headers={
                    "x-csrf-token": csrf_token,
                    "referer": referer_url,
                    "origin": "https://accounts.spotify.com",
                    "content-type": "application/json",
                },
            )
            response.raise_for_status()
            return response.json().get("result") == "ok"
        except Exception as e:
            logger.error(f"ERROR (Submitting user code): {e}")
            return False

    def _exchange_device_code(self, device_code):
        try:
            response = requests.post(
                self.DEVICE_TOKEN_URL,
                data={
                    "client_id": self.DEVICE_CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                headers={
                    'User-Agent': self.DEVICE_FLOW_USER_AGENT,
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"ERROR (Exchanging device code): {e}")
            return None

    def _refresh_session_auth(self):
        timestamp_session_expire = int(
            self.session_info["accessTokenExpirationTimestampMs"]
        )
        timestamp_now = time.time() * 1000
        if timestamp_now < timestamp_session_expire:
            return
        self._set_session_info()

    def _set_user_profile(self):
        response = self.session.get(self.METADATA_API_URL.format(type="me", item_id=""))
        check_response(response)
        self.user_profile = response.json()

    @staticmethod
    def media_id_to_gid(media_id: str) -> str:
        return hex(base62.decode(media_id, base62.CHARSET_INVERTED))[2:].zfill(32)

    @staticmethod
    def gid_to_media_id(gid: str) -> str:
        return base62.encode(int(gid, 16), charset=base62.CHARSET_INVERTED).zfill(22)

    def get_gid_metadata(
        self,
        gid: str,
        media_type: str,
    ) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.GID_METADATA_API_URL.format(gid=gid, media_type=media_type)
        )
        check_response(response)
        return response.json()

    def get_lyrics(self, track_id: str) -> dict | None:
        self._refresh_session_auth()
        response = self.session.get(self.LYRICS_API_URL.format(track_id=track_id))
        if response.status_code == 404:
            return None
        check_response(response)
        return response.json()

    def get_track(self, track_id: str) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.METADATA_API_URL.format(type="tracks", item_id=track_id)
        )
        check_response(response)
        return response.json()

    def extended_media_collection(
        self,
        next_url: str,
    ) -> typing.Generator[dict, None, None]:
        while next_url is not None:
            response = self.session.get(next_url)
            check_response(response)
            extended_collection = response.json()
            yield extended_collection
            next_url = extended_collection["next"]
            time.sleep(self.EXTEND_TRACK_COLLECTION_WAIT_TIME)

    @functools.lru_cache()
    def get_album(
        self,
        album_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.METADATA_API_URL.format(type="albums", item_id=album_id)
        )
        check_response(response)
        album = response.json()
        if extend:
            album["tracks"]["items"].extend(
                [
                    item
                    for extended_collection in self.extended_media_collection(
                        album["tracks"]["next"],
                    )
                    for item in extended_collection["items"]
                ]
            )
        return album

    def get_playlist(
        self,
        playlist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.METADATA_API_URL.format(type="playlists", item_id=playlist_id)
        )
        check_response(response)
        playlist = response.json()
        if extend:
            playlist["tracks"]["items"].extend(
                [
                    item
                    for extended_collection in self.extended_media_collection(
                        playlist["tracks"]["next"],
                    )
                    for item in extended_collection["items"]
                ]
            )
        return playlist

    def get_track_credits(self, track_id: str) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.TRACK_CREDITS_API_URL.format(track_id=track_id)
        )
        check_response(response)
        return response.json()

    def get_episode(self, episode_id: str) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.METADATA_API_URL.format(type="episodes", item_id=episode_id)
        )
        check_response(response)
        return response.json()

    def get_show(self, show_id: str, extend: bool = True) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.METADATA_API_URL.format(type="shows", item_id=show_id)
        )
        check_response(response)
        show = response.json()
        if extend:
            show["episodes"]["items"].extend(
                [
                    item
                    for extended_collection in self.extended_media_collection(
                        show["episodes"]["next"],
                    )
                    for item in extended_collection["items"]
                ]
            )
        return show

    def get_artist_albums(
        self,
        artist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.METADATA_API_URL.format(type="artists", item_id=artist_id) + "/albums"
        )
        check_response(response)
        artist_albums = response.json()
        if extend:
            artist_albums["items"].extend(
                [
                    item
                    for extended_collection in self.extended_media_collection(
                        artist_albums["next"],
                    )
                    for item in extended_collection["items"]
                ]
            )
        return artist_albums

    def get_video_manifest(
        self,
        gid: str,
    ) -> dict:
        self._refresh_session_auth()
        response = self.session.get(self.VIDEO_MANIFEST_API_URL.format(gid=gid))
        check_response(response)
        return response.json()

    def get_seek_table(self, file_id: str) -> dict:
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Origin": self.SPOTIFY_HOME_PAGE_URL,
            "Pragma": "no-cache",
            "Priority": "u=4",
            "Referer": self.SPOTIFY_HOME_PAGE_URL,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": self.session.headers["user-agent"],
        }
        response = requests.get(
            self.SEEK_TABLE_API_URL.format(file_id=file_id),
            headers=headers,
        )
        check_response(response)
        return response.json()

    def get_playplay_license(self, file_id: str, challenge: bytes) -> bytes:
        self._refresh_session_auth()
        response = self.session.post(
            self.PLAYPLAY_LICENSE_API_URL.format(file_id=file_id),
            challenge,
        )
        check_response(response)
        return response.content

    def get_widevine_license(self, challenge: bytes, media_type: str) -> bytes:
        self._refresh_session_auth()
        response = self.session.post(
            self.WIDEVINE_LICENSE_API_URL.format(type=media_type),
            challenge,
        )
        check_response(response)
        return response.content

    def get_stream_urls(self, file_id: str) -> str:
        self._refresh_session_auth()
        response = self.session.get(self.STREAM_URLS_API_URL.format(file_id=file_id))
        check_response(response)
        return response.json()

    def get_now_playing_view(self, track_id: str, artist_id: str) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.PATHFINDER_API_URL,
            params={
                "operationName": "queryNpvArtist",
                "variables": json.dumps(
                    {
                        "artistUri": f"spotify:artist:{artist_id}",
                        "trackUri": f"spotify:track:{track_id}",
                        "enableCredits": True,
                        "enableRelatedVideos": True,
                    }
                ),
                "extensions": json.dumps(
                    {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "4ec4ae302c609a517cab6b8868f601cd3457c751c570ab12e988723cc036284f",
                        }
                    }
                ),
            },
        )
        check_response(response)
        return response.json()
