import os
from datetime import timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Match, utcnow

HANDLED_MATCH_RETENTION_DAYS = int(os.getenv("HANDLED_MATCH_RETENTION_DAYS", "7"))


def handled_match_cutoff():
    return utcnow() - timedelta(days=HANDLED_MATCH_RETENTION_DAYS)


def purge_expired_handled_matches(db: Session) -> int:
    """Delete handled matches older than the retention window."""
    cutoff = handled_match_cutoff()
    expired = (
        db.query(Match)
        .filter(Match.notified.is_(True))
        .filter(Match.notified_at.isnot(None))
        .filter(Match.notified_at < cutoff)
        .all()
    )
    for match in expired:
        db.delete(match)
    if expired:
        db.commit()
    return len(expired)


def apply_handled_match_visibility(query):
    """Exclude dismissed matches and handled matches past the retention window."""
    cutoff = handled_match_cutoff()
    return query.filter(Match.dismissed.is_(False)).filter(
        or_(
            Match.notified.is_(False),
            Match.notified_at.is_(None),
            Match.notified_at >= cutoff,
        )
    )


def dismiss_match(db: Session, match: Match) -> Match:
    """Hide a match from the list and prevent rematching the same pair."""
    match.dismissed = True
    match.dismissed_at = utcnow()
    # Clear related unread notifications so they don't linger on the dashboard.
    for notification in list(match.notifications):
        notification.is_read = True
    db.commit()
    db.refresh(match)
    return match


def expire_handled_match(db: Session, match: Match) -> None:
    if not match.notified:
        raise ValueError("Only handled matches can be expired manually")
    db.delete(match)
    db.commit()


def expire_all_handled_matches(db: Session, ids: list[int] | None = None) -> int:
    query = db.query(Match).filter(Match.notified.is_(True))
    if ids is not None:
        query = query.filter(Match.id.in_(ids))
    handled = query.all()
    for match in handled:
        db.delete(match)
    if handled:
        db.commit()
    return len(handled)
