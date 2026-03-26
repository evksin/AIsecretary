from __future__ import annotations

import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ai_secretary.db",
)

engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

logger.info("Database engine initialized for %s", DATABASE_URL)
if DATABASE_URL.startswith("sqlite"):
    logger.warning(
        "SQLite is enabled for local development. "
        "Set DATABASE_URL to PostgreSQL in production."
    )


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        logger.exception("Database session failed")
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """Validate current database connectivity with a lightweight query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connectivity check passed")
        return True
    except SQLAlchemyError:
        logger.exception("Database connectivity check failed")
        return False

