import sys
sys.path.append("/app/src")
from src.totp_utils import generate_totp_code, verify_totp_code
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
app = FastAPI()

DATA_PATH = "/data"
SEED_FILE = f"{DATA_PATH}/seed.txt"

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

@app.post("/decrypt-seed")
def decrypt_seed_api(req: DecryptRequest):
    try:
        os.makedirs(DATA_PATH, exist_ok=True)

        with open("student_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        encrypted_bytes = base64.b64decode(req.encrypted_seed)

        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        hex_seed = decrypted.decode()

        if len(hex_seed) != 64:
            raise ValueError("Invalid seed length")

        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}
    except Exception:
        raise HTTPException(500, detail="Decryption failed")

@app.get("/generate-2fa")
def generate_2fa():
    try:
        if not os.path.exists(SEED_FILE):
            raise FileNotFoundError

        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)

        import time
        valid_for = 30 - (int(time.time()) % 30)

        return {"code": code, "valid_for": valid_for}
    except FileNotFoundError:
        raise HTTPException(500, detail="Seed not decrypted yet")
    except Exception:
        raise HTTPException(500, detail="Unexpected error")

@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(400, detail="Missing code")

    try:
        if not os.path.exists(SEED_FILE):
            raise FileNotFoundError

        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        is_valid = verify_totp_code(hex_seed, req.code)

        return {"valid": is_valid}
    except FileNotFoundError:
        raise HTTPException(500, detail="Seed not decrypted yet")
    except Exception:
        raise HTTPException(500, detail="Unexpected error")

