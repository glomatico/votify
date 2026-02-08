import hashlib
import hmac

from typing import Collection


class TOTP:
    PERIOD = 30
    DIGITS = 6

    def __init__(self, *, version: int, ciphertext: Collection[int]) -> None:
        self.version = version
        self.secret = self.derive(ciphertext)

    @staticmethod
    def derive(ciphertext: Collection[int]) -> bytes:
        return "".join(
            str(byte ^ ((i % 33) + 9)) for i, byte in enumerate(ciphertext)
        ).encode("ascii")

    def generate(self, timestamp: int) -> str:
        counter = int(timestamp) // 1000 // self.PERIOD
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

        return str(binary % (10**self.DIGITS)).zfill(self.DIGITS)
