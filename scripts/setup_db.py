"""
Database setup script.

Initializes the database and creates all tables.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import init_db, engine
from src.utils.logger import setup_logger
import subprocess

logger = setup_logger(__name__)


def run_sql_file(sql_file: Path):
    """
    Run SQL file using psql command.

    Args:
        sql_file: Path to SQL file
    """
    from config import config

    logger.info(f"Running SQL file: {sql_file}")

    # Extract database connection details from DATABASE_URL
    # Format: postgresql://user:password@host:port/dbname
    db_url = config.DATABASE_URL

    try:
        result = subprocess.run(
            ['psql', db_url, '-f', str(sql_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"Successfully executed {sql_file}")
            if result.stdout:
                print(result.stdout)
        else:
            logger.error(f"Error executing {sql_file}")
            if result.stderr:
                print(result.stderr)
            raise Exception(f"SQL execution failed: {result.stderr}")

    except FileNotFoundError:
        logger.error("psql command not found. Make sure PostgreSQL is installed and in PATH")
        raise


def setup_database():
    """Setup database with schema."""
    logger.info("=" * 50)
    logger.info("DATABASE SETUP STARTING")
    logger.info("=" * 50)

    try:
        # Option 1: Run SQL file (preferred if TimescaleDB is needed)
        schema_file = project_root / 'database' / 'schema.sql'

        if schema_file.exists():
            logger.info("Running schema.sql file...")
            run_sql_file(schema_file)
        else:
            logger.warning(f"schema.sql not found at {schema_file}")

            # Option 2: Create tables using SQLAlchemy
            logger.info("Creating tables using SQLAlchemy...")
            init_db()

        logger.info("=" * 50)
        logger.info("DATABASE SETUP COMPLETED SUCCESSFULLY!")
        logger.info("=" * 50)

        # Test connection
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM stocks"))
            count = result.scalar()
            logger.info(f"Stocks table verified: {count} records")

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise


if __name__ == '__main__':
    setup_database()
