from __future__ import annotations

import functools
import json
import logging
import re
import time
import typing
from http.cookiejar import MozillaCookieJar
from pathlib import Path

import base62
import requests

from .device_flow import SpotifyDeviceFlow
from .totp import TOTP
from .utils import check_response

logger = logging.getLogger("votify")


class SpotifyApi:
    SPOTIFY_HOME_PAGE_URL = "https://open.spotify.com/"
    SPOTIFY_COOKIE_DOMAIN = ".spotify.com"
    CLIENT_VERSION = "1.2.70.61.g856ccd63"
    LYRICS_API_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
    METADATA_API_URL = "https://api-partner.spotify.com/pathfinder/v2/query"
    GID_METADATA_API_URL = "https://spclient.wg.spotify.com/metadata/4/{media_type}/{gid}?market=from_token"
    PATHFINDER_API_URL = "https://api-partner.spotify.com/pathfinder/v1/query"
    VIDEO_MANIFEST_API_URL = "https://gue1-spclient.spotify.com/manifests/v7/json/sources/{gid}/options/supports_drm"
    TRACK_PLAYBACK_API_URL = "https://gue1-spclient.spotify.com/track-playback/v1/media/spotify:{type}:{id}"
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
    CLIENT_TOKEN_URL = "https://clienttoken.spotify.com/v1/clienttoken"

    def __init__(
        self, *,
        secrets_url: str,
        sp_dc: str | None = None,
        use_device_flow: bool = False,
    ) -> None:
        self.session = requests.Session()

        secrets = self.session.get(secrets_url)
        check_response(secrets)
        totp_version, secrets_ciphertext = max(secrets.json().items(), key=lambda item: int(item[0]))

        self.totp = TOTP(version=totp_version, ciphertext=secrets_ciphertext)
        self.sp_dc = sp_dc
        self.use_device_flow = use_device_flow
        self._set_session()

    @classmethod
    def from_cookies_file(cls, cookies_path: Path, **kwargs) -> SpotifyApi:
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
        return cls(sp_dc=sp_dc, **kwargs)

    def _set_session(self) -> None:
        self._setup_session_headers()
        self._setup_authorization()
        self._setup_user_profile()

    def _setup_session_headers(self) -> None:
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

    def _get_server_time(self) -> int:
        response = self.session.get(self.SERVER_TIME_URL)
        check_response(response)
        return 1e3 * response.json()["serverTime"]

    def set_token_headers(self, token: str, client_token: str | None = None) -> None:

        self.session.headers.update(
            {
                "authorization": f"Bearer {token}",
                "client-token": client_token
            }
        )

    def _setup_authorization_with_totp(self) -> None:
        server_time = self._get_server_time()
        totp = self.totp.generate(timestamp=server_time)
        response = self.session.get(
            self.SESSION_TOKEN_URL,
            params={
                "reason": "init",
                "productType": "web-player",
                "totp": totp,
                "totpServer": totp,
                "totpVer": str(self.totp.version),
            },
        )
        check_response(response)
        authorization_info = response.json()
        if not authorization_info.get("accessToken"):
            raise ValueError("Failed to retrieve access token.")
        
        response = self.session.post(self.CLIENT_TOKEN_URL,
                json = {
                    'client_data': {
                        'client_version': self.CLIENT_VERSION,
                        'client_id': authorization_info['clientId'],
                        'js_sdk_data': {}
                    }
                },
                headers = {
                    'Accept': 'application/json',
                }
        )
        check_response(response)
        client_token = response.json()
        if not client_token.get("granted_token"):
            raise ValueError("Failed to retrieve granted token.")
        
        self.set_token_headers(authorization_info["accessToken"], client_token["granted_token"]["token"])
        self.session_auth_expire_time = (
            authorization_info["accessTokenExpirationTimestampMs"] / 1000
        )   

    def _setup_authorization(self) -> None:
        if self.use_device_flow:
            self._setup_authorization_with_device_flow()
        else:
            self._setup_authorization_with_totp()

    def _setup_authorization_with_device_flow(self) -> None:
        device_flow = SpotifyDeviceFlow(self.sp_dc)
        token_data = device_flow.get_token()
        self.set_token_headers(token_data["access_token"])
        self.session_auth_expire_time = (
            int(time.time()) + token_data["expires_in"]
        ) * 1000

    def _refresh_session_auth(self) -> None:
        timestamp_session_expire = int(self.session_auth_expire_time)
        timestamp_now = time.time()
        if timestamp_now < timestamp_session_expire:
            return
        self._setup_authorization()

    def _setup_user_profile(self) -> None:
        payload = {
            "variables": {},
            "operationName": "accountAttributes",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "24aaa3057b69fa91492de26841ad199bd0b330ca95817b7a4d6715150de01827"
                }
            }
        }

        response = self.session.post(
            self.METADATA_API_URL,
            json=payload,
        )
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
        response = self.session.get(self.GID_METADATA_API_URL.format(gid=gid, media_type=media_type))
        check_response(response)
        return response.json()

    def get_track_playback_info(
        self,
        media_id: str,
        media_type: str
    ) -> dict | None:
        self._refresh_session_auth()
        params = {"manifestFileFormat": ["file_ids_mp4"]}
        response = self.session.get(f'https://gue1-spclient.spotify.com/track-playback/v1/media/spotify:{media_type}:{media_id}?manifestFileFormat=file_ids_mp4')
        return response.json()

    def get_lyrics(self, track_id: str) -> dict | None:
        self._refresh_session_auth()
        response = self.session.get(self.LYRICS_API_URL.format(track_id=track_id))
        if response.status_code == 404:
            return None
        check_response(response)
        return response.json()

    def extract_keys_with_cdrm(self, pssh, media_type):
        cmd = self.session.post('https://cdrm-project.com/api/decrypt',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
            json={
                  'pssh': pssh,
                  'licurl': self.WIDEVINE_LICENSE_API_URL.format(type=media_type),
                  'headers': json.dumps(self.session.headers)
            }).json()
        return cmd['message']

    def get_track(self, track_id: str) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:track:{track_id}"
            },
            "operationName": "getTrack",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "612585ae06ba435ad26369870deaae23b5c8800a256cd8a57e08eddc25a37294"
                }
            }
        }

        response = self.session.post(
            self.METADATA_API_URL,
            json=payload,
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
        payload = {
            "variables": {
                "uri": f"spotify:album:{album_id}", "locale": "intl-pt", "offset": 0, "limit": 5000
            },
            "operationName": "getAlbum",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10"
                }
            }
        }

        response = self.session.post(
            self.METADATA_API_URL,
            json=payload,
        )

        return response.json()['data']['albumUnion']['tracksV2']['items']


    def get_playlist(
        self,
        playlist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:playlist:{playlist_id}",
                "offset": 0,
                "limit": 5000,
                "enableWatchFeedEntrypoint": True
            },
            "operationName": "fetchPlaylist",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "bb67e0af06e8d6f52b531f97468ee4acd44cd0f82b988e15c2ea47b1148efc77"
                }
            }
        }

        response = self.session.post(
            self.METADATA_API_URL,
            json=payload,
        )
        return response.json()['data']['playlistV2']


    def get_track_credits(self, track_id: str) -> dict:
        self._refresh_session_auth()
        response = self.session.get(
            self.TRACK_CREDITS_API_URL.format(track_id=track_id)
        )
        check_response(response)
        return response.json()

    def get_episode(self, episode_id: str) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:episode:{episode_id}"
            },
            "operationName": "getEpisodeOrChapter",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "8a62dbdeb7bd79605d7d68b01bcdf83f08bc6c6287ee1665ba012c748a4cf1f3"
                }
            }
        }

        response = self.session.post(
            self.METADATA_API_URL,
            json=payload,
        )
        check_response(response)
        return response.json()['data']['episodeUnionV2']

    def get_show(self, show_id: str, extend: bool = True) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:show:{show_id}",
                "offset": 0,
                "limit": 5000
            },
            "operationName": "queryPodcastEpisodes",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "8e2826c5993383566cc08bf9f5d3301b69513c3f6acb8d706286855e57bf44b2"
                }
            }
        }
        response = self.session.post(
            self.METADATA_API_URL,
            json=payload,
        )
        check_response(response)
        show = response.json()
        '''if extend:
            show["episodes"]["items"].extend(
                [
                    item
                    for extended_collection in self.extended_media_collection(
                        show["episodes"]["next"],
                    )
                    for item in extended_collection["items"]
                ]
            )'''
        return show["data"]['podcastUnionV2']

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
