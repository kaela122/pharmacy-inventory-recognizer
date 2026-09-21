"""Database engine + session factory + FastAPI dependency.

Postgres-first: the app uses the DATABASE_URL from your .env (PostgreSQL by
default). If Postgres can't be reached on startup, it automatically falls back
to a local SQLite file so the app still runs -- and prints which one it used.
The engine is created lazily so importing the app never requires a live DB.
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None
ACTIVE_URL: str = ""

SQLITE_FALLBACK = "sqlite:///./pharmahub.db"


def _try(url: str) -> Engine | None:
    try:
        eng = create_engine(url, pool_pre_ping=True, future=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return eng
    except (SQLAlchemyError, ImportError, Exception):
        return None


def _init() -> None:
    global _engine, _SessionLocal, ACTIVE_URL
    if _engine is not None:
        return

    wanted = get_settings().database_url
    eng = _try(wanted)
    if eng is not None:
        ACTIVE_URL = wanted
        kind = "PostgreSQL" if wanted.startswith("postgresql") else "SQLite"
        print(f"[db] Connected to {kind}: {wanted.split('@')[-1]}")
    else:
        eng = create_engine(SQLITE_FALLBACK, future=True)
        ACTIVE_URL = SQLITE_FALLBACK
        print("=" * 68)
        print("[db] PostgreSQL not reachable — using SQLite fallback (pharmahub.db).")
        print("     To use Postgres: start the server, create the 'pharmacy' DB,")
        print("     and set DATABASE_URL in backend/.env  (see README).")
        print("=" * 68)

    _engine = eng
    _SessionLocal = sessionmaker(bind=eng, autoflush=False, expire_on_commit=False)


def get_engine() -> Engine:
    _init()
    assert _engine is not None
    return _engine


def new_session() -> Session:
    """Create a Session (used by the seeder). Always call _init() first."""
    _init()
    assert _SessionLocal is not None
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a session and always close it."""
    db = new_session()
    try:
        yield db
    finally:
        db.close()
