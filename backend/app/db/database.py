from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _get_target_database_name() -> str:
    parsed = urlsplit(settings.DATABASE_URL)
    if parsed.path and parsed.path != "/":
        return parsed.path.lstrip("/")
    return "postgres"


def _build_admin_database_url() -> str:
    parsed = urlsplit(settings.DATABASE_URL)
    return urlunsplit((parsed.scheme, parsed.netloc, "/postgres", parsed.query, parsed.fragment))


def ensure_database_exists() -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return
    except OperationalError as exc:
        if "does not exist" not in str(exc).lower():
            raise

    db_name = _get_target_database_name()
    admin_engine = create_engine(_build_admin_database_url(), connect_args=connect_args)
    with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.exec_driver_sql(f'CREATE DATABASE "{db_name}"')


ensure_database_exists()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

