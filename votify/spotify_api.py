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

import secrets
import websocket
import threading

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
    VIDEO_MANIFEST_API_URL = "https://gue1-spclient.spotify.com/manifests/v9/json/sources/{gid}/options/supports_drm"
    TRACK_PLAYBACK_API_URL = "https://gue1-spclient.spotify.com/track-playback/v1/media/spotify:{media_type}:{media_id}"
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

        TRACK_ID = media_id
        if not hasattr(self, 'cached_device_id'):
            self.cached_device_id = secrets.token_hex(20)

        DEVICE_ID = self.cached_device_id

        ACCESS_TOKEN = self.session.headers["Authorization"].replace("Bearer ", "")
        WS_URL = f"wss://dealer.spotify.com/?access_token={ACCESS_TOKEN}"
        URL_REGISTRO = "https://spclient.wg.spotify.com/track-playback/v1/devices"
        URL_COMMAND = f"https://spclient.wg.spotify.com/connect-state/v1/player/command/from/{DEVICE_ID}/to/{DEVICE_ID}"
        URL = f"https://gue1-spclient.spotify.com/track-playback/v1/devices/{DEVICE_ID}/state"

        class Context:
            conn_id = None
            machine_id = None
            state_id = None
            stop_event = threading.Event()

        ctx = Context()

        def find_key(data, target):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == target: return v
                    res = find_key(v, target)
                    if res: return res
            elif isinstance(data, list):
                for item in data:
                    res = find_key(item, target)
                    if res: return res
            return None

        def on_message(ws, message):
            try:
                data = json.loads(message)
                if "headers" in data and "Spotify-Connection-Id" in data["headers"]:
                    ctx.conn_id = data["headers"]["Spotify-Connection-Id"]

                new_mid = find_key(data, "state_machine_id")
                if new_mid:
                    if new_mid != ctx.machine_id:
                        ctx.machine_id = new_mid

                    new_sid = find_key(data, "state_id")
                    if new_sid and new_sid != ctx.state_id:
                        ctx.state_id = new_sid
            except:
                pass

        def start_socket():
            ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
            ws.run_forever()

        def keep_alive_loop():
            seq_num = 1
            last_mid = None
            attempt_count = 0
            wait_ids_count = 0

            while not ctx.stop_event.is_set():
                if ctx.machine_id and ctx.state_id and ctx.conn_id:
                    wait_ids_count = 0

                    if ctx.machine_id != last_mid:
                        seq_num = 1
                        last_mid = ctx.machine_id

                    payload = {
                        "seq_num": 0,
                        "state_ref": {
                            "state_machine_id": ctx.machine_id,
                            "state_id": ctx.state_id,
                            "paused": False,
                        },
                        "sub_state": {
                            "playback_speed": 1,
                            "position": 1258,
                            "duration": 199954,
                            "media_type": "AUDIO",
                            "bitrate": 128000,
                            "audio_quality": "HIGH",
                            "format": 10,
                            "is_video_on": False,
                        },
                        "previous_position": 1258,
                        "debug_source": "started_playing",
                    }

                    try:
                        r = self.session.put(
                            URL,
                            data=json.dumps(payload, separators=(",", ":"))
                        )

                        if r.status_code == 200:
                            ctx.stop_event.set()
                            break
                        else:
                            attempt_count += 1

                    except Exception as e:
                        attempt_count += 1

                    if attempt_count >= 3:
                        ctx.stop_event.set()
                        break

                    seq_num += 1
                    time.sleep(3)

                else:
                    wait_ids_count += 1
                    time.sleep(0.5)

                    if wait_ids_count > 20:
                        ctx.stop_event.set()
                        break

        t_ws = threading.Thread(target=start_socket, daemon=True)
        t_ws.start()

        while not ctx.conn_id:
            time.sleep(0.1)

        self.session.headers.update({
            "x-spotify-connection-id": ctx.conn_id
        })

        reg_payload = {
            "device": {
                "brand": "spotify",
                "capabilities": {"change_volume": True, "enable_play_token": True, "supports_file_media_type": True,
                    "manifest_formats": ["file_ids_mp4", "file_ids_mp4_dual"], "audio_podcasts": True,
                    "video_playback": True},
                "device_id": DEVICE_ID, "device_type": "computer", "metadata": {}, "model": "web_player",
                "name": "Python Final", "platform_identifier": "web_player windows 10;chrome 124.0.0.0;desktop",
                "is_group": False
            },
            "connection_id": ctx.conn_id, "client_version": "harmony:4.62.1-5dc29b8a7", "volume": 65535
        }
        self.session.post(URL_REGISTRO, json=reg_payload)

        t_put = threading.Thread(target=keep_alive_loop, daemon=True)
        t_put.start()

        track_uri = f"spotify:track:{TRACK_ID}"
        cmd_payload = {
            "command": {
                "context": {"uri": track_uri, "url": f"context://{track_uri}", "metadata": {}},
                "play_origin": {"feature_identifier": "harmony", "feature_version": "4.26.0"},
                "options": {"license": "premium", "skip_to": {"track_uri": track_uri}, "player_options_override": {}},
                "endpoint": "play"
            }
        }
        self.session.post(URL_COMMAND, json=cmd_payload)

        try:
            while not ctx.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            ctx.stop_event.set()

        ##################################################

        params = {
            "manifestFileFormat": [
                "file_ids_mp4",
                "manifest_ids_video"
            ]
        }
        response = self.session.get(
            self.TRACK_PLAYBACK_API_URL.format(
                media_type=media_type,
                media_id=media_id
            ),
            params=params
        )
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
                  'headers': str(self.session.headers)
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

    def get_artist_albums_selection(
        self,
        artist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:artist:{artist_id}",
                "offset": 0,
                "limit": 5000,
                "order": "DATE_DESC"
            },
            "operationName": "queryArtistDiscographyAlbums",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "5e07d323febb57b4a56a42abbf781490e58764aa45feb6e3dc0591564fc56599"
                }
            }
        }
        response = self.session.post(self.METADATA_API_URL, json=payload)
        check_response(response)
        artist_albums = response.json()['data']['artistUnion']['discography']['albums']
        return self._select_and_queue(artist_albums, "Albuns")

    def get_artist_singles_selection(
        self,
        artist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:artist:{artist_id}",
                "offset": 0,
                "limit": 5000,
                "order": "DATE_DESC"
            },
            "operationName": "queryArtistDiscographySingles",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "5e07d323febb57b4a56a42abbf781490e58764aa45feb6e3dc0591564fc56599"
                }
            }
        }
        response = self.session.post(self.METADATA_API_URL, json=payload)
        check_response(response)
        artist_albums = response.json()['data']['artistUnion']['discography']['singles']
        return self._select_and_queue(artist_albums, "Singles")

    def get_artist_compilations_selection(
        self,
        artist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:artist:{artist_id}",
                "offset": 0,
                "limit": 5000,
                "order": "DATE_DESC"
            },
            "operationName": "queryArtistDiscographyCompilations",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "5e07d323febb57b4a56a42abbf781490e58764aa45feb6e3dc0591564fc56599"
                }
            }
        }
        response = self.session.post(self.METADATA_API_URL, json=payload)
        check_response(response)
        artist_albums = response.json()['data']['artistUnion']['discography']['compilations']
        return self._select_and_queue(artist_albums, "Compilations")

    def get_artist_collaborations_selection(
        self,
        artist_id: str,
        extend: bool = True,
    ) -> dict:
        self._refresh_session_auth()
        payload = {
            "variables": {
                "uri": f"spotify:artist:{artist_id}",
                "offset": 0,
                "limit": 5000,
                "order": "DATE_DESC"
            },
            "operationName": "queryArtistAppearsOn",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "9a4bb7a20d6720fe52d7b47bc001cfa91940ddf5e7113761460b4a288d18a4c1"
                }
            }
        }
        response = self.session.post(self.METADATA_API_URL, json=payload)
        check_response(response)
        artist_albums = response.json()['data']['artistUnion']['relatedContent']['appearsOn']
        return self._select_and_queue(artist_albums, "Collaborations")

    def _select_and_queue(self, data_input: any, category_name: str) -> list[str]:
        raw_items = []
        if isinstance(data_input, dict) and 'items' in data_input:
            raw_items = data_input['items']
        elif isinstance(data_input, list):
            raw_items = data_input

        if not raw_items:
            print(f"No {category_name} found for this artist.")
            return []

        clean_list = []
        for entry in raw_items:
            try:
                if 'releases' in entry and 'items' in entry['releases']:
                    album_data = entry['releases']['items'][0]
                    clean_obj = {
                        'name': album_data.get('name', 'Unknown'),
                        'id': album_data.get('id'),
                        'year': str(album_data.get('date', {}).get('year', '????')),
                        'total_tracks': album_data.get('tracks', {}).get('totalCount', 0)
                    }
                    clean_list.append(clean_obj)
                elif 'name' in entry:
                    clean_list.append({
                        'name': entry.get('name'),
                        'id': entry.get('id'),
                        'year': entry.get('release_date', '????')[:4],
                        'total_tracks': entry.get('total_tracks', 0)
                    })
            except Exception:
                continue

        if not clean_list:
            print(f"Could not parse items for {category_name}.")
            return []

        print(f"\n--- Select {category_name} ---")
        print("Index | Tracks | Year | Name")
        for index, album in enumerate(clean_list):
            display_str = f"{album['total_tracks']:03d} | {album['year']} | {album['name']}"
            print(f"[{index + 1}] {display_str}")

        print("\nType numbers separated by space (e.g. '1 3') or 'all'.")
        user_input = input("Selection: ").strip().lower()

        selected_ids = []

        if user_input == 'all':
            selected_ids = [album['id'] for album in clean_list]
        else:
            parts = user_input.replace(',', ' ').split()
            for part in parts:
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(clean_list):
                        selected_ids.append(clean_list[idx]['id'])

        return selected_ids


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
        if response.status_code == 403:
            logger.error(f"The device.wvd file is invalid or banned.")
            logger.warning(f'Delete the device.wvd file to use the alternate key.')
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
