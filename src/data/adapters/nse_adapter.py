"""
NSE India Data Adapter.

This adapter supplements primary OHLCV data with NSE-specific metrics:
- FII/DII (Foreign/Domestic Institutional Investment)
- Delivery percentage
- Market indicators

Note: This does NOT provide primary OHLCV data. Use Yahoo Finance adapter for that.
"""
import logging
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd

from .base_adapter import BaseDataAdapter
from ..providers.free.nse_scraper import NSEScraper

logger = logging.getLogger(__name__)


class NSEAdapter(BaseDataAdapter):
    """
    Adapter for NSE India supplementary data.

    Provides NSE-specific metrics that complement OHLCV data:
    - FII/DII activity (institutional buying/selling)
    - Delivery percentage (genuine buying vs speculation)
    - Market-wide indicators
    """

    name = "nse"

    def __init__(self):
        """Initialize NSE adapter with scraper."""
        super().__init__()
        self.scraper = NSEScraper()
        logger.info("NSE adapter initialized")

    def get_historical_data(self, symbol: str, start_date: datetime,
                          end_date: datetime, timeframe: str = '1d') -> pd.DataFrame:
        """
        NSE does not provide historical OHLCV data through public APIs.

        Use Yahoo Finance adapter for OHLCV data instead.
        This method is implemented to satisfy the interface but will raise an error.

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            timeframe: Time interval

        Returns:
            Empty DataFrame (NSE doesn't provide OHLCV data)
        """
        logger.warning(f"NSE adapter does not provide OHLCV data. Use Yahoo Finance adapter instead.")

        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'source', 'timeframe'])

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price from NSE.

        Note: NSE doesn't provide real-time price through public APIs.
        Use Yahoo Finance adapter for this instead.

        Args:
            symbol: Stock symbol

        Returns:
            None (not available through NSE public API)
        """
        logger.warning("Current price not available through NSE adapter. Use Yahoo Finance adapter.")
        return None

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol exists on NSE.

        Args:
            symbol: Stock symbol

        Returns:
            True if symbol appears to be valid
        """
        # Basic validation - just check if it's a non-empty string
        # More sophisticated validation would require NSE symbol lookup
        symbol = symbol.upper().strip()
        return len(symbol) > 0 and symbol.isalpha()

    def get_supported_timeframes(self) -> List[str]:
        """
        Get supported timeframes.

        NSE adapter doesn't provide OHLCV data, so this returns empty list.

        Returns:
            Empty list (NSE is for supplementary data only)
        """
        return []  # NSE adapter doesn't provide OHLCV data

    def get_fii_dii_data(self, date: datetime = None) -> Optional[Dict]:
        """
        Get FII/DII (Foreign/Domestic Institutional Investment) data.

        This shows institutional money flow - critical for Indian markets.

        Args:
            date: Date to fetch (default: latest available)

        Returns:
            Dictionary with FII/DII data:
            {
                'date': '2024-11-07',
                'fii_net': 500.0,  # Crores (positive = buying)
                'dii_net': 200.0,  # Crores
                'fii_gross_purchase': 5000.0,
                'fii_gross_sale': 4500.0,
                'dii_gross_purchase': 3000.0,
                'dii_gross_sale': 2800.0
            }
        """
        try:
            logger.info("Fetching FII/DII data from NSE...")
            data = self.scraper.get_fii_dii_data(date)

            if data:
                logger.info(f"FII/DII data retrieved for {data['date']}")
                return data
            else:
                logger.warning("No FII/DII data available")
                return None

        except Exception as e:
            logger.error(f"Error fetching FII/DII data: {e}")
            return None

    def get_delivery_percentage(self, symbol: str) -> Optional[Dict]:
        """
        Get delivery percentage for a stock.

        Delivery % shows genuine buying vs speculation:
        - High delivery % (>60%): Strong genuine buying
        - Low delivery % (<40%): More speculation/intraday trading

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')

        Returns:
            Dictionary with delivery data:
            {
                'symbol': 'RELIANCE',
                'date': '2024-11-07',
                'delivery_quantity': 1000000,
                'traded_quantity': 2000000,
                'delivery_percentage': 50.0
            }
        """
        try:
            logger.info(f"Fetching delivery percentage for {symbol}...")
            data = self.scraper.get_delivery_percentage(symbol)

            if data:
                logger.info(
                    f"{symbol} delivery: {data['delivery_percentage']:.2f}% "
                    f"on {data['date']}"
                )
                return data
            else:
                logger.warning(f"No delivery data available for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Error fetching delivery percentage for {symbol}: {e}")
            return None

    def get_market_status(self) -> Optional[Dict]:
        """
        Get current market status.

        Returns:
            Dictionary with market status:
            {
                'market_status': 'Open' | 'Closed',
                'timestamp': '2024-11-07 14:30:00'
            }
        """
        try:
            logger.info("Fetching market status...")
            status = self.scraper.get_market_status()

            if status:
                logger.info(f"Market is {status['market_status']}")
                return status
            else:
                logger.warning("Could not fetch market status")
                return None

        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return None

    def get_index_data(self, index_name: str = "NIFTY 50") -> Optional[Dict]:
        """
        Get index data (NIFTY 50, NIFTY Bank, etc.).

        Args:
            index_name: Index name (default: 'NIFTY 50')

        Returns:
            Dictionary with index data:
            {
                'name': 'NIFTY 50',
                'last_price': 19500.50,
                'change': 150.25,
                'percent_change': 0.77,
                'timestamp': '07-Nov-2024 15:30:00'
            }
        """
        try:
            logger.info(f"Fetching {index_name} data...")
            data = self.scraper.get_index_data(index_name)

            if data:
                logger.info(
                    f"{index_name}: {data['last_price']} "
                    f"({data['percent_change']:+.2f}%)"
                )
                return data
            else:
                logger.warning(f"Could not fetch data for {index_name}")
                return None

        except Exception as e:
            logger.error(f"Error fetching index data: {e}")
            return None

    def enrich_stock_data(self, symbol: str, ohlcv_data: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich OHLCV data with NSE-specific metrics.

        Adds delivery percentage as a new column to existing price data.

        Args:
            symbol: Stock symbol
            ohlcv_data: DataFrame with OHLCV data from Yahoo Finance

        Returns:
            Enhanced DataFrame with additional NSE metrics
        """
        try:
            logger.info(f"Enriching {symbol} data with NSE metrics...")

            # Get delivery percentage
            delivery_data = self.get_delivery_percentage(symbol)

            if delivery_data and not ohlcv_data.empty:
                # Add delivery percentage to the latest row
                delivery_date = pd.to_datetime(delivery_data['date'])

                # Find matching date in OHLCV data
                if delivery_date in ohlcv_data.index:
                    ohlcv_data.loc[delivery_date, 'delivery_pct'] = delivery_data['delivery_percentage']
                    ohlcv_data.loc[delivery_date, 'delivery_qty'] = delivery_data['delivery_quantity']
                    ohlcv_data.loc[delivery_date, 'traded_qty'] = delivery_data['traded_quantity']

                    logger.info(f"Added delivery data for {delivery_date.date()}")
                else:
                    logger.warning(f"Delivery date {delivery_date.date()} not found in OHLCV data")

            return ohlcv_data

        except Exception as e:
            logger.error(f"Error enriching data with NSE metrics: {e}")
            return ohlcv_data  # Return original data on error

    def close(self):
        """Close the NSE scraper session."""
        if self.scraper:
            self.scraper.close()
            logger.info("NSE adapter closed")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Example usage
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    adapter = NSEAdapter()

    print("=" * 60)
    print("Testing NSE Adapter")
    print("=" * 60)

    # Test 1: FII/DII data
    print("\n1. FII/DII Data:")
    print("-" * 60)
    fii_dii = adapter.get_fii_dii_data()
    if fii_dii:
        print(f"Date: {fii_dii['date']}")
        print(f"FII Net: ₹{fii_dii['fii_net']:.2f} Cr")
        print(f"DII Net: ₹{fii_dii['dii_net']:.2f} Cr")

    # Test 2: Delivery percentage
    print("\n2. Delivery Percentage (RELIANCE):")
    print("-" * 60)
    delivery = adapter.get_delivery_percentage('RELIANCE')
    if delivery:
        print(f"Date: {delivery['date']}")
        print(f"Delivery %: {delivery['delivery_percentage']:.2f}%")
        print(f"Delivery Qty: {delivery['delivery_quantity']:,}")
        print(f"Traded Qty: {delivery['traded_quantity']:,}")

    # Test 3: Market status
    print("\n3. Market Status:")
    print("-" * 60)
    status = adapter.get_market_status()
    if status:
        print(f"Status: {status['market_status']}")
        print(f"Time: {status['timestamp']}")

    # Test 4: Index data
    print("\n4. NIFTY 50 Index:")
    print("-" * 60)
    index = adapter.get_index_data("NIFTY 50")
    if index:
        print(f"Index: {index['name']}")
        print(f"Price: {index['last_price']:.2f}")
        print(f"Change: {index['change']:+.2f} ({index['percent_change']:+.2f}%)")

    adapter.close()
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)
