"""
Database initialization script.

Creates all tables and optionally seeds initial data.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import DatabaseManager, Stock, get_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database(seed_data: bool = False):
    """
    Initialize database with all tables.

    Args:
        seed_data: Whether to seed with sample data
    """
    logger.info("=" * 60)
    logger.info("Database Initialization Starting...")
    logger.info("=" * 60)

    # Get database instance
    db = get_db()

    logger.info(f"Database type: {db.db_type}")
    logger.info(f"Database URL: {db.db_url}")

    # Tables are created automatically in DatabaseManager.__init__()
    logger.info("✅ All tables created successfully!")

    if seed_data:
        logger.info("\n" + "=" * 60)
        logger.info("Seeding sample data...")
        logger.info("=" * 60)

        seed_sample_data(db)

    logger.info("\n" + "=" * 60)
    logger.info("Database initialization complete!")
    logger.info("=" * 60)

    return db


def seed_sample_data(db: DatabaseManager):
    """Seed database with sample stock data."""

    # Sample Indian stocks
    sample_stocks = [
        {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd', 'sector': 'Energy', 'industry': 'Oil & Gas', 'exchange': 'NSE'},
        {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'sector': 'IT', 'industry': 'IT Services', 'exchange': 'NSE'},
        {'symbol': 'INFY', 'name': 'Infosys Ltd', 'sector': 'IT', 'industry': 'IT Services', 'exchange': 'NSE'},
        {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd', 'sector': 'Financial', 'industry': 'Banking', 'exchange': 'NSE'},
        {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd', 'sector': 'Financial', 'industry': 'Banking', 'exchange': 'NSE'},
        {'symbol': 'WIPRO', 'name': 'Wipro Ltd', 'sector': 'IT', 'industry': 'IT Services', 'exchange': 'NSE'},
        {'symbol': 'ITC', 'name': 'ITC Ltd', 'sector': 'FMCG', 'industry': 'Diversified', 'exchange': 'NSE'},
        {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Ltd', 'sector': 'Auto', 'industry': 'Automobiles', 'exchange': 'NSE'},
        {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Ltd', 'sector': 'Auto', 'industry': 'Automobiles', 'exchange': 'NSE'},
        {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Financial', 'industry': 'Banking', 'exchange': 'NSE'},
    ]

    with db.get_session() as session:
        added_count = 0

        for stock_data in sample_stocks:
            # Check if stock already exists
            existing = session.query(Stock).filter_by(symbol=stock_data['symbol']).first()

            if not existing:
                stock = Stock(**stock_data)
                session.add(stock)
                added_count += 1
                logger.info(f"  ✅ Added: {stock_data['symbol']} - {stock_data['name']}")
            else:
                logger.info(f"  ⏭️  Skipped: {stock_data['symbol']} (already exists)")

        if added_count > 0:
            logger.info(f"\n✅ Seeded {added_count} stocks")
        else:
            logger.info("\n✅ No new stocks to seed")


def verify_database():
    """Verify database setup."""
    logger.info("\n" + "=" * 60)
    logger.info("Verifying database...")
    logger.info("=" * 60)

    db = get_db()

    with db.get_session() as session:
        # Count stocks
        stock_count = session.query(Stock).count()
        logger.info(f"✅ Stocks table: {stock_count} records")

        # Show sample stocks
        if stock_count > 0:
            logger.info("\nSample stocks:")
            stocks = session.query(Stock).limit(5).all()
            for stock in stocks:
                logger.info(f"  - {stock.symbol}: {stock.name} ({stock.sector})")

    logger.info("\n✅ Database verification complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Initialize stock analysis database')
    parser.add_argument('--seed', action='store_true', help='Seed with sample data')
    parser.add_argument('--verify', action='store_true', help='Verify database setup')
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: deletes all data!)')

    args = parser.parse_args()

    try:
        if args.reset:
            response = input("⚠️  WARNING: This will delete ALL data! Type 'YES' to confirm: ")
            if response == 'YES':
                db = get_db()
                db.drop_tables()
                logger.info("✅ Database reset complete")
                db.create_tables()
                logger.info("✅ Tables recreated")
            else:
                logger.info("Reset cancelled")
                sys.exit(0)

        # Initialize database
        db = init_database(seed_data=args.seed)

        # Verify if requested
        if args.verify:
            verify_database()

        logger.info("\n🎉 Database setup complete!")
        logger.info(f"\n📍 Database location: {db.db_url}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
