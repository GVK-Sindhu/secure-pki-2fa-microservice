#!/usr/bin/env bash
set -e

echo "[entrypoint] starting container..."

if [ -n "$ENCRYPTED_SEED" ] && [ ! -f /app/encrypted_seed.txt ]; then
  echo "[entrypoint] writing encrypted_seed.txt from ENCRYPTED_SEED env var"
  printf "%s" "$ENCRYPTED_SEED" > /app/encrypted_seed.txt
  chmod 0644 /app/encrypted_seed.txt
fi

if [ ! -f /app/encrypted_seed.txt ]; then
  echo "[entrypoint] WARNING: /app/encrypted_seed.txt not found."
else
  echo "[entrypoint] found /app/encrypted_seed.txt"
fi

service cron start 2>/dev/null || true

echo "[entrypoint] starting uvicorn..."
exec uvicorn src.api:app --host 0.0.0.0 --port 8080
