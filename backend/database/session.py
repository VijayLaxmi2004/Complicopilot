from __future__ import annotations
from typing import Generator, Optional
from sqlalchemy.orm import Session

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database URL (env with sane default for local/dev)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./complicopilot.db",
)

# Engine config - SQLite-specific configuration
if DATABASE_URL.startswith("sqlite"):
    logger.info(f"Using SQLite database: {DATABASE_URL}")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other database
    # Mask password in logs for security
    log_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    logger.info(f"Using PostgreSQL database at: {log_url}")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        future=True,
    )

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy Session for request-scoped DB access.

    Usage:
        def route(db: Session = Depends(get_db)):
            ...
    """
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()