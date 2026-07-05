import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.services.scrape_service import run_scrape_and_match

logger = logging.getLogger(__name__)

# Hours between automatic scrapes. Override with SCRAPE_INTERVAL_HOURS env var.
SCRAPE_INTERVAL_HOURS = float(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))

scheduler = BackgroundScheduler()


def scheduled_scrape_job():
    logger.info("Running scheduled inventory scrape")
    db = SessionLocal()
    try:
        result = run_scrape_and_match(db)
        logger.info(result.message)
    except Exception:
        logger.exception("Scheduled scrape failed")
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        scheduled_scrape_job,
        trigger="interval",
        hours=SCRAPE_INTERVAL_HOURS,
        id="inventory_scrape",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Scheduler started: scrape every %s hour(s)", SCRAPE_INTERVAL_HOURS)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
