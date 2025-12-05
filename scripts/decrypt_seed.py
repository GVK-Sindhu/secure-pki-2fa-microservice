import base64
import re
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed():
    # 1. Load private key
    with open("student_private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # 2. Read encrypted seed
    with open("encrypted_seed.txt", "r") as f:
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

    # 5. Convert to UTF-8 string
    decrypted_seed = decrypted_bytes.decode()

    # 6. Validation: must be 64-char hex string
    if len(decrypted_seed) != 64:
        raise ValueError("Invalid seed: length is not 64 chars")

    if not re.fullmatch(r"[0-9a-f]{64}", decrypted_seed):
        raise ValueError("Invalid seed: contains non-hex characters")

    # 7. Save decrypted seed
    with open("decrypted_seed.txt", "w") as f:
        f.write(decrypted_seed)

    print("Seed decrypted successfully!")
    print("Saved to decrypted_seed.txt")


if __name__ == "__main__":
    decrypt_seed()
