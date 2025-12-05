import base64
import re
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed():
    # 1. Load private key from /app/
    with open("/app/student_private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # 2. Read encrypted seed (already copied into container)
    with open("/app/encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()

    # 3. Base64 decode
    encrypted_seed = base64.b64decode(encrypted_seed_b64)

    # 4. RSA OAEP SHA-256 decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_seed,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 5. Convert bytes → UTF-8 string
    decrypted_seed = decrypted_bytes.decode()

    # 6. Validate seed format
    if len(decrypted_seed) != 64:
        raise ValueError("Invalid seed: length is not 64 chars")

    if not re.fullmatch(r"[0-9a-f]{64}", decrypted_seed):
        raise ValueError("Invalid seed: contains non-hex characters")

    # 7. Save decrypted seed to persistent storage
    with open("/data/seed.txt", "w") as f:
        f.write(decrypted_seed)

    print("Seed decrypted successfully!")
    print("Saved to /data/seed.txt")


if __name__ == "__main__":
    decrypt_seed()

