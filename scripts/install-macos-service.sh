#!/bin/bash
# One-time setup: build the UI and install the background service on macOS.
set -euo pipefail

PROJECT_DIR="/Users/samparker/QCHD Wishlist App"
PLIST_NAME="com.qchd.wishlist.plist"
PLIST_SRC="$PROJECT_DIR/scripts/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "==> Building frontend..."
cd "$PROJECT_DIR/frontend"
npm install
npm run build

echo "==> Ensuring backend venv..."
cd "$PROJECT_DIR/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
  pip install -r requirements.txt
fi

mkdir -p "$PROJECT_DIR/backend/logs"

if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
  cp "$PROJECT_DIR/backend/.env.example" "$PROJECT_DIR/backend/.env"
  echo ""
  echo "Created backend/.env — edit it to add your email alert settings."
fi

echo "==> Installing launchd service..."
cp "$PLIST_SRC" "$PLIST_DEST"
launchctl bootout "gui/$(id -u)/$PLIST_NAME" 2>/dev/null || launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST" 2>/dev/null || launchctl load "$PLIST_DEST"

echo ""
echo "Done! The app runs in the background and starts on login."
echo ""
echo "  Open:  http://localhost:8000"
echo "  Logs:  $PROJECT_DIR/backend/logs/"
echo ""
echo "Next: edit $PROJECT_DIR/backend/.env for email alerts, then restart:"
echo "  launchctl kickstart -k gui/$(id -u)/$PLIST_NAME"
