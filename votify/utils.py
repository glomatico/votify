from __future__ import annotations

import hmac
import hashlib
import requests
import struct


def check_response(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.HTTPError:
        _raise_response_exception(response)


def _raise_response_exception(response: requests.Response):
    raise Exception(
        f"Request failed with status code {response.status_code}: {response.text}"
    )


def generate_secret_key(arr: list):
    """
    I'd prefer to keep these close to the original code, so
    we can debug if/when spotify changes their code. Logic obtained from:
    https://open.spotifycdn.com/cdn/build/web-player/web-player.<HASH>.js
    """
    def Ee(e):
        """
        Convert hex string to bytes
        Original code:
        Ee = e => {
            e = e.replace(/ /g, "");
            const t = new ArrayBuffer(e.length / 2)
            , n = new Uint8Array(t);
            for (let r = 0; r < e.length; r += 2)
                n[r / 2] = parseInt(e.substring(r, r + 2), 16);
            return n
        }
        """
        e = e.replace(" ", "")
        n = [0] * (len(e) // 2)
        for r in range(0, len(e), 2):
            n[r // 2] = int(e[r:r + 2], 16)
        return n

    class xe:
        def __init__(self, options):
            self.buffer = options.get('buffer')
        
        @classmethod
        def fromHex(cls, e):
            return cls({
                'buffer': Ee(e)
            })

        def __repr__(self):
            return f'xe(buffer={self.buffer})'

    class Ne:
        @staticmethod
        def _from(e, t = 'utf-8'):
            '''
            e is the buffer 
            t is utf8
            '''
            if type(e) == str:
                return [ord(char) for char in e]
            raise NotImplementedError

    def Pe(e):
        '''
        Obfuscate the secret key - this could change in the future
        Original code:
        function Pe(e) {
            const t = e.map(( (e, t) => e ^ t % 33 + 9))
                , n = Ne.from(t.join(""), "utf8").toString("hex"); // [Calculating n]
            return xe.fromHex(n) // [Calculating xe.fromHex(n)]
        }
        '''
        t = [element ^ (idx % 33 + 9) for idx, element in enumerate(e)]
        
        n = Ne._from(''.join(map(str, t)), 'utf-8')
        n = bytes(n).hex()
        
        return xe.fromHex(n)

    return Pe(arr).buffer
        

def generate_totp(secret_bytes, timestamp, digits=6, period=30):
    """
    Generate TOTP code using Python's standard crypto libraries
    
    Args:
        secret_bytes: Byte array containing the secret key
        digits: Number of digits in the output (typically 6 or 8)
        period: Time step in seconds (typically 30)
        timestamp: Optional timestamp (in milliseconds), defaults to current time
    """
    if timestamp is None:
        raise ValueError("Timestamp is required")
    
    counter = int(timestamp // 1000 // period)
    
    # Convert counter to 8-byte big-endian format
    counter_bytes = struct.pack('>Q', counter)
    
    # Create HMAC-SHA1
    hmac_result = hmac.new(bytes(secret_bytes), counter_bytes, hashlib.sha1).digest()
    # print({str(i): hmac_result[i] for i in range(len(hmac_result))})
    
    # Dynamic truncation
    # Original Code:
    # o = 15 & i[i.byteLength - 1];
    # return (((127 & i[o]) << 24 | (255 & i[o + 1]) << 16 | (255 & i[o + 2]) << 8 | 255 & i[o + 3]) % 10 ** n).toString().padStart(n, "0")
    offset = hmac_result[-1] & 0xF
    binary = ((hmac_result[offset] & 0x7F) << 24 |
              (hmac_result[offset + 1] & 0xFF) << 16 |
              (hmac_result[offset + 2] & 0xFF) << 8 |
              (hmac_result[offset + 3] & 0xFF))
    
    # Generate the OTP value
    otp = binary % (10 ** digits)
    
    # Ensure proper padding with leading zeros
    return f'{otp:0{digits}d}'


def create_totp(timestamp, 
                secret = [12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54], 
                digits = 6, 
                period = 30):
    """
    secret was taken from the web-player.<HASH>.js file
    from this line:
    De = {
                period: 30,
                digits: 6,
                algorithm: "SHA1",
                secret: Pe([12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54])
    }
    """
    secret_key = bytes(generate_secret_key(secret))
    return generate_totp(secret_key, timestamp, digits, period)
    