from pathlib import Path

from sqlalchemy import create_engine
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
    from app.models import AppState

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(AppState).filter(AppState.id == 1).first() is None:
            db.add(AppState(id=1, scrape_status="idle"))
            db.commit()
    finally:
        db.close()
