#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/samparker/QCHD Wishlist App"
APP_DIR="$PROJECT_DIR/backend"
cd "$APP_DIR"

# Rebuild UI if npm is available (optional — skip when running under launchd)
if command -v npm >/dev/null 2>&1 && [ -d "$PROJECT_DIR/frontend/node_modules" ]; then
  (cd "$PROJECT_DIR/frontend" && npm run build --silent) || true
fi

# Do NOT `source .env` here — passwords with spaces break bash.
# Python loads backend/.env via python-dotenv in app/main.py.

exec "$APP_DIR/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000
