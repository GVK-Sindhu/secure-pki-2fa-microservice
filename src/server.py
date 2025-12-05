import sys
sys.path.append("/app/scripts")

from flask import Flask, request, jsonify
from scripts import totp_utils
from scripts import decrypt_seed

app = Flask(__name__)

@app.get("/")
def home():
    return {"message": "Server running!"}

@app.post("/decrypt-seed")
def decrypt_seed_route():
    try:
        # Decrypt and write to /data/seed.txt
        decrypt_seed.decrypt_seed()

        # Read the decrypted seed
        with open("/data/seed.txt", "r") as f:
            seed = f.read().strip()

        return jsonify({"seed": seed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/generate-2fa")
def generate_2fa():
    try:
        # Read seed from persistent storage
        with open("/data/seed.txt", "r") as f:
            hex_seed = f.read().strip()

        code = totp_utils.generate_totp_code(hex_seed)
        return jsonify({"code": code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/verify-2fa")
def verify_2fa():
    try:
        data = request.get_json()
        code = data.get("code")

        if not code:
            return jsonify({"error": "No code provided"}), 400

        # Read from /data/seed.txt 
        with open("/data/seed.txt", "r") as f:
            hex_seed = f.read().strip()

        valid = totp_utils.verify_totp_code(hex_seed, code)
        return jsonify({"valid": valid})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

