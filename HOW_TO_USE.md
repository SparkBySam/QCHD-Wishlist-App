# How to Run & Use — Bike Wishlist Tracker

This tool is for **local use on a trusted Mac**. It has no login and stores
customer contact info in a local SQLite database. Keep it on `localhost`
(see [SECURITY.md](SECURITY.md)). Never commit `backend/.env` or `backend/wishlist.db`.

## Option A: Run in background (recommended — no daily Terminal)

One-time setup:

```bash
chmod +x "/Users/samparker/QCHD Wishlist App/scripts/install-macos-service.sh"
"/Users/samparker/QCHD Wishlist App/scripts/install-macos-service.sh"
```

Then open **http://localhost:8000** in your browser anytime.

The app starts automatically when you log in to your Mac. No Terminal needed.

**Logs:** `backend/logs/stdout.log` and `backend/logs/stderr.log`

**Restart after config changes:**
```bash
launchctl kickstart -k gui/$(id -u)/com.qchd.wishlist
```

**Stop the background service:**
```bash
launchctl bootout gui/$(id -u)/com.qchd.wishlist
```

---

## Option B: Run manually (development)

**Terminal 1 — backend:**
```bash
cd "/Users/samparker/QCHD Wishlist App/backend"
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend (hot reload while editing):**
```bash
cd "/Users/samparker/QCHD Wishlist App/frontend"
npm run dev
```

Open **http://localhost:5173**

---

## Email alerts on match

1. Copy the example config:
   ```bash
   cp "/Users/samparker/QCHD Wishlist App/backend/.env.example" \
      "/Users/samparker/QCHD Wishlist App/backend/.env"
   ```

2. Edit `backend/.env` with your email settings.

   **Gmail:** use an [App Password](https://myaccount.google.com/apppasswords), not your normal password.

   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=you@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   SMTP_FROM=you@gmail.com
   ALERT_EMAIL_TO=you@gmail.com
   ```

3. Restart the backend (or kickstart the launchd service).

4. Test it:
   ```bash
   curl -X POST http://localhost:8000/api/inventory/alerts/test
   ```

You'll get an email on every **new** match (not duplicates for the same customer + bike).

---

## Multiple models per customer

In the **Wishlist** tab, the **Desired model(s)** field accepts more than one model.

Separate with commas or put one per line:

```
Fat Boy
Street Glide
FLHX
```

or

```
Fat Boy, Street Glide, Heritage Classic
```

One customer entry can match **any** of those models against current inventory.

---

## Daily use (3 tabs)

### Dashboard
- View active inventory
- **Scrape Now** — pulls fresh bikes from queencityharley.com (2–5 min)
- Match notifications appear here

### Wishlist
- Add customers and what they're looking for
- Matches run **immediately** against bikes already on the lot
- Mark **Fulfill** when the customer buys

### Matches
- All hits between wishlist and inventory
- Click a row for contact info
- **Mark notified** after you've reached out
- **Export CSV** for follow-up

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 8000 in use | `lsof -i :8000` then `kill <PID>` |
| Scrape fails | Install Google Chrome |
| No emails | Check `.env`, test with curl command above |
| Page won't load | Service may be stopped — re-run install script |
