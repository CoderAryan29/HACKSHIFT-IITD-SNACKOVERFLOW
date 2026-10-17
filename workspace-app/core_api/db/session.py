
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core_api.config import get_database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create the database engine when the first connection is needed."""
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )


def get_session_factory() -> sessionmaker[Session]:
    """Return a factory for database sessions."""
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """Provide a database session to a FastAPI endpoint."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
