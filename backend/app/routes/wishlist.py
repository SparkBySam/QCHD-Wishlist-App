from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Match, WishlistEntry
from app.schemas import WishlistEntryCreate, WishlistEntryOut, WishlistEntryUpdate, WishlistMutationOut
from app.services.matching_service import run_matching

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


def _validate_years(year_min: int, year_max: int) -> None:
    if year_min > year_max:
        raise HTTPException(
            status_code=400,
            detail="desired_year_min cannot be greater than desired_year_max",
        )


def _maybe_match_entry(db: Session, entry: WishlistEntry) -> int:
    if entry.status != "active":
        return 0
    return run_matching(db, wishlist_entry_ids=[entry.id])


def _to_mutation_out(entry: WishlistEntry, new_matches: int) -> WishlistMutationOut:
    return WishlistMutationOut(
        id=entry.id,
        customer_name=entry.customer_name,
        phone_or_email=entry.phone_or_email,
        desired_model=entry.desired_model,
        desired_year_min=entry.desired_year_min,
        desired_year_max=entry.desired_year_max,
        desired_color=entry.desired_color,
        desired_condition=entry.desired_condition,
        date_added=entry.date_added,
        notes=entry.notes,
        status=entry.status,
        new_matches=new_matches,
    )


@router.get("", response_model=list[WishlistEntryOut])
def list_wishlist(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    condition: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(WishlistEntry)
    if status:
        query = query.filter(WishlistEntry.status == status)
    if condition:
        normalized = condition.strip().lower()
        if normalized in {"new", "used"}:
            query = query.filter(WishlistEntry.desired_condition == normalized)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            WishlistEntry.customer_name.ilike(term)
            | WishlistEntry.phone_or_email.ilike(term)
            | WishlistEntry.desired_model.ilike(term)
            | WishlistEntry.notes.ilike(term)
        )
    return query.order_by(WishlistEntry.date_added.desc()).all()


@router.post("", response_model=WishlistMutationOut, status_code=201)
def create_wishlist_entry(payload: WishlistEntryCreate, db: Session = Depends(get_db)):
    _validate_years(payload.desired_year_min, payload.desired_year_max)

    entry = WishlistEntry(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)

    new_matches = _maybe_match_entry(db, entry)
    return _to_mutation_out(entry, new_matches)


@router.get("/{entry_id}", response_model=WishlistEntryOut)
def get_wishlist_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(WishlistEntry).filter(WishlistEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Wishlist entry not found")
    return entry


@router.put("/{entry_id}", response_model=WishlistMutationOut)
def update_wishlist_entry(
    entry_id: int,
    payload: WishlistEntryUpdate,
    db: Session = Depends(get_db),
):
    entry = db.query(WishlistEntry).filter(WishlistEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Wishlist entry not found")

    updates = payload.model_dump(exclude_unset=True)
    year_min = updates.get("desired_year_min", entry.desired_year_min)
    year_max = updates.get("desired_year_max", entry.desired_year_max)
    _validate_years(year_min, year_max)

    for field, value in updates.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)

    new_matches = _maybe_match_entry(db, entry)
    return _to_mutation_out(entry, new_matches)


@router.patch("/{entry_id}/fulfill", response_model=WishlistEntryOut)
def fulfill_wishlist_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(WishlistEntry).filter(WishlistEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Wishlist entry not found")
    entry.status = "fulfilled"
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_wishlist_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = (
        db.query(WishlistEntry)
        .options(joinedload(WishlistEntry.matches).joinedload(Match.notifications))
        .filter(WishlistEntry.id == entry_id)
        .first()
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Wishlist entry not found")

    for match in entry.matches:
        for notification in list(match.notifications):
            db.delete(notification)
        db.delete(match)

    db.delete(entry)
    db.commit()
    return None
