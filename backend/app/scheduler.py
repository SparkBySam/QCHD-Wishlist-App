import logging
import os
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from app.database import SessionLocal
from app.services.app_state_service import get_or_create_state, utcnow
from app.services.match_cleanup_service import purge_expired_handled_matches
from app.services.scrape_service import run_scrape_and_match

logger = logging.getLogger(__name__)

# How often inventory should be refreshed.
SCRAPE_INTERVAL_HOURS = float(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
# How often to check whether a scrape is due (handles Mac sleep/wake).
SCRAPE_CHECK_INTERVAL_MINUTES = int(os.getenv("SCRAPE_CHECK_INTERVAL_MINUTES", "30"))
HANDLED_MATCH_CLEANUP_HOURS = float(os.getenv("HANDLED_MATCH_CLEANUP_HOURS", "24"))

scheduler = BackgroundScheduler()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def scrape_is_stale(db) -> bool:
    """True if inventory has never been scraped or is older than the interval."""
    state = get_or_create_state(db)
    if state.last_scrape_at is None:
        return True
    age = datetime.now(timezone.utc) - _as_utc(state.last_scrape_at)
    return age >= timedelta(hours=SCRAPE_INTERVAL_HOURS)


def next_scrape_due_at(db) -> datetime | None:
    """When the next automatic scrape should run, based on last_scrape_at."""
    state = get_or_create_state(db)
    if state.last_scrape_at is None:
        return datetime.now(timezone.utc)
    return _as_utc(state.last_scrape_at) + timedelta(hours=SCRAPE_INTERVAL_HOURS)


def check_and_scrape_if_due():
    """
    Poll for stale inventory and scrape when due.

    Unlike a fixed wall-clock interval, this recovers after Mac sleep:
    whenever the app wakes up, the next check sees stale inventory and scrapes.
    """
    db = SessionLocal()
    try:
        state = get_or_create_state(db)
        if state.scrape_status == "running":
            logger.debug("Scrape check skipped — scrape already running")
            return
        if not scrape_is_stale(db):
            return

        due_at = next_scrape_due_at(db)
        logger.info(
            "Inventory scrape is due (interval=%s hour(s)) — running now (due %s)",
            SCRAPE_INTERVAL_HOURS,
            due_at.isoformat() if due_at else "immediately",
        )
        result = run_scrape_and_match(db)
        logger.info(result.message)
    except Exception:
        logger.exception("Scheduled scrape check failed")
    finally:
        db.close()


def scheduled_match_cleanup_job():
    logger.info("Purging expired handled matches")
    db = SessionLocal()
    try:
        removed = purge_expired_handled_matches(db)
        if removed:
            logger.info("Removed %s expired handled match(es)", removed)
    except Exception:
        logger.exception("Handled match cleanup failed")
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        check_and_scrape_if_due,
        trigger="interval",
        minutes=SCRAPE_CHECK_INTERVAL_MINUTES,
        id="inventory_scrape_check",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        scheduled_match_cleanup_job,
        trigger="interval",
        hours=HANDLED_MATCH_CLEANUP_HOURS,
        id="handled_match_cleanup",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # Run an immediate check on startup if inventory is stale.
    db = SessionLocal()
    try:
        if scrape_is_stale(db):
            scheduler.add_job(
                check_and_scrape_if_due,
                trigger=DateTrigger(run_date=datetime.now()),
                id="inventory_scrape_startup",
                replace_existing=True,
                max_instances=1,
            )
            logger.info(
                "Inventory is stale on startup — scheduling immediate scrape check"
            )
    except Exception:
        logger.exception("Failed to evaluate startup scrape check")
    finally:
        db.close()

    scheduler.start()
    logger.info(
        "Scheduler started: scrape every %s hour(s), checked every %s minute(s), "
        "match cleanup every %s hour(s)",
        SCRAPE_INTERVAL_HOURS,
        SCRAPE_CHECK_INTERVAL_MINUTES,
        HANDLED_MATCH_CLEANUP_HOURS,
    )


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
