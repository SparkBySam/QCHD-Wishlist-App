from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "wishlist.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401
    from app.models import AppState, Match

    Base.metadata.create_all(bind=engine)
    _migrate_matches_notified_at()
    _migrate_matches_dismissed()
    _migrate_inventory_condition()
    _migrate_wishlist_desired_condition()

    db = SessionLocal()
    try:
        if db.query(AppState).filter(AppState.id == 1).first() is None:
            db.add(AppState(id=1, scrape_status="idle"))
            db.commit()

        now = models.utcnow()
        stale = (
            db.query(Match)
            .filter(Match.notified.is_(True), Match.notified_at.is_(None))
            .all()
        )
        if stale:
            for match in stale:
                match.notified_at = now
            db.commit()
    finally:
        db.close()


def _migrate_matches_notified_at():
    inspector = inspect(engine)
    if "matches" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("matches")}
    if "notified_at" in columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE matches ADD COLUMN notified_at DATETIME"))


def _migrate_matches_dismissed():
    inspector = inspect(engine)
    if "matches" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("matches")}
    with engine.begin() as conn:
        if "dismissed" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE matches "
                    "ADD COLUMN dismissed BOOLEAN NOT NULL DEFAULT 0"
                )
            )
        if "dismissed_at" not in columns:
            conn.execute(text("ALTER TABLE matches ADD COLUMN dismissed_at DATETIME"))


def _migrate_inventory_condition():
    inspector = inspect(engine)
    if "inventory_items" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("inventory_items")}
    if "condition" in columns:
        return

    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE inventory_items "
                "ADD COLUMN condition VARCHAR(16) NOT NULL DEFAULT 'unknown'"
            )
        )


def _migrate_wishlist_desired_condition():
    inspector = inspect(engine)
    if "wishlist_entries" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("wishlist_entries")}
    if "desired_condition" in columns:
        return

    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE wishlist_entries ADD COLUMN desired_condition VARCHAR(16)")
        )
