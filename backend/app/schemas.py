from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_number: str
    model_name: str
    year: int
    color: str
    date_first_seen: datetime
    is_active: bool


class WishlistEntryCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    phone_or_email: str = Field(min_length=1)
    desired_model: str = Field(min_length=1)
    desired_year_min: int
    desired_year_max: int
    desired_color: str | None = None
    notes: str | None = None
    status: Literal["active", "fulfilled", "cancelled"] = "active"


class WishlistEntryUpdate(BaseModel):
    customer_name: str | None = None
    phone_or_email: str | None = None
    desired_model: str | None = None
    desired_year_min: int | None = None
    desired_year_max: int | None = None
    desired_color: str | None = None
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
    date_added: datetime
    notes: str | None
    status: str


class WishlistMutationOut(WishlistEntryOut):
    new_matches: int = 0


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wishlist_entry_id: int
    inventory_item_id: int
    matched_date: datetime
    notified: bool
    customer_name: str | None = None
    phone_or_email: str | None = None
    desired_model: str | None = None
    customer_notes: str | None = None
    stock_number: str | None = None
    model_name: str | None = None
    year: int | None = None
    color: str | None = None


class MatchNotifyUpdate(BaseModel):
    notified: bool


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    message: str
    created_at: datetime
    is_read: bool


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
    last_scrape_at: datetime | None = None
    scrape_started_at: datetime | None = None


class ScrapeTriggerOut(BaseModel):
    started: bool
    message: str


class AlertsConfigOut(BaseModel):
    email: bool
    sms: bool
