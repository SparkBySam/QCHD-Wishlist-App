import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Match
from app.schemas import MatchNotifyUpdate, MatchOut

router = APIRouter(prefix="/api/matches", tags=["matches"])


def serialize_match(match: Match) -> MatchOut:
    entry = match.wishlist_entry
    item = match.inventory_item
    return MatchOut(
        id=match.id,
        wishlist_entry_id=match.wishlist_entry_id,
        inventory_item_id=match.inventory_item_id,
        matched_date=match.matched_date,
        notified=match.notified,
        customer_name=entry.customer_name if entry else None,
        phone_or_email=entry.phone_or_email if entry else None,
        desired_model=entry.desired_model if entry else None,
        customer_notes=entry.notes if entry else None,
        stock_number=item.stock_number if item else None,
        model_name=item.model_name if item else None,
        year=item.year if item else None,
        color=item.color if item else None,
    )


@router.get("", response_model=list[MatchOut])
def list_matches(
    search: str | None = Query(default=None),
    unhandled_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Match)
        .options(
            joinedload(Match.wishlist_entry),
            joinedload(Match.inventory_item),
        )
        .order_by(Match.matched_date.desc())
    )

    if unhandled_only:
        query = query.filter(Match.notified.is_(False))

    matches = query.all()

    if search:
        term = search.strip().lower()
        matches = [
            match
            for match in matches
            if term
            in " ".join(
                filter(
                    None,
                    [
                        match.wishlist_entry.customer_name if match.wishlist_entry else "",
                        match.wishlist_entry.phone_or_email if match.wishlist_entry else "",
                        match.wishlist_entry.desired_model if match.wishlist_entry else "",
                        match.inventory_item.stock_number if match.inventory_item else "",
                        match.inventory_item.model_name if match.inventory_item else "",
                    ],
                )
            ).lower()
        ]

    return [serialize_match(match) for match in matches]


@router.get("/export")
def export_matches_csv(db: Session = Depends(get_db)):
    matches = (
        db.query(Match)
        .options(
            joinedload(Match.wishlist_entry),
            joinedload(Match.inventory_item),
        )
        .order_by(Match.matched_date.desc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "matched_date",
            "customer_name",
            "phone_or_email",
            "customer_notes",
            "desired_model",
            "stock_number",
            "year",
            "model_name",
            "color",
            "notified",
        ]
    )
    for match in matches:
        entry = match.wishlist_entry
        item = match.inventory_item
        writer.writerow(
            [
                match.matched_date.isoformat() if match.matched_date else "",
                entry.customer_name if entry else "",
                entry.phone_or_email if entry else "",
                entry.notes if entry else "",
                entry.desired_model if entry else "",
                item.stock_number if item else "",
                item.year if item else "",
                item.model_name if item else "",
                item.color if item else "",
                "yes" if match.notified else "no",
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=matches.csv"},
    )


@router.patch("/{match_id}/notified", response_model=MatchOut)
def update_match_notified(
    match_id: int,
    payload: MatchNotifyUpdate,
    db: Session = Depends(get_db),
):
    match = (
        db.query(Match)
        .options(
            joinedload(Match.wishlist_entry),
            joinedload(Match.inventory_item),
        )
        .filter(Match.id == match_id)
        .first()
    )
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    match.notified = payload.notified
    db.commit()
    db.refresh(match)
    return serialize_match(match)
