from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer


def _serialize_utc(value: datetime) -> str:
    """Emit UTC ISO-8601 with Z so browsers don't treat naive stamps as local."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


UtcDateTime = Annotated[datetime, PlainSerializer(_serialize_utc, return_type=str)]


class InventoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_number: str
    model_name: str
    year: int
    color: str
    condition: str = "unknown"
    date_first_seen: UtcDateTime
    is_active: bool


class WishlistEntryCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    phone_or_email: str = Field(min_length=1)
    desired_model: str = Field(min_length=1)
    desired_year_min: int
    desired_year_max: int
    desired_color: str | None = None
    desired_condition: Literal["new", "used"] | None = None
    notes: str | None = None
    status: Literal["active", "fulfilled", "cancelled"] = "active"


class WishlistEntryUpdate(BaseModel):
    customer_name: str | None = None
    phone_or_email: str | None = None
    desired_model: str | None = None
    desired_year_min: int | None = None
    desired_year_max: int | None = None
    desired_color: str | None = None
    desired_condition: Literal["new", "used"] | None = None
    notes: str | None = None
    status: Literal["active", "fulfilled", "cancelled"] | None = None


class WishlistEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    phone_or_email: str
    desired_model: str
    desired_year_min: int
    desired_year_max: int
    desired_color: str | None
    desired_condition: str | None = None
    date_added: UtcDateTime
    notes: str | None
    status: str


class WishlistMutationOut(WishlistEntryOut):
    new_matches: int = 0


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wishlist_entry_id: int
    inventory_item_id: int
    matched_date: UtcDateTime
    notified: bool
    dismissed: bool = False
    customer_name: str | None = None
    phone_or_email: str | None = None
    desired_model: str | None = None
    customer_notes: str | None = None
    stock_number: str | None = None
    model_name: str | None = None
    year: int | None = None
    color: str | None = None
    condition: str | None = None


class MatchNotifyUpdate(BaseModel):
    notified: bool


class MatchExpireHandledRequest(BaseModel):
    ids: list[int] | None = None


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    message: str
    created_at: UtcDateTime
    is_read: bool


class NotificationsClearedOut(BaseModel):
    cleared: int


class ScrapeResult(BaseModel):
    scraped_count: int
    new_items: int
    reactivated_items: int
    deactivated_items: int
    new_matches: int
    message: str


class ScrapeStatusOut(BaseModel):
    scrape_status: str
    scrape_message: str | None = None
    last_scrape_at: UtcDateTime | None = None
    scrape_started_at: UtcDateTime | None = None
    next_scrape_due_at: UtcDateTime | None = None
    scrape_interval_hours: float = 6


class ScrapeTriggerOut(BaseModel):
    started: bool
    message: str


class AlertsConfigOut(BaseModel):
    email: bool
    sms: bool
