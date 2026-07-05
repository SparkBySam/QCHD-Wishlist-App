from sqlalchemy.orm import Session

from app.models import InventoryItem, Match, Notification, WishlistEntry


def build_match_message(entry: WishlistEntry, item: InventoryItem) -> str:
    color_part = f" in {item.color}" if item.color else ""
    return (
        f"Match for {entry.customer_name}: "
        f"{item.year} {item.model_name}{color_part} "
        f"(stock #{item.stock_number}) matches wishlist for "
        f"'{entry.desired_model}' ({entry.desired_year_min}–{entry.desired_year_max}). "
        f"Contact: {entry.phone_or_email}"
    )


def create_match_notification(
    db: Session,
    match: Match,
    entry: WishlistEntry,
    item: InventoryItem,
) -> Notification:
    notification = Notification(
        match_id=match.id,
        message=build_match_message(entry, item),
        is_read=False,
    )
    db.add(notification)
    return notification
