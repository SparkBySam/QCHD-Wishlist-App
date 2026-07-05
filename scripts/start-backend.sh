#!/bin/bash
set -euo pipefail

APP_DIR="/Users/samparker/QCHD Wishlist App/backend"
cd "$APP_DIR"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

exec "$APP_DIR/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000
