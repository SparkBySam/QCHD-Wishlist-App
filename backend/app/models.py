from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    condition: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    date_first_seen: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    matches: Mapped[list["Match"]] = relationship(
        back_populates="inventory_item",
        cascade="all, delete-orphan",
    )


class WishlistEntry(Base):
    __tablename__ = "wishlist_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_or_email: Mapped[str] = mapped_column(String(255), nullable=False)
    desired_model: Mapped[str] = mapped_column(String(255), nullable=False)
    desired_year_min: Mapped[int] = mapped_column(Integer, nullable=False)
    desired_year_max: Mapped[int] = mapped_column(Integer, nullable=False)
    desired_color: Mapped[str | None] = mapped_column(String(128), nullable=True)
    desired_condition: Mapped[str | None] = mapped_column(String(16), nullable=True)
    date_added: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)

    matches: Mapped[list["Match"]] = relationship(
        back_populates="wishlist_entry",
        cascade="all, delete-orphan",
    )


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wishlist_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("wishlist_entries.id"), nullable=False
    )
    inventory_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id"), nullable=False
    )
    matched_date: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    wishlist_entry: Mapped["WishlistEntry"] = relationship(back_populates="matches")
    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="matches")
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="match",
        cascade="all, delete-orphan",
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    match: Mapped["Match"] = relationship(back_populates="notifications")


class AppState(Base):
    __tablename__ = "app_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_scrape_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scrape_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scrape_status: Mapped[str] = mapped_column(String(32), default="idle", nullable=False)
    scrape_message: Mapped[str | None] = mapped_column(Text, nullable=True)
