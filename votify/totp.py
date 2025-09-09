from __future__ import annotations

import hashlib
import hmac
import math
import requests


# thanks to https://github.com/glomatico/votify/pull/42#issuecomment-2727036757
class TOTP:
    SPOTIFY_SECRETS_JSON = "https://raw.githubusercontent.com/Thereallo1026/spotify-secrets/refs/heads/main/secrets/secretDict.json"
    PERIOD = 30
    DIGITS = 6

    def __init__(self) -> None:
        self._setup()

    def _setup(self) -> None:
        version, secret_cipher_bytes = self.get_latest_secret()
        self.version = version
        self.secret = self.derive_secret_number(secret_cipher_bytes).encode()

    def derive_secret_number(self, secret_cipher_bytes: list[int]) -> str:
        transformed = [
            byte ^ ((i % 33) + 9) for i, byte in enumerate(secret_cipher_bytes)
        ]
        return "".join(str(n) for n in transformed)

    def get_latest_secret(self) -> tuple[int, list[int]]:
        response = requests.get(self.SPOTIFY_SECRETS_JSON)
        response.raise_for_status()
        secrets = response.json()
        latest_version = max(int(v) for v in secrets.keys())
        return latest_version, secrets[str(latest_version)]

    def generate(self, timestamp: int) -> str:
        counter = math.floor(timestamp / 1000 / self.PERIOD)
        counter_bytes = counter.to_bytes(8, byteorder="big")

        h = hmac.new(self.secret, counter_bytes, hashlib.sha1)
        hmac_result = h.digest()

        offset = hmac_result[-1] & 0x0F
        binary = (
            (hmac_result[offset] & 0x7F) << 24
            | (hmac_result[offset + 1] & 0xFF) << 16
            | (hmac_result[offset + 2] & 0xFF) << 8
            | (hmac_result[offset + 3] & 0xFF)
        )

        return str(binary % (10**self.DIGITS)).zfill(self.DIGITS)
