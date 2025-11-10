"""
5paisa Data Adapter - Live and historical data from 5paisa broker.

Provides:
- Real-time price quotes
- Historical OHLCV data (better than Yahoo for Indian stocks)
- Intraday data (1min, 5min, 15min, 30min, 1hr)
- Market depth
- Live streaming quotes

Note: Requires 5paisa API credentials in .env file
"""
from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

from ..adapters.base_adapter import BaseDataAdapter
from ...brokers.config import BrokerConfig

logger = logging.getLogger(__name__)


class FivePaisaAdapter(BaseDataAdapter):
    """
    5paisa broker data adapter.

    Provides superior data quality for Indian stocks compared to Yahoo Finance:
    - Real-time quotes
    - Accurate corporate actions
    - Better intraday data
    - NSE/BSE both supported
    """

    def __init__(self, config: Optional[BrokerConfig] = None):
        """
        Initialize 5paisa adapter.

        Args:
            config: BrokerConfig with credentials (loads from env if not provided)
        """
        self.name = "5paisa"
        self.supported_timeframes = ['1min', '5min', '15min', '30min', '1h', '1d']

        # Load config
        if config is None:
            try:
                config = BrokerConfig.from_env()
            except ValueError as e:
                logger.error(f"Failed to load 5paisa credentials: {e}")
                logger.info("5paisa adapter initialized without credentials (data fetching will fail)")
                self.client = None
                self.config = None
                return

        self.config = config

        # Initialize 5paisa client
        try:
            creds = config.to_5paisa_creds()
            self.client = FivePaisaClient(cred=creds)

            # Login
            self.client.login()
            logger.info("✅ 5paisa client connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to 5paisa: {e}")
            self.client = None

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch historical data from 5paisa.

        Args:
            symbol: Stock symbol (NSE format, e.g., 'RELIANCE')
            start_date: Start date
            end_date: End date
            timeframe: Timeframe ('1min', '5min', '15min', '30min', '1h', '1d')

        Returns:
            DataFrame with OHLCV data
        """
        if not self.client:
            raise RuntimeError("5paisa client not initialized. Check credentials.")

        try:
            # Validate timeframe
            if timeframe not in self.supported_timeframes:
                raise ValueError(
                    f"Timeframe '{timeframe}' not supported. "
                    f"Supported: {self.supported_timeframes}"
                )

            # Format symbol for 5paisa
            scrip_code = self._get_scrip_code(symbol)

            # Map timeframe to 5paisa format
            interval_map = {
                '1min': 1,
                '5min': 5,
                '15min': 15,
                '30min': 30,
                '1h': 60,
                '1d': 1440  # daily
            }

            interval = interval_map[timeframe]

            logger.info(f"Fetching {symbol} data from {start_date} to {end_date} ({timeframe})")

            # Fetch data from 5paisa
            # Note: 5paisa uses different methods for intraday vs daily
            if timeframe == '1d':
                # Daily data
                data = self.client.historical_data(
                    Exch='N',  # NSE
                    ExchangeSegment='C',  # Cash
                    ScripCode=scrip_code,
                    time=interval,
                    From=start_date.strftime('%Y-%m-%d'),
                    To=end_date.strftime('%Y-%m-%d')
                )
            else:
                # Intraday data
                data = self.client.historical_data(
                    Exch='N',
                    ExchangeSegment='C',
                    ScripCode=scrip_code,
                    time=interval,
                    From=start_date.strftime('%Y-%m-%d'),
                    To=end_date.strftime('%Y-%m-%d')
                )

            if data is None or data.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()

            # Normalize column names
            df = data.rename(columns={
                'Datetime': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Set date as index
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)

            # Add metadata
            df['source'] = self.name
            df['timeframe'] = timeframe

            # Select required columns
            columns = ['open', 'high', 'low', 'close', 'volume', 'source', 'timeframe']
            df = df[[col for col in columns if col in df.columns]]

            # Validate
            if not self.validate_data(df):
                logger.warning(f"Data validation failed for {symbol}")

            logger.info(f"Successfully fetched {len(df)} rows for {symbol}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol (real-time).

        Args:
            symbol: Stock symbol

        Returns:
            Latest price or None
        """
        if not self.client:
            logger.error("5paisa client not initialized")
            return None

        try:
            scrip_code = self._get_scrip_code(symbol)

            # Get market feed
            req_list = [{
                "Exch": "N",
                "ExchangeType": "C",
                "ScripCode": scrip_code
            }]

            market_feed = self.client.fetch_market_feed(req_list)

            if market_feed and len(market_feed) > 0:
                # Get LTP (Last Traded Price)
                ltp = market_feed[0].get('LastRate', None)

                if ltp:
                    logger.info(f"{symbol}: ₹{ltp}")
                    return float(ltp)

            logger.warning(f"Could not fetch price for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_live_quotes(self, symbols: List[str]) -> Dict[str, dict]:
        """
        Get live quotes for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary with symbol -> quote data
        """
        if not self.client:
            raise RuntimeError("5paisa client not initialized")

        try:
            # Build request list
            req_list = []
            for symbol in symbols:
                scrip_code = self._get_scrip_code(symbol)
                req_list.append({
                    "Exch": "N",
                    "ExchangeType": "C",
                    "ScripCode": scrip_code
                })

            # Fetch market feed
            market_feed = self.client.fetch_market_feed(req_list)

            # Parse results
            quotes = {}
            for i, symbol in enumerate(symbols):
                if i < len(market_feed):
                    feed = market_feed[i]
                    quotes[symbol] = {
                        'ltp': feed.get('LastRate'),
                        'open': feed.get('OpenRate'),
                        'high': feed.get('High'),
                        'low': feed.get('Low'),
                        'close': feed.get('PClose'),  # Previous close
                        'volume': feed.get('TotalQty'),
                        'bid': feed.get('BidRate'),
                        'ask': feed.get('AskRate'),
                        'change': feed.get('Chg'),
                        'change_pct': feed.get('ChgPcnt'),
                    }

            return quotes

        except Exception as e:
            logger.error(f"Error fetching live quotes: {e}")
            return {}

    def get_market_depth(self, symbol: str) -> Optional[dict]:
        """
        Get market depth (order book) for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with bid/ask depth
        """
        if not self.client:
            return None

        try:
            scrip_code = self._get_scrip_code(symbol)

            req_list = [{
                "Exch": "N",
                "ExchangeType": "C",
                "ScripCode": scrip_code
            }]

            depth = self.client.fetch_market_depth(req_list)

            if depth and len(depth) > 0:
                return depth[0]

            return None

        except Exception as e:
            logger.error(f"Error fetching market depth for {symbol}: {e}")
            return None

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate that symbol exists.

        Args:
            symbol: Stock symbol

        Returns:
            True if valid, False otherwise
        """
        try:
            scrip_code = self._get_scrip_code(symbol)
            return scrip_code is not None
        except:
            return False

    def get_supported_timeframes(self) -> list:
        """Return list of supported timeframes."""
        return self.supported_timeframes

    def _get_scrip_code(self, symbol: str) -> int:
        """
        Get 5paisa scrip code for a symbol.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')

        Returns:
            Scrip code (integer)

        Note: 5paisa uses scrip codes instead of symbols.
              This is a simplified mapping. In production, use 5paisa's
              scrip master file or API.
        """
        # Common NSE scrip codes (simplified mapping)
        # In production, fetch from 5paisa scrip master
        scrip_map = {
            'RELIANCE': 2885,
            'TCS': 11536,
            'INFY': 1594,
            'HDFCBANK': 1333,
            'ICICIBANK': 4963,
            'WIPRO': 3787,
            'ITC': 1660,
            'SBIN': 3045,
            'TATAMOTORS': 3456,
            'MARUTI': 10999,
            'BAJFINANCE': 16675,
            'KOTAKBANK': 1922,
            'AXISBANK': 5900,
            'HINDUNILVR': 1394,
            'BHARTIARTL': 10604,
        }

        symbol_upper = symbol.upper().strip()

        if symbol_upper in scrip_map:
            return scrip_map[symbol_upper]

        # If not in map, try to fetch from scrip master
        logger.warning(
            f"Scrip code not found for {symbol}. "
            f"Add to scrip_map or use 5paisa scrip master."
        )

        # Return None or raise error
        raise ValueError(
            f"Scrip code not found for {symbol}. "
            f"Please add to scrip_map in fivepaisa_adapter.py"
        )

    def get_scrip_master(self) -> pd.DataFrame:
        """
        Get complete scrip master from 5paisa.

        Returns:
            DataFrame with all available scrips
        """
        if not self.client:
            raise RuntimeError("5paisa client not initialized")

        try:
            # Fetch scrip master
            scrips = self.client.get_scrip_master()

            if scrips is not None and not scrips.empty:
                logger.info(f"Fetched {len(scrips)} scrips from master")
                return scrips

            logger.warning("No scrips returned from master")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching scrip master: {e}")
            return pd.DataFrame()

    def close(self):
        """Close connection to 5paisa."""
        if self.client:
            # 5paisa client doesn't have explicit close
            logger.info("5paisa adapter closed")
            self.client = None
