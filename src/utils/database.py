"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import logging

from config import config
from src.data.models.base import Base

logger = logging.getLogger(__name__)


# Create engine
engine = create_engine(
    config.DATABASE_URL,
    poolclass=NullPool if config.DEBUG else None,
    echo=config.DEBUG,
    future=True
)

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)


def get_db():
    """
    Get database session.

    Usage:
        db = get_db()
        try:
            # Use db
            db.commit()
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    """
    return SessionLocal()


@contextmanager
def get_db_context():
    """
    Context manager for database session.

    Usage:
        with get_db_context() as db:
            stock = db.query(Stock).filter_by(symbol='RELIANCE').first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database (create all tables)."""
    try:
        # Import all models to ensure they're registered
        from src.data.models import Stock, StockPrice, Signal, BacktestResult

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def drop_all_tables():
    """Drop all tables (use with caution!)."""
    if not config.DEBUG:
        raise Exception("Cannot drop tables in production")

    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")


def close_db():
    """Close all database connections."""
    SessionLocal.remove()
    engine.dispose()
    logger.info("Database connections closed")
