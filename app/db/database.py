from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def _db_url() -> str:
    from app.core.config import settings
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{settings.DATA_DIR}/app.db"


def _make_engine():
    return create_engine(_db_url(), connect_args={"check_same_thread": False})


# Initialised once on first use
_engine = None
_SessionLocal = None


def _get_session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = _make_engine()
        _SessionLocal = sessionmaker(bind=_engine)
    return _SessionLocal


def get_session():
    """FastAPI dependency — yields a database session."""
    factory = _get_session_factory()
    with factory() as session:
        yield session


def create_tables() -> None:
    """Create all tables. Called once on startup."""
    from app.db import models  # noqa: F401 — registers models with Base
    engine = _make_engine()
    Base.metadata.create_all(engine)
