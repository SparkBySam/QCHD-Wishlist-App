# Security Policy

## Intended use

This project is a **local dealership tool**. It is designed to run on a trusted
Mac bound to **localhost only** (`127.0.0.1`).

The API has **no authentication**. Anyone who can reach it can:

- Read and export customer names, phones, and emails
- Create, edit, or delete wishlist entries
- Trigger inventory scrapes
- Mark or dismiss matches

Do **not** bind the server to `0.0.0.0`, put it behind a public URL, or deploy
it to a shared host without adding authentication first.

## Secrets and private data

Never commit:

| Path | Why |
|---|---|
| `backend/.env` | SMTP / Twilio credentials |
| `backend/wishlist.db` | Real customer PII |
| `backend/logs/` | May contain operational details |

Use `backend/.env.example` as a template. Copy it to `backend/.env` locally and
fill in real values there only.

If a secret was ever committed or shared, **rotate it immediately** (for Gmail,
revoke the App Password and create a new one).

## Safe defaults in this repo

- Production start script binds **`127.0.0.1:8000`**
- CORS allowlist is limited to localhost origins
- OpenAPI docs (`/docs`, `/redoc`, `/openapi.json`) are **off by default**;
  enable locally with `ENABLE_API_DOCS=true` in `backend/.env`
- `.gitignore` excludes `.env`, SQLite DBs, and logs

## Reporting a vulnerability

If you find a security issue in this repository, please open a private report
with the repo owner (GitHub Security Advisory if available, or contact the
maintainer directly) rather than filing a public issue with exploit details.
