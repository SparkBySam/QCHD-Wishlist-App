# Bike Wishlist Tracker

Full-stack dealership tool that scrapes motorcycle inventory, matches it against
customer wishlists, and alerts staff when a bike hits the lot.

Built for **Queen City Harley-Davidson** floor use. Runs locally on a Mac;
staff open a browser to `http://localhost:8000`.

> **Security:** This app has **no login**. Keep it on localhost. See [SECURITY.md](SECURITY.md).
> Never commit `backend/.env` or `backend/wishlist.db` (customer PII + email credentials).

## Stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, SQLite, APScheduler |
| Scraper | Selenium + BeautifulSoup (Chrome headless) |
| Frontend | React (Vite), custom design system |
| Ops | macOS `launchd` background service |
| Alerts | Gmail SMTP (optional Twilio SMS) |

## Features

- **Dashboard** — Active inventory, new/used filter, scrape status, in-app notifications
- **Wishlist** — Multi-model entries, year range, color, new/used preference, notes
- **Matches** — Unhandled-first queue, phone copy, mark notified / not interested, CSV export
- **Matching** — Runs after scrapes and on wishlist create/update (model, year, color, condition)
- **Email digests** — One email per match, or one digest when several land at once
- **Auto-scrape** — Checks every 30 minutes whether a scrape is due (recovers after Mac sleep)

## Project structure

```
backend/
  app/
    main.py              # FastAPI entrypoint
    database.py          # SQLite + migrations
    models.py            # Inventory, wishlist, matches, notifications
    scheduler.py         # Due-scrape polling + cleanup jobs
    scraper/scraper.py   # Dealership inventory scraper
    services/            # Sync, matching, alerts, notifications
    routes/              # REST APIs
  .env.example           # Template only — copy to .env locally
frontend/
  src/
    views/               # Dashboard, Wishlist, Matches
    ds/                  # Design-system tokens + components
scripts/
  start-backend.sh       # launchd entry (binds 127.0.0.1)
  install-macos-service.sh
  com.qchd.wishlist.plist
HOW_TO_USE.md            # Day-to-day operator guide
SECURITY.md              # Public-repo security notes
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Chrome (or Chromium) for the scraper

## Quick start (development)

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env with real SMTP values if you want email
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
# Frontend (second terminal) — hot reload while coding
cd frontend
npm install
npm run dev
```

- App (Vite): http://localhost:5173  
- API: http://localhost:8000  
- API docs (only if `ENABLE_API_DOCS=true` in `.env`): http://localhost:8000/docs  

For day-to-day dealership use (single URL, no Terminal), see [HOW_TO_USE.md](HOW_TO_USE.md).

## Environment variables

Copy `backend/.env.example` → `backend/.env`. **Do not commit `.env`.**

| Variable | Default | Description |
|---|---|---|
| `SCRAPE_INTERVAL_HOURS` | `6` | How often inventory should be refreshed |
| `SCRAPE_CHECK_INTERVAL_MINUTES` | `30` | How often to check if a scrape is due |
| `HANDLED_MATCH_RETENTION_DAYS` | `7` | Auto-delete handled matches after N days |
| `ENABLE_API_DOCS` | `false` | Set `true` to enable `/docs` and `/openapi.json` |
| `SMTP_*`, `ALERT_EMAIL_TO` | — | Gmail App Password recommended for alerts |
| `TWILIO_*`, `ALERT_SMS_TO` | — | Optional SMS alerts |

## How it works

1. **Scrape** — Manual **Scrape Now**, or automatic when inventory is older than the interval.
2. **Inventory sync** — Insert new stock #s; mark missing ones inactive; store new/used (incl. Certified Pre-Owned → used).
3. **Matching** — Model codes/names (strict token rules), year range, optional color, optional new/used.
4. **Alerts** — In-app notifications + optional email/SMS.
5. **Follow-up** — Matches tab for contact, notify/dismiss, CSV export.

## Run as a background service (macOS)

```bash
chmod +x scripts/install-macos-service.sh
./scripts/install-macos-service.sh
```

Then open **http://localhost:8000**.

Restart after `.env` changes:

```bash
launchctl kickstart -k gui/$(id -u)/com.qchd.wishlist
```

Logs: `backend/logs/stdout.log`, `backend/logs/stderr.log`

The service script binds **`127.0.0.1` only**. Do not change that without adding auth.

## API overview

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Liveness |
| `GET` | `/api/inventory` | List inventory (`search`, `condition`) |
| `POST` | `/api/inventory/scrape` | Start background scrape |
| `GET` | `/api/inventory/scrape/status` | Status / last run / next due |
| `POST` | `/api/inventory/alerts/test` | Send a test email |
| `GET` | `/api/wishlist` | List wishlist |
| `POST` / `PUT` | `/api/wishlist` | Create / update (+ immediate match) |
| `GET` | `/api/matches` | List matches |
| `POST` | `/api/matches/{id}/dismiss` | Not interested (no rematch) |
| `GET` | `/api/matches/export` | CSV export |

## Smoke test

1. Start the backend (and frontend if developing).
2. **Scrape Now** on the Dashboard; wait for the success banner.
3. Add a wishlist entry (e.g. model `Fat Boy`, years `2024–2026`).
4. Confirm any immediate matches on the Matches tab and (if SMTP is set) in email.

## License / disclaimer

Unofficial dealership utility. Not affiliated with or endorsed by Harley-Davidson
Motor Company. Scrapes a public dealership inventory site for internal matching
only—respect the site’s terms and use responsibly.
