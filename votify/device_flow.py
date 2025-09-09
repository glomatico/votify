from __future__ import annotations

import json
import re
import time
from urllib.parse import parse_qs, urlparse

import requests

from .utils import check_response


class SpotifyDeviceFlow:
    DEVICE_AUTH_URL = "https://accounts.spotify.com/oauth2/device/authorize"
    DEVICE_TOKEN_URL = "https://accounts.spotify.com/api/token"
    DEVICE_RESOLVE_URL = "https://accounts.spotify.com/pair/api/resolve"
    DEVICE_CLIENT_ID = "65b708073fc0480ea92a077233ca87bd"  # Spotify for Desktop
    DEVICE_SCOPE = "app-remote-control,playlist-modify,playlist-modify-private,playlist-modify-public,playlist-read,playlist-read-collaborative,playlist-read-private,streaming,transfer-auth-session,ugc-image-upload,user-follow-modify,user-follow-read,user-library-modify,user-library-read,user-modify,user-modify-playback-state,user-modify-private,user-personalized,user-read-birthdate,user-read-currently-playing,user-read-email,user-read-play-history,user-read-playback-position,user-read-playback-state,user-read-private,user-read-recently-played,user-top-read"
    DEVICE_FLOW_USER_AGENT = "Spotify/126600447 Win32_x86_64/0 (PC laptop)"

    def __init__(self, sp_dc: str) -> None:
        self.session = requests.Session()
        self.session.cookies.update({"sp_dc": sp_dc})

    def get_token(self) -> dict:
        """Get access token via device flow."""
        auth_data = self._initiate_device_authorization()
        device_code = auth_data["device_code"]
        user_code = auth_data["user_code"]
        verification_url = auth_data["verification_uri_complete"]
        flow_ctx, csrf_token = self._parse_verification_page(verification_url)
        self._submit_user_code(user_code, flow_ctx, csrf_token, verification_url)
        return self._exchange_device_code(device_code)

    def _initiate_device_authorization(self) -> dict:
        response = requests.post(
            self.DEVICE_AUTH_URL,
            data={
                "client_id": self.DEVICE_CLIENT_ID,
                "scope": self.DEVICE_SCOPE,
            },
            headers={
                "User-Agent": self.DEVICE_FLOW_USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        check_response(response)
        return response.json()

    def _parse_verification_page(self, verification_url: str) -> tuple[str, str]:
        response = self.session.get(
            verification_url,
            allow_redirects=True,
        )
        check_response(response)

        parsed_url = urlparse(response.url)
        try:
            flow_ctx_full = parse_qs(parsed_url.query)["flow_ctx"][0]
            flow_ctx = flow_ctx_full.split(":")[0]
        except (KeyError, IndexError):
            raise ValueError("Failed to extract flow_ctx")

        csrf_token = self._extract_csrf_token(response.text)

        return flow_ctx, csrf_token

    def _extract_csrf_token(self, html_content: str) -> str | None:
        pattern = (
            r'<script id="__NEXT_DATA__" type="application/json"[^>]*>(.*?)</script>'
        )
        match = re.search(pattern, html_content, re.DOTALL)
        try:
            json_data = json.loads(match.group(1))
            return json_data["props"]["initialToken"]
        except (AttributeError, json.JSONDecodeError, KeyError):
            raise ValueError("Failed to extract CSRF token")

    def _submit_user_code(
        self,
        user_code: str,
        flow_ctx: str,
        csrf_token: str,
        referer_url: str,
    ) -> None:
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
        check_response(response)
        try:
            submit_result = response.json()
            assert submit_result.get("result") == "ok"
        except (json.JSONDecodeError, AssertionError):
            raise ValueError("Failed to submit user code")

    def _exchange_device_code(self, device_code: str) -> dict:
        response = requests.post(
            self.DEVICE_TOKEN_URL,
            data={
                "client_id": self.DEVICE_CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers={
                "User-Agent": self.DEVICE_FLOW_USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        check_response(response)
        return response.json()
