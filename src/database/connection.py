"""
Database connection manager.

Supports SQLite (dev) and PostgreSQL (production).
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from pathlib import Path
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections for both SQLite and PostgreSQL.

    Usage:
        # SQLite (default)
        db = DatabaseManager()

        # PostgreSQL
        db = DatabaseManager(
            db_type='postgresql',
            host='localhost',
            port=5432,
            database='stock_analysis',
            user='your_user',
            password='your_password'
        )
    """

    def __init__(
        self,
        db_type: str = 'sqlite',
        database: str = None,
        host: str = 'localhost',
        port: int = 5432,
        user: str = None,
        password: str = None
    ):
        """
        Initialize database connection.

        Args:
            db_type: 'sqlite' or 'postgresql'
            database: Database name (SQLite: path, PostgreSQL: database name)
            host: Database host (PostgreSQL only)
            port: Database port (PostgreSQL only)
            user: Database user (PostgreSQL only)
            password: Database password (PostgreSQL only)
        """
        self.db_type = db_type.lower()

        if self.db_type == 'sqlite':
            # Default SQLite database path
            if database is None:
                db_path = Path(__file__).parent.parent.parent / 'data' / 'stock_analysis.db'
                db_path.parent.mkdir(parents=True, exist_ok=True)
                database = str(db_path)

            self.db_url = f'sqlite:///{database}'

            # SQLite-specific settings
            self.engine = create_engine(
                self.db_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )

            # Enable foreign keys in SQLite
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            logger.info(f"SQLite database initialized at {database}")

        elif self.db_type == 'postgresql':
            # PostgreSQL connection
            if not all([database, user, password]):
                raise ValueError("PostgreSQL requires database, user, and password")

            self.db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'

            self.engine = create_engine(
                self.db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                echo=False
            )

            logger.info(f"PostgreSQL database initialized at {host}:{port}/{database}")

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

        # Create all tables
        self.create_tables()

    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.

        Usage:
            with db.get_session() as session:
                stock = session.query(Stock).first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close all database connections."""
        self.SessionLocal.remove()
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance (can be overridden)
_db_instance = None


def get_db() -> DatabaseManager:
    """
    Get global database instance.

    Uses SQLite by default. To use PostgreSQL, set environment variables:
        DB_TYPE=postgresql
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=stock_analysis
        DB_USER=your_user
        DB_PASSWORD=your_password

    Returns:
        DatabaseManager instance
    """
    global _db_instance

    if _db_instance is None:
        db_type = os.getenv('DB_TYPE', 'sqlite')

        if db_type == 'postgresql':
            _db_instance = DatabaseManager(
                db_type='postgresql',
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                database=os.getenv('DB_NAME', 'stock_analysis'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
        else:
            # SQLite (default)
            db_path = os.getenv('DB_PATH')
            _db_instance = DatabaseManager(db_type='sqlite', database=db_path)

    return _db_instance


def reset_db_instance():
    """Reset global database instance (useful for testing)."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
    _db_instance = None
