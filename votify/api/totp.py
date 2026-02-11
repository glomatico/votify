import hashlib
import hmac
import logging
from typing import Collection

import httpx

from ..utils import safe_json
from .constants import TOTP_DIGITS, TOTP_PERIOD, TOTP_SECRETS_URL
from .exceptions import VotifyRequestException

logger = logging.getLogger(__name__)


class Totp:
    def __init__(
        self,
        version: str,
        secret: bytes,
    ) -> None:
        self.version = version
        self.secret = secret

    @classmethod
    async def initialize(cls) -> "Totp":
        async with httpx.AsyncClient() as client:
            response = await client.get(TOTP_SECRETS_URL)
        secrets = safe_json(response)
        if response.status_code != 200 or not secrets:
            raise VotifyRequestException(
                name="TOTP secrets",
                response_status_code=response.status_code,
                response_text=response.text,
            )

        logger.debug(f"Received TOTP secrets: {secrets}")

        version = max(secrets.keys(), key=int)

        return cls(
            version=version,
            secret=cls.derive(secrets[version]),
        )

    @staticmethod
    def derive(ciphertext: Collection[int]) -> bytes:
        return "".join(
            str(byte ^ ((i % 33) + 9)) for i, byte in enumerate(ciphertext)
        ).encode("ascii")

    def generate(self, timestamp: int) -> str:
        counter = int(timestamp) // 1000 // TOTP_PERIOD
        counter_bytes = counter.to_bytes(8, "big")

        h = hmac.new(self.secret, counter_bytes, hashlib.sha1)
        hmac_result = h.digest()

        offset = hmac_result[-1] & 0x0F
        binary = (
            (hmac_result[offset] & 0x7F) << 24
            | (hmac_result[offset + 1] & 0xFF) << 16
            | (hmac_result[offset + 2] & 0xFF) << 8
            | (hmac_result[offset + 3] & 0xFF)
        )
        result = str(binary % (10**TOTP_DIGITS)).zfill(TOTP_DIGITS)

        logger.debug(f"Generated TOTP code: {result}")

        return result
