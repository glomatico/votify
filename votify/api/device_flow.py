import json
import logging
import re
import time
from urllib.parse import parse_qs

import httpx

from .constants import (
    DEVICE_AUTH_URL,
    DEVICE_CLIENT_ID,
    DEVICE_FLOW_USER_AGENT,
    DEVICE_RESOLVE_URL,
    DEVICE_SCOPE,
    DEVICE_TOKEN_URL,
)

logger = logging.getLogger(__name__)


class SpotifyDeviceFlow:
    def __init__(self, sp_dc: str) -> None:
        self.client = httpx.AsyncClient()
        self.client.cookies.set("sp_dc", sp_dc, domain=".spotify.com")

    async def get_token(self) -> dict:
        """Get access token via device flow."""
        auth_data = await self._initiate_device_authorization()
        device_code = auth_data["device_code"]
        user_code = auth_data["user_code"]
        verification_url = auth_data["verification_uri_complete"]
        flow_ctx, csrf_token = await self._parse_verification_page(verification_url)
        await self._submit_user_code(user_code, flow_ctx, csrf_token, verification_url)
        token_data = await self._exchange_device_code(device_code)

        logger.debug(f"Obtained device flow token data: {token_data}")

        return token_data

    async def _initiate_device_authorization(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEVICE_AUTH_URL,
                data={
                    "client_id": DEVICE_CLIENT_ID,
                    "scope": DEVICE_SCOPE,
                },
                headers={
                    "User-Agent": DEVICE_FLOW_USER_AGENT,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            response.raise_for_status()
            return response.json()

    async def _parse_verification_page(self, verification_url: str) -> tuple[str, str]:
        response = await self.client.get(verification_url, follow_redirects=True)

        try:
            flow_ctx_full = parse_qs(response.url.query.decode())["flow_ctx"][0]
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

    async def _submit_user_code(
        self,
        user_code: str,
        flow_ctx: str,
        csrf_token: str,
        referer_url: str,
    ) -> None:
        current_ts = int(time.time())
        response = await self.client.post(
            DEVICE_RESOLVE_URL,
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
        try:
            submit_result = response.json()
            assert submit_result.get("result") == "ok"
        except (json.JSONDecodeError, AssertionError):
            raise ValueError("Failed to submit user code")

    async def _exchange_device_code(self, device_code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEVICE_TOKEN_URL,
                data={
                    "client_id": DEVICE_CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                headers={
                    "User-Agent": DEVICE_FLOW_USER_AGENT,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
        response.raise_for_status()
        return response.json()
