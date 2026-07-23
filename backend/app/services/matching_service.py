from sqlalchemy.orm import Session

from app.models import InventoryItem, Match, WishlistEntry
from app.services.alert_service import dispatch_batch_match_alerts
from app.services.model_utils import model_matches_any
from app.services.notification_service import build_match_message, create_match_notification


def color_matches(desired_color: str | None, inventory_color: str) -> bool:
    if not desired_color or not desired_color.strip():
        return True
    return desired_color.strip().lower() in (inventory_color or "").strip().lower()


def condition_matches(desired_condition: str | None, inventory_condition: str) -> bool:
    if not desired_condition or not desired_condition.strip():
        return True
    wanted = desired_condition.strip().lower()
    if wanted not in {"new", "used"}:
        return True
    return (inventory_condition or "").strip().lower() == wanted


def year_in_range(year: int, year_min: int, year_max: int) -> bool:
    return year_min <= year <= year_max


def find_match(entry: WishlistEntry, item: InventoryItem) -> str | None:
    """Return the wishlist model that matched, or None."""
    if not year_in_range(item.year, entry.desired_year_min, entry.desired_year_max):
        return None
    if not color_matches(entry.desired_color, item.color):
        return None
    if not condition_matches(entry.desired_condition, item.condition):
        return None
    return model_matches_any(entry.desired_model, item.model_name)


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

            matched_model = find_match(entry, item)
            if matched_model is None:
                continue

            match = Match(
                wishlist_entry_id=entry.id,
                inventory_item_id=item.id,
                notified=False,
            )
            db.add(match)
            db.flush()
            message = build_match_message(entry, item, matched_model)
            create_match_notification(db, match, entry, item, message)
            alert_messages.append(message)
            existing_pairs.add(pair)
            new_matches += 1

    db.commit()

    if alert_messages:
        dispatch_batch_match_alerts(alert_messages)

    return new_matches
