import hashlib
import hmac
import math
import requests
import json
from typing import Tuple

# thanks to https://github.com/glomatico/votify/pull/42#issuecomment-2727036757
class TOTP:
    def __init__(self) -> None:
        # dumped directly from the object, after all decryptions
        self.secret = b'6934698199123836152873265447694113111117791033370'
        self.version = 24
        self.period = 30
        self.digits = 6
        self.short_code = "000000"
        
    def transform_secret(self, original_secret: str) -> str:
        if not isinstance(original_secret, str):
            return ""
        ascii_codes = [ord(c) for c in original_secret]
        transformed = [val ^ ((i % 33) + 9) for i, val in enumerate(ascii_codes)]
        joined_decimal = "".join(str(num) for num in transformed)
        self.secret = joined_decimal.encode()
        return joined_decimal
    
    def update_key(self) -> Tuple[str, int]:
        response = requests.get("https://github.com/Thereallo1026/spotify-secrets/raw/refs/heads/main/secrets/secrets.json")
        keys = response.json()
        # for example, `[{'version': 22, 'secret': 'cew{Ex[{aJ50Lf7En6'}, {'version': 23, 'secret': "0'Ep-k`^9(3zb|weR"}, {'version': 24, 'secret': 'L(N]nu\\-%E3U9ZIivoT{<X'}]`
        # get the key with the highest version
        latest_secret_data = max(keys, key=lambda x: x.get('version', -1))
        key_string = latest_secret_data.get('secret')
        key_version = latest_secret_data.get('version')
        self.version = key_version
        return key_string, key_version

    def get_latest_key_and_version(self, timestamp: int) -> Tuple[str, int]:
        key_string, key_version = self.update_key()
        transformed_key = self.transform_secret(key_string)
        new_totp = self.generate(timestamp=timestamp, secret=transformed_key.encode())
        return new_totp, key_version
    
    def generate(self, timestamp: int, secret: bytes=b''):
        if secret == b'':
            secret = self.secret
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
        self.short_code = str(binary % (10**self.digits)).zfill(self.digits)
        return self.short_code
