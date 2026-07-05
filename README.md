# Bike Wishlist Tracker

Full-stack app that scrapes dealership motorcycle inventory, stores customer wishlists, and notifies you when a bike matches what someone is looking for.

- **Backend:** Python, FastAPI, SQLAlchemy (SQLite), APScheduler
- **Frontend:** React (Vite), plain CSS

## Project structure

```
backend/
  app/
    main.py              # FastAPI app entrypoint
    database.py          # SQLite + SQLAlchemy setup
    models.py            # InventoryItem, WishlistEntry, Match, Notification, AppState
    schemas.py           # Pydantic request/response models
    scheduler.py         # Periodic scrape job
    scraper/scraper.py   # Queen City Harley inventory scraper
    services/            # inventory sync, matching, alerts, notifications
    routes/              # inventory, wishlist, matches APIs
  .env.example           # optional email/SMS alert config
frontend/
  src/
    views/               # Dashboard, Wishlist, Matches
scripts/
  start-backend.sh       # launchd helper script
  com.qchd.wishlist.plist
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Chrome (or Chromium) — required for the inventory scraper

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in what you need.

| Variable | Default | Description |
|---|---|---|
| `SCRAPE_INTERVAL_HOURS` | `6` | Hours between automatic scrapes |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `ALERT_EMAIL_TO` | — | Email alerts on new matches |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `ALERT_SMS_TO` | — | SMS alerts via Twilio |

Example:

```bash
SCRAPE_INTERVAL_HOURS=2 uvicorn app.main:app --reload --port 8000
```

## Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

App UI: [http://localhost:5173](http://localhost:5173)

## Scraper

Inventory is pulled from [Queen City Harley](https://www.queencityharley.com) via Selenium + BeautifulSoup (`backend/app/scraper/scraper.py`), adapted from your PhotoGetApp script.

- Scrapes **full active inventory** (not only bikes missing photos)
- Skips sale-pending / sold listings
- Chrome required; Selenium Manager resolves ChromeDriver

## How it works

1. **Scrape** — Manual via **Scrape Now** (runs in background, 2–5 min), or automatically on the APScheduler interval.
2. **Inventory sync** — New stock numbers inserted; missing ones marked inactive.
3. **Matching** — Runs after scrapes **and** when wishlist entries are created/updated:
   - Model: normalized Harley names, token match, model codes (`FLFB`, `Street Glide`, `Fat Boy`, etc.)
   - Year: within min/max range
   - Color: optional substring match
4. **Notifications** — In-app banner + optional email/SMS when env vars are configured.
5. **Matches view** — Click a row for customer contact details; export CSV for follow-up.

## Run as a background service (macOS)

```bash
# Edit scripts/com.qchd.wishlist.plist if your project path differs
mkdir -p backend/logs
cp scripts/com.qchd.wishlist.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.qchd.wishlist.plist
```

Stop/unload:

```bash
launchctl unload ~/Library/LaunchAgents/com.qchd.wishlist.plist
```

Logs: `backend/logs/stdout.log` and `backend/logs/stderr.log`

## API overview

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/inventory?search=` | List inventory |
| `POST` | `/api/inventory/scrape` | Start background scrape |
| `GET` | `/api/inventory/scrape/status` | Scrape progress / last run |
| `GET` | `/api/inventory/alerts/config` | Which external alerts are enabled |
| `GET` | `/api/inventory/notifications` | In-app notifications |
| `GET` | `/api/wishlist?search=&status=` | List wishlist |
| `POST` | `/api/wishlist` | Create entry (+ immediate matching) |
| `PUT` | `/api/wishlist/{id}` | Update entry (+ immediate matching) |
| `GET` | `/api/matches?search=&unhandled_only=` | List matches |
| `GET` | `/api/matches/export` | Download matches CSV |
| `PATCH` | `/api/matches/{id}/notified` | Mark handled |

## Quick smoke test

1. Start backend and frontend.
2. Run a scrape from the Dashboard (wait for completion banner).
3. Add a wishlist entry for `Fat Boy`, years `2024–2026`.
4. If one is on the lot, you'll see an immediate match message and a hit on the Matches tab.
