#!/bin/sh
set -eu

: "${DB_HOST:?DB_HOST is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${SECRET_KEY:?SECRET_KEY is required}"

export DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"

python - <<'PY'
import os
import socket
import sys
import time

host = os.environ["DB_HOST"]
port = 5432
for attempt in range(30):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"PostgreSQL reachable at {host}:{port}")
            break
    except OSError as exc:
        print(f"Waiting for PostgreSQL ({attempt + 1}/30): {exc}", flush=True)
        time.sleep(2)
else:
    print("PostgreSQL did not become reachable", file=sys.stderr)
    sys.exit(1)
PY

alembic upgrade head

if [ "${UVICORN_RELOAD:-false}" = "true" ]; then
    exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/src
fi

exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
