import hmac
import base64
import time
import hashlib

def generate_totp_code(hex_seed, digits=6, interval=30, timestep=None):
    seed = bytes.fromhex(hex_seed)

    # Allow external timestep override for verification
    if timestep is None:
        timestep = int(time.time()) // interval

    # Convert timestep → 8 bytes
    msg = timestep.to_bytes(8, "big")

    # HMAC-SHA1 digest
    h = hmac.new(seed, msg, hashlib.sha1).digest()

    # Dynamic truncation
    offset = h[-1] & 0x0F
    binary = (
        ((h[offset] & 0x7F) << 24)
        | ((h[offset + 1] & 0xFF) << 16)
        | ((h[offset + 2] & 0xFF) << 8)
        | (h[offset + 3] & 0xFF)
    )

    return str(binary % (10 ** digits)).zfill(digits)


def verify_totp_code(hex_seed, code, window=1, interval=30):
    now = int(time.time()) // interval

    # Check previous, current, next windows
    for offset in range(-window, window + 1):
        ts = now + offset
        if generate_totp_code(hex_seed, interval=interval, timestep=ts) == code:
            return True

    return False
