from sqlalchemy.orm import Session

from app.models import InventoryItem, Match, WishlistEntry
from app.services.alert_service import dispatch_match_alerts
from app.services.model_utils import model_matches
from app.services.notification_service import build_match_message, create_match_notification


def color_matches(desired_color: str | None, inventory_color: str) -> bool:
    if not desired_color or not desired_color.strip():
        return True
    return desired_color.strip().lower() in (inventory_color or "").strip().lower()


def year_in_range(year: int, year_min: int, year_max: int) -> bool:
    return year_min <= year <= year_max


def is_match(entry: WishlistEntry, item: InventoryItem) -> bool:
    return (
        model_matches(entry.desired_model, item.model_name)
        and year_in_range(item.year, entry.desired_year_min, entry.desired_year_max)
        and color_matches(entry.desired_color, item.color)
    )


def run_matching(
    db: Session,
    inventory_item_ids: list[int] | None = None,
    wishlist_entry_ids: list[int] | None = None,
) -> int:
    """
    Match active wishlist entries against active inventory.

    - inventory_item_ids only: post-scrape check for new/reactivated bikes
    - wishlist_entry_ids only: check new/updated wishlist against full inventory
    - both None: full cross-check
    """
    entry_query = db.query(WishlistEntry).filter(WishlistEntry.status == "active")
    if wishlist_entry_ids is not None:
        if not wishlist_entry_ids:
            return 0
        entry_query = entry_query.filter(WishlistEntry.id.in_(wishlist_entry_ids))

    active_entries = entry_query.all()
    if not active_entries:
        return 0

    inventory_query = db.query(InventoryItem).filter(InventoryItem.is_active.is_(True))
    if inventory_item_ids is not None:
        if not inventory_item_ids:
            return 0
        inventory_query = inventory_query.filter(InventoryItem.id.in_(inventory_item_ids))

    inventory_items = inventory_query.all()
    if not inventory_items:
        return 0

    existing_pairs = {
        (m.wishlist_entry_id, m.inventory_item_id)
        for m in db.query(Match).all()
    }

    alert_messages: list[str] = []
    new_matches = 0

    for entry in active_entries:
        for item in inventory_items:
            pair = (entry.id, item.id)
            if pair in existing_pairs:
                continue
            if not is_match(entry, item):
                continue

            match = Match(
                wishlist_entry_id=entry.id,
                inventory_item_id=item.id,
                notified=False,
            )
            db.add(match)
            db.flush()
            create_match_notification(db, match, entry, item)
            alert_messages.append(build_match_message(entry, item))
            existing_pairs.add(pair)
            new_matches += 1

    db.commit()

    for message in alert_messages:
        dispatch_match_alerts(message)

    return new_matches
