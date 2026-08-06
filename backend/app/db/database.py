"""
Database engine + session setup.

Works with PostgreSQL (production) and SQLite (local dev / quick demos).
- PostgreSQL: expects `postgresql+psycopg://user:pass@host:port/db`
- SQLite:    set `DATABASE_URL=sqlite:///./aee.db` in `.env`

SQLAlchemy 2.0 style: declarative base via `DeclarativeBase`.
"""
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base used by every ORM model."""
    pass


def _build_connect_args() -> dict:
    """SQLite needs `check_same_thread=False` to work across FastAPI's threadpool."""
    if settings.DATABASE_URL.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_build_connect_args(),
    pool_pre_ping=True,   # silently reconnect on stale connections
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    future=True,
)


def _get_target_database_name() -> str:
    parsed = urlsplit(settings.DATABASE_URL)
    if parsed.path and parsed.path != "/":
        return parsed.path.lstrip("/")
    return "postgres"


def _build_admin_database_url() -> str:
    parsed = urlsplit(settings.DATABASE_URL)
    # Connect to the maintenance DB ('postgres') so we can CREATE DATABASE.
    return urlunsplit((parsed.scheme, parsed.netloc, "/postgres", parsed.query, parsed.fragment))


def ensure_database_exists() -> None:
    """
    Best-effort auto-create the target database (PostgreSQL only).

    Safe to call repeatedly — if the DB already exists it returns immediately.
    No-op for SQLite.
    """
    if not settings.DATABASE_URL.startswith(("postgres", "postgresql")):
        return

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return
    except OperationalError as exc:
        msg = str(exc).lower()
        if "does not exist" not in msg:
            # Different error (auth, network, etc.) — surface it.
            raise

    db_name = _get_target_database_name()
    admin_engine = create_engine(
        _build_admin_database_url(),
        connect_args={},
        isolation_level="AUTOCOMMIT",
    )
    with admin_engine.connect() as conn:
        conn.exec_driver_sql(f'CREATE DATABASE "{db_name}"')


def get_db():
    """FastAPI dependency that yields a SQLAlchemy session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

