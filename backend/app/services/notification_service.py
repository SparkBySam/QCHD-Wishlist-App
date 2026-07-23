from sqlalchemy.orm import Session

from app.models import InventoryItem, Match, Notification, WishlistEntry


def build_match_message(
    entry: WishlistEntry,
    item: InventoryItem,
    matched_model: str | None = None,
) -> str:
    color_part = f" in {item.color}" if item.color else ""
    condition = (item.condition or "unknown").lower()
    condition_part = f" [{condition}]" if condition in {"new", "used"} else ""
    model_hit = matched_model or entry.desired_model
    return (
        f"Match for {entry.customer_name}: "
        f"{item.year} {item.model_name}{color_part}{condition_part} "
        f"(stock #{item.stock_number}) matched '{model_hit}' "
        f"({entry.desired_year_min}–{entry.desired_year_max}). "
        f"Contact: {entry.phone_or_email}"
    )


def create_match_notification(
    db: Session,
    match: Match,
    entry: WishlistEntry,
    item: InventoryItem,
    message: str | None = None,
) -> Notification:
    notification = Notification(
        match_id=match.id,
        message=message or build_match_message(entry, item),
        is_read=False,
    )
    db.add(notification)
    return notification
