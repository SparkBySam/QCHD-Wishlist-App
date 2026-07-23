import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import InventoryItem, Notification
from app.schemas import (
    AlertsConfigOut,
    InventoryItemOut,
    NotificationOut,
    NotificationsClearedOut,
    ScrapeResult,
    ScrapeStatusOut,
    ScrapeTriggerOut,
)
from app.services.alert_service import alerts_configured, send_email_alert
from app.services.app_state_service import get_or_create_state, set_scrape_running
from app.scheduler import SCRAPE_INTERVAL_HOURS, next_scrape_due_at
from app.services.scrape_service import run_scrape_and_match

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def _background_scrape_job():
    db = SessionLocal()
    try:
        run_scrape_and_match(db)
    except Exception:
        logger.exception("Background scrape failed")
    finally:
        db.close()


@router.get("", response_model=list[InventoryItemOut])
def list_inventory(
    active_only: bool = Query(default=True),
    search: str | None = Query(default=None),
    condition: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(InventoryItem)
    if active_only:
        query = query.filter(InventoryItem.is_active.is_(True))
    if condition:
        normalized = condition.strip().lower()
        if normalized in {"new", "used", "unknown"}:
            query = query.filter(InventoryItem.condition == normalized)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            InventoryItem.stock_number.ilike(term)
            | InventoryItem.model_name.ilike(term)
            | InventoryItem.color.ilike(term)
            | InventoryItem.condition.ilike(term)
        )
    return query.order_by(InventoryItem.date_first_seen.desc()).all()


@router.get("/scrape/status", response_model=ScrapeStatusOut)
def scrape_status(db: Session = Depends(get_db)):
    state = get_or_create_state(db)
    return ScrapeStatusOut(
        scrape_status=state.scrape_status,
        scrape_message=state.scrape_message,
        last_scrape_at=state.last_scrape_at,
        scrape_started_at=state.scrape_started_at,
        next_scrape_due_at=next_scrape_due_at(db),
        scrape_interval_hours=SCRAPE_INTERVAL_HOURS,
    )


@router.post("/scrape", response_model=ScrapeTriggerOut)
def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    state = get_or_create_state(db)
    if state.scrape_status == "running":
        raise HTTPException(status_code=409, detail="A scrape is already running")

    set_scrape_running(db, "Scrape started. Pulling inventory pages…")
    background_tasks.add_task(_background_scrape_job)
    return ScrapeTriggerOut(
        started=True,
        message="Scrape started. This usually takes 2–5 minutes.",
    )


@router.post("/scrape/sync", response_model=ScrapeResult)
def trigger_scrape_sync(db: Session = Depends(get_db)):
    """Run scrape synchronously (useful for scripts / debugging)."""
    state = get_or_create_state(db)
    if state.scrape_status == "running":
        raise HTTPException(status_code=409, detail="A scrape is already running")

    try:
        return run_scrape_and_match(db)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Scrape failed: {exc}. "
                "Ensure Google Chrome is installed and can run headless."
            ),
        ) from exc


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = db.query(Notification)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).all()


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/notifications/read-all", response_model=NotificationsClearedOut)
def mark_all_notifications_read(db: Session = Depends(get_db)):
    unread = db.query(Notification).filter(Notification.is_read.is_(False)).all()
    for notification in unread:
        notification.is_read = True
    db.commit()
    return NotificationsClearedOut(cleared=len(unread))


@router.get("/alerts/config", response_model=AlertsConfigOut)
def get_alerts_config():
    return AlertsConfigOut(**alerts_configured())


@router.post("/alerts/test")
def test_email_alert():
    sent, error = send_email_alert(
        subject="Bike Wishlist Tracker — test email",
        body="If you received this, email alerts are configured correctly.",
    )
    if error == "not_configured":
        raise HTTPException(
            status_code=400,
            detail=(
                "Email not configured. Edit backend/.env with your real "
                "SMTP_USER, SMTP_PASSWORD, and ALERT_EMAIL_TO (not the placeholder values)."
            ),
        )
    if not sent:
        raise HTTPException(
            status_code=400,
            detail=f"Email failed to send: {error}",
        )
    return {"sent": True, "message": "Test email sent."}
