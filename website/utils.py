# utils.py

import hmac
import hashlib
import base64

def generate_esewa_signature(message: str, secret_key: str = "8gBm/:&EnhH.1/q") -> str:
    secret_key_bytes = secret_key.encode('utf-8')
    message_bytes = message.encode('utf-8')

    hmac_sha256 = hmac.new(secret_key_bytes, message_bytes, hashlib.sha256)
    digest = hmac_sha256.digest()
    return base64.b64encode(digest).decode('utf-8')
