import hashlib
import hmac
import math

# thanks to https://github.com/glomatico/votify/pull/42#issuecomment-2727036757
class TOTP:
    def __init__(self) -> None:
        # dumped directly from the object, after all decryptions
        self.secret = b"10239356982684469120121471223494829410773366870"
        self.version = 11
        self.period = 30
        self.digits = 6

    def generate(self, timestamp: int) -> str:
        counter = math.floor(timestamp / 1000 / self.period)
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

        return str(binary % (10**self.digits)).zfill(self.digits)
