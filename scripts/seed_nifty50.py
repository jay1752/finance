"""
Seed NIFTY 50 stocks into the database.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_context
from src.data.models.stock import Stock
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# NIFTY 50 stocks (as of 2024)
NIFTY50_STOCKS = [
    {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd.', 'sector': 'IT', 'industry': 'IT Services'},
    {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd.', 'sector': 'Financials', 'industry': 'Banking'},
    {'symbol': 'INFY', 'name': 'Infosys Ltd.', 'sector': 'IT', 'industry': 'IT Services'},
    {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd.', 'sector': 'Financials', 'industry': 'Banking'},
    {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd.', 'sector': 'FMCG', 'industry': 'Consumer Goods'},
    {'symbol': 'ITC', 'name': 'ITC Ltd.', 'sector': 'FMCG', 'industry': 'Diversified'},
    {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Financials', 'industry': 'Banking'},
    {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd.', 'sector': 'Telecom', 'industry': 'Telecommunications'},
    {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Ltd.', 'sector': 'Financials', 'industry': 'Banking'},
    {'symbol': 'LT', 'name': 'Larsen & Toubro Ltd.', 'sector': 'Industrials', 'industry': 'Engineering'},
    {'symbol': 'AXISBANK', 'name': 'Axis Bank Ltd.', 'sector': 'Financials', 'industry': 'Banking'},
    {'symbol': 'ASIANPAINT', 'name': 'Asian Paints Ltd.', 'sector': 'Materials', 'industry': 'Paints'},
    {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Ltd.', 'sector': 'Auto', 'industry': 'Automobiles'},
    {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical Industries Ltd.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    {'symbol': 'TITAN', 'name': 'Titan Company Ltd.', 'sector': 'Consumer Goods', 'industry': 'Jewelry & Watches'},
    {'symbol': 'ULTRACEMCO', 'name': 'UltraTech Cement Ltd.', 'sector': 'Materials', 'industry': 'Cement'},
    {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance Ltd.', 'sector': 'Financials', 'industry': 'NBFC'},
    {'symbol': 'WIPRO', 'name': 'Wipro Ltd.', 'sector': 'IT', 'industry': 'IT Services'},
    {'symbol': 'NESTLEIND', 'name': 'Nestle India Ltd.', 'sector': 'FMCG', 'industry': 'Food Products'},
    {'symbol': 'HCLTECH', 'name': 'HCL Technologies Ltd.', 'sector': 'IT', 'industry': 'IT Services'},
    {'symbol': 'TECHM', 'name': 'Tech Mahindra Ltd.', 'sector': 'IT', 'industry': 'IT Services'},
    {'symbol': 'ONGC', 'name': 'Oil & Natural Gas Corporation Ltd.', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Ltd.', 'sector': 'Auto', 'industry': 'Automobiles'},
    {'symbol': 'NTPC', 'name': 'NTPC Ltd.', 'sector': 'Utilities', 'industry': 'Power Generation'},
    {'symbol': 'TATASTEEL', 'name': 'Tata Steel Ltd.', 'sector': 'Materials', 'industry': 'Steel'},
    {'symbol': 'POWERGRID', 'name': 'Power Grid Corporation of India Ltd.', 'sector': 'Utilities', 'industry': 'Power Transmission'},
    {'symbol': 'M&M', 'name': 'Mahindra & Mahindra Ltd.', 'sector': 'Auto', 'industry': 'Automobiles'},
    {'symbol': 'JSWSTEEL', 'name': 'JSW Steel Ltd.', 'sector': 'Materials', 'industry': 'Steel'},
    {'symbol': 'ADANIPORTS', 'name': 'Adani Ports and Special Economic Zone Ltd.', 'sector': 'Industrials', 'industry': 'Ports'},
    {'symbol': 'BAJAJFINSV', 'name': 'Bajaj Finserv Ltd.', 'sector': 'Financials', 'industry': 'NBFC'},
    {'symbol': 'DIVISLAB', 'name': 'Divi\'s Laboratories Ltd.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    {'symbol': 'BRITANNIA', 'name': 'Britannia Industries Ltd.', 'sector': 'FMCG', 'industry': 'Food Products'},
    {'symbol': 'INDUSINDBK', 'name': 'IndusInd Bank Ltd.', 'sector': 'Financials', 'industry': 'Banking'},
    {'symbol': 'DRREDDY', 'name': 'Dr. Reddy\'s Laboratories Ltd.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    {'symbol': 'COALINDIA', 'name': 'Coal India Ltd.', 'sector': 'Energy', 'industry': 'Coal'},
    {'symbol': 'CIPLA', 'name': 'Cipla Ltd.', 'sector': 'Healthcare', 'industry': 'Pharmaceuticals'},
    {'symbol': 'EICHERMOT', 'name': 'Eicher Motors Ltd.', 'sector': 'Auto', 'industry': 'Automobiles'},
    {'symbol': 'GRASIM', 'name': 'Grasim Industries Ltd.', 'sector': 'Materials', 'industry': 'Diversified'},
    {'symbol': 'HINDALCO', 'name': 'Hindalco Industries Ltd.', 'sector': 'Materials', 'industry': 'Aluminum'},
    {'symbol': 'HEROMOTOCO', 'name': 'Hero MotoCorp Ltd.', 'sector': 'Auto', 'industry': 'Automobiles'},
    {'symbol': 'APOLLOHOSP', 'name': 'Apollo Hospitals Enterprise Ltd.', 'sector': 'Healthcare', 'industry': 'Hospitals'},
    {'symbol': 'BAJAJ-AUTO', 'name': 'Bajaj Auto Ltd.', 'sector': 'Auto', 'industry': 'Automobiles'},
    {'symbol': 'TATACONSUM', 'name': 'Tata Consumer Products Ltd.', 'sector': 'FMCG', 'industry': 'Consumer Goods'},
    {'symbol': 'BPCL', 'name': 'Bharat Petroleum Corporation Ltd.', 'sector': 'Energy', 'industry': 'Oil & Gas'},
    {'symbol': 'ADANIENT', 'name': 'Adani Enterprises Ltd.', 'sector': 'Industrials', 'industry': 'Diversified'},
    {'symbol': 'SBILIFE', 'name': 'SBI Life Insurance Company Ltd.', 'sector': 'Financials', 'industry': 'Insurance'},
    {'symbol': 'HDFCLIFE', 'name': 'HDFC Life Insurance Company Ltd.', 'sector': 'Financials', 'industry': 'Insurance'},
    {'symbol': 'SHRIRAMFIN', 'name': 'Shriram Finance Ltd.', 'sector': 'Financials', 'industry': 'NBFC'},
    {'symbol': 'LTIM', 'name': 'LTIMindtree Ltd.', 'sector': 'IT', 'industry': 'IT Services'},
]


def seed_nifty50():
    """Seed NIFTY 50 stocks into database."""
    logger.info("=" * 50)
    logger.info("SEEDING NIFTY 50 STOCKS")
    logger.info("=" * 50)

    try:
        with get_db_context() as db:
            added_count = 0
            updated_count = 0
            skipped_count = 0

            for stock_data in NIFTY50_STOCKS:
                try:
                    # Check if stock already exists
                    existing = db.query(Stock).filter_by(symbol=stock_data['symbol']).first()

                    if existing:
                        # Update existing stock
                        for key, value in stock_data.items():
                            setattr(existing, key, value)

                        existing.exchange = 'NSE'
                        existing.is_active = True

                        updated_count += 1
                        logger.info(f"Updated: {stock_data['symbol']} - {stock_data['name']}")

                    else:
                        # Create new stock
                        stock = Stock(
                            **stock_data,
                            exchange='NSE',
                            is_active=True
                        )

                        db.add(stock)
                        added_count += 1
                        logger.info(f"Added: {stock_data['symbol']} - {stock_data['name']}")

                except Exception as e:
                    logger.error(f"Error processing {stock_data['symbol']}: {e}")
                    skipped_count += 1

            # Commit all changes
            db.commit()

            logger.info("=" * 50)
            logger.info("SEEDING COMPLETED")
            logger.info(f"Added: {added_count} stocks")
            logger.info(f"Updated: {updated_count} stocks")
            logger.info(f"Skipped: {skipped_count} stocks")
            logger.info(f"Total: {added_count + updated_count + skipped_count} stocks processed")
            logger.info("=" * 50)

            # Verify
            total_stocks = db.query(Stock).count()
            logger.info(f"Total stocks in database: {total_stocks}")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == '__main__':
    seed_nifty50()
