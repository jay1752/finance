"""
NSE Data Updater - Scheduled task to fetch and store NSE data daily.

This script:
1. Fetches FII/DII data from NSE
2. Fetches delivery percentage for all active stocks
3. Stores data in the database
4. Runs daily during off-market hours

Usage:
    # Run once:
    python scripts/nse_data_updater.py --once

    # Run as scheduled service:
    python scripts/nse_data_updater.py
"""
import sys
from pathlib import Path
import logging
from datetime import datetime, time
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import IntegrityError

from config import config
from src.data.adapters import NSEAdapter
from src.data.models import FIIDIIData, DeliveryData, Stock
from src.utils.database import get_db_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nse_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def update_fii_dii_data():
    """
    Fetch and store FII/DII data from NSE.

    This runs once per day and stores institutional investment data.
    """
    logger.info("=" * 60)
    logger.info("Starting FII/DII data update...")
    logger.info("=" * 60)

    try:
        # Initialize NSE adapter
        nse_adapter = NSEAdapter()

        # Fetch FII/DII data
        logger.info("Fetching FII/DII data from NSE...")
        fii_dii = nse_adapter.get_fii_dii_data()

        if not fii_dii:
            logger.warning("No FII/DII data received from NSE")
            nse_adapter.close()
            return False

        logger.info(f"Received FII/DII data for date: {fii_dii['date']}")
        logger.info(f"FII Net: ₹{fii_dii['fii_net']:.2f} Cr")
        logger.info(f"DII Net: ₹{fii_dii['dii_net']:.2f} Cr")

        # Store in database
        with get_db_context() as db:
            # Create model instance
            fii_dii_record = FIIDIIData.from_nse_data(fii_dii)

            # Check if data for this date already exists
            existing = db.query(FIIDIIData).filter(
                FIIDIIData.date == fii_dii_record.date
            ).first()

            if existing:
                # Update existing record
                logger.info(f"Updating existing FII/DII record for {fii_dii_record.date}")
                existing.fii_gross_purchase = fii_dii_record.fii_gross_purchase
                existing.fii_gross_sale = fii_dii_record.fii_gross_sale
                existing.fii_net = fii_dii_record.fii_net
                existing.dii_gross_purchase = fii_dii_record.dii_gross_purchase
                existing.dii_gross_sale = fii_dii_record.dii_gross_sale
                existing.dii_net = fii_dii_record.dii_net
            else:
                # Insert new record
                logger.info(f"Inserting new FII/DII record for {fii_dii_record.date}")
                db.add(fii_dii_record)

            db.commit()
            logger.info("✓ FII/DII data saved to database successfully")

        nse_adapter.close()
        return True

    except Exception as e:
        logger.error(f"Error updating FII/DII data: {e}", exc_info=True)
        return False


def update_delivery_data():
    """
    Fetch and store delivery percentage for all active stocks.

    This runs once per day for each stock in the database.
    """
    logger.info("=" * 60)
    logger.info("Starting delivery percentage update...")
    logger.info("=" * 60)

    try:
        # Initialize NSE adapter
        nse_adapter = NSEAdapter()

        # Get all active stocks
        with get_db_context() as db:
            active_stocks_query = db.query(Stock).filter(Stock.is_active == True).all()
            # Extract stock info while in session
            active_stocks = [(stock.id, stock.symbol) for stock in active_stocks_query]
            logger.info(f"Found {len(active_stocks)} active stocks")

        success_count = 0
        error_count = 0

        # Fetch delivery data for each stock
        for stock_id, stock_symbol in active_stocks:
            try:
                logger.info(f"Fetching delivery data for {stock_symbol}...")

                # Fetch from NSE
                delivery = nse_adapter.get_delivery_percentage(stock_symbol)

                if not delivery:
                    logger.warning(f"No delivery data received for {stock_symbol}")
                    error_count += 1
                    continue

                logger.info(
                    f"{stock_symbol}: {delivery['delivery_percentage']:.2f}% "
                    f"({delivery['delivery_quantity']:,} / {delivery['traded_quantity']:,})"
                )

                # Store in database
                with get_db_context() as db:
                    # Create model instance
                    delivery_record = DeliveryData.from_nse_data(stock_id, delivery)

                    # Check if data for this stock and date already exists
                    existing = db.query(DeliveryData).filter(
                        DeliveryData.stock_id == stock_id,
                        DeliveryData.date == delivery_record.date
                    ).first()

                    if existing:
                        # Update existing record
                        logger.debug(f"Updating existing delivery record for {stock_symbol}")
                        existing.delivery_quantity = delivery_record.delivery_quantity
                        existing.traded_quantity = delivery_record.traded_quantity
                        existing.delivery_percentage = delivery_record.delivery_percentage
                    else:
                        # Insert new record
                        logger.debug(f"Inserting new delivery record for {stock_symbol}")
                        db.add(delivery_record)

                    db.commit()

                success_count += 1

                # Small delay to be respectful to NSE servers
                import time
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error fetching delivery data for {stock_symbol}: {e}")
                error_count += 1
                continue

        logger.info("=" * 60)
        logger.info(f"Delivery data update complete:")
        logger.info(f"  ✓ Success: {success_count} stocks")
        logger.info(f"  ✗ Errors: {error_count} stocks")
        logger.info("=" * 60)

        nse_adapter.close()
        return True

    except Exception as e:
        logger.error(f"Error updating delivery data: {e}", exc_info=True)
        return False


def run_daily_update():
    """Run both FII/DII and delivery data updates."""
    logger.info("\n" + "=" * 60)
    logger.info("NSE DAILY DATA UPDATE - STARTED")
    logger.info(f"Time: {datetime.now()}")
    logger.info("=" * 60)

    # Update FII/DII data
    fii_dii_success = update_fii_dii_data()

    # Update delivery data
    delivery_success = update_delivery_data()

    logger.info("=" * 60)
    logger.info("NSE DAILY DATA UPDATE - COMPLETED")
    logger.info(f"FII/DII: {'✓ Success' if fii_dii_success else '✗ Failed'}")
    logger.info(f"Delivery: {'✓ Success' if delivery_success else '✗ Failed'}")
    logger.info("=" * 60 + "\n")


def main():
    """Main entry point for NSE data updater."""
    parser = argparse.ArgumentParser(description='NSE Data Updater')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (instead of scheduling)'
    )
    parser.add_argument(
        '--hour',
        type=int,
        default=17,
        help='Hour to run daily update (default: 17, i.e., 5 PM)'
    )
    parser.add_argument(
        '--minute',
        type=int,
        default=30,
        help='Minute to run daily update (default: 30)'
    )

    args = parser.parse_args()

    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)

    if args.once:
        # Run once and exit
        logger.info("Running NSE data update once...")
        run_daily_update()
        logger.info("Done!")
        return

    # Schedule daily updates
    logger.info("Starting NSE Data Updater Service...")
    logger.info(f"Scheduled to run daily at {args.hour:02d}:{args.minute:02d}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    scheduler = BlockingScheduler()

    # Schedule daily update (default: 5:30 PM IST - after market close)
    scheduler.add_job(
        run_daily_update,
        CronTrigger(hour=args.hour, minute=args.minute),
        id='nse_daily_update',
        name='NSE Daily Data Update',
        replace_existing=True
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\nShutting down NSE Data Updater Service...")
        scheduler.shutdown()
        logger.info("Service stopped.")


if __name__ == '__main__':
    main()
