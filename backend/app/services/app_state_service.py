from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import AppState


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_state(db: Session) -> AppState:
    state = db.query(AppState).filter(AppState.id == 1).first()
    if state is None:
        state = AppState(id=1, scrape_status="idle")
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def set_scrape_running(db: Session, message: str = "Scrape in progress…") -> None:
    state = get_or_create_state(db)
    state.scrape_status = "running"
    state.scrape_message = message
    state.scrape_started_at = utcnow()
    db.commit()


def set_scrape_success(db: Session, message: str) -> None:
    state = get_or_create_state(db)
    state.scrape_status = "success"
    state.scrape_message = message
    state.last_scrape_at = utcnow()
    state.scrape_started_at = None
    db.commit()


def set_scrape_error(db: Session, message: str) -> None:
    state = get_or_create_state(db)
    state.scrape_status = "error"
    state.scrape_message = message
    state.scrape_started_at = None
    db.commit()


def reset_scrape_idle(db: Session) -> None:
    state = get_or_create_state(db)
    if state.scrape_status == "running":
        state.scrape_status = "idle"
    db.commit()
