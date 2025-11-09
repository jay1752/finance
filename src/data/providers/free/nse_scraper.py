"""
NSE India Web Scraper.

Fetches data from NSE India website that's unique to Indian markets:
- FII/DII data (Foreign/Domestic Institutional Investment)
- Delivery percentage
- Market-wide indicators

IMPORTANT: Be respectful of NSE servers:
- Add delays between requests
- Cache aggressively
- Use during off-market hours when possible
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
import json

logger = logging.getLogger(__name__)


class NSEScraper:
    """
    Scraper for NSE India website.

    NSE provides valuable data not available through Yahoo Finance:
    1. FII/DII activity - Institutional buying/selling
    2. Delivery percentage - Genuine buying vs speculation
    3. Market-wide statistics
    """

    BASE_URL = "https://www.nseindia.com"

    # API endpoints
    FII_DII_URL = f"{BASE_URL}/api/fiidiiTradeReact"
    EQUITY_META_URL = f"{BASE_URL}/api/equity-meta-info"
    MARKET_DATA_URL = f"{BASE_URL}/api/equity-stockIndices"

    def __init__(self):
        """Initialize NSE scraper with session."""
        self.session = requests.Session()

        # NSE requires proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

        # Initialize session with homepage visit (sets cookies)
        self._init_session()

    def _init_session(self):
        """
        Initialize session by visiting NSE homepage.

        NSE requires this to set cookies before API calls work.
        """
        try:
            logger.info("Initializing NSE session...")
            response = self.session.get(self.BASE_URL, timeout=10)

            if response.status_code == 200:
                logger.info("NSE session initialized successfully")
            else:
                logger.warning(f"NSE session init returned status {response.status_code}")

            # Small delay to be respectful
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error initializing NSE session: {e}")

    def get_fii_dii_data(self, date: datetime = None) -> dict:
        """
        Fetch FII/DII (Foreign/Domestic Institutional Investment) data.

        This shows how much money foreign and domestic institutions
        are putting into or taking out of the market.

        Args:
            date: Date to fetch (default: latest available)

        Returns:
            Dictionary with FII/DII data:
            {
                'date': '2024-01-15',
                'fii_gross_purchase': 5000.0,  # Crores
                'fii_gross_sale': 4500.0,
                'fii_net': 500.0,  # Positive = buying, Negative = selling
                'dii_gross_purchase': 3000.0,
                'dii_gross_sale': 2800.0,
                'dii_net': 200.0
            }
        """
        logger.info("Fetching FII/DII data from NSE...")

        try:
            response = self.session.get(
                self.FII_DII_URL,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if not data or len(data) == 0:
                logger.warning("No FII/DII data received from NSE")
                return None

            # Get latest data (first item)
            latest = data[0]

            result = {
                'date': latest.get('date', ''),
                'fii_gross_purchase': self._parse_number(latest.get('fii', {}).get('grossPurchase', 0)),
                'fii_gross_sale': self._parse_number(latest.get('fii', {}).get('grossSale', 0)),
                'fii_net': self._parse_number(latest.get('fii', {}).get('net', 0)),
                'dii_gross_purchase': self._parse_number(latest.get('dii', {}).get('grossPurchase', 0)),
                'dii_gross_sale': self._parse_number(latest.get('dii', {}).get('grossSale', 0)),
                'dii_net': self._parse_number(latest.get('dii', {}).get('net', 0)),
            }

            logger.info(f"FII/DII data fetched for {result['date']}")
            logger.info(f"FII Net: ₹{result['fii_net']:.2f} Cr, DII Net: ₹{result['dii_net']:.2f} Cr")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching FII/DII data: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing FII/DII data: {e}")
            return None

    def get_delivery_percentage(self, symbol: str) -> dict:
        """
        Get delivery percentage for a stock.

        Delivery percentage shows what portion of trades resulted in
        actual delivery (genuine buying) vs speculation (intraday).

        Higher delivery % (>60%) = Strong genuine buying
        Lower delivery % (<40%) = More speculation/intraday trading

        Args:
            symbol: NSE stock symbol (without .NS)

        Returns:
            Dictionary with delivery data:
            {
                'symbol': 'RELIANCE',
                'date': '2024-01-15',
                'delivery_quantity': 1000000,
                'traded_quantity': 2000000,
                'delivery_percentage': 50.0
            }
        """
        logger.info(f"Fetching delivery percentage for {symbol}...")

        try:
            # NSE uses uppercase symbols
            symbol = symbol.upper().replace('.NS', '').replace('.BO', '')

            url = f"{self.EQUITY_META_URL}?symbol={symbol}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Delivery data is in 'securityWiseDP' section
            if 'securityWiseDP' not in data:
                logger.warning(f"No delivery data found for {symbol}")
                return None

            delivery_data = data['securityWiseDP']

            result = {
                'symbol': symbol,
                'date': delivery_data.get('tradedDate', ''),
                'delivery_quantity': int(delivery_data.get('deliveryQuantity', 0)),
                'traded_quantity': int(delivery_data.get('quantityTraded', 0)),
                'delivery_percentage': float(delivery_data.get('deliveryToTradedQuantity', 0)),
            }

            logger.info(
                f"{symbol} delivery: {result['delivery_percentage']:.2f}% "
                f"({result['delivery_quantity']:,} / {result['traded_quantity']:,})"
            )

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching delivery data for {symbol}: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing delivery data for {symbol}: {e}")
            return None

    def get_market_status(self) -> dict:
        """
        Get current market status.

        Returns:
            Dictionary with market status:
            {
                'market_status': 'Open' | 'Closed',
                'timestamp': '2024-01-15 14:30:00'
            }
        """
        try:
            url = f"{self.BASE_URL}/api/marketStatus"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Parse market status
            if 'marketState' in data:
                for market in data['marketState']:
                    if market.get('market') == 'Capital Market':
                        return {
                            'market_status': market.get('marketStatus', 'Unknown'),
                            'timestamp': datetime.now().isoformat()
                        }

            return None

        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return None

    def get_index_data(self, index_name: str = "NIFTY 50") -> dict:
        """
        Get index data (NIFTY 50, NIFTY Bank, etc.).

        Args:
            index_name: Index name (default: NIFTY 50)

        Returns:
            Dictionary with index data
        """
        try:
            url = f"{self.MARKET_DATA_URL}?index={index_name}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'data' in data and len(data['data']) > 0:
                index_data = data['data'][0]

                return {
                    'name': index_data.get('index', ''),
                    'last_price': float(index_data.get('last', 0)),
                    'change': float(index_data.get('change', 0)),
                    'percent_change': float(index_data.get('percentChange', 0)),
                    'timestamp': index_data.get('timeVal', '')
                }

            return None

        except Exception as e:
            logger.error(f"Error fetching index data: {e}")
            return None

    def _parse_number(self, value) -> float:
        """
        Parse number from various formats (string with commas, etc.).

        Args:
            value: Value to parse

        Returns:
            Float value
        """
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        # Remove commas and parse
        try:
            return float(str(value).replace(',', ''))
        except ValueError:
            return 0.0

    def close(self):
        """Close the session."""
        self.session.close()
        logger.info("NSE scraper session closed")


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    scraper = NSEScraper()

    # Test FII/DII data
    print("=" * 60)
    print("FII/DII Data")
    print("=" * 60)
    fii_dii = scraper.get_fii_dii_data()
    if fii_dii:
        for key, value in fii_dii.items():
            print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("Delivery Percentage - RELIANCE")
    print("=" * 60)
    delivery = scraper.get_delivery_percentage('RELIANCE')
    if delivery:
        for key, value in delivery.items():
            print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("Market Status")
    print("=" * 60)
    status = scraper.get_market_status()
    if status:
        for key, value in status.items():
            print(f"{key}: {value}")

    scraper.close()
