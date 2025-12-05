import base64
import binascii
import pyotp

def hex_to_base32(hex_seed: str) -> str:
    # 1. Hex → bytes
    seed_bytes = binascii.unhexlify(hex_seed)

    # 2. bytes → base32 encoded string
    base32_seed = base64.b32encode(seed_bytes).decode().replace("=", "")
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    base32_seed = hex_to_base32(hex_seed)

    # 3. Create TOTP object (SHA-1, 30s, 6 digits default)
    totp = pyotp.TOTP(base32_seed)

    # 4. Generate current TOTP code
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)

    # 5. Verify with ±30s tolerance
    return totp.verify(code, valid_window=valid_window)
