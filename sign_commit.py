from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import subprocess
import base64

# Load student private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

# Get latest commit hash
commit_hash = subprocess.check_output(["git", "log", "-1", "--format=%H"]).decode().strip()

# Sign commit hash
signature = private_key.sign(
    commit_hash.encode('utf-8'),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Load instructor public key
with open("instructor_public.pem", "rb") as f:
    instructor_public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

# Encrypt signature with instructor public key
encrypted_signature = instructor_public_key.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Base64 encode encrypted signature
b64_signature = base64.b64encode(encrypted_signature).decode()
print("Commit Hash:", commit_hash)
print("Encrypted Signature:", b64_signature)
