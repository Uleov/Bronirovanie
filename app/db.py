import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def _database_url() -> str:
    return os.environ.get("DATABASE_URL", "sqlite:///app.db")


def _echo() -> bool:
    return os.environ.get("SQLALCHEMY_ECHO", "").strip() in {"1", "true", "True", "yes", "YES"}


engine = create_engine(_database_url(), echo=_echo())


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

