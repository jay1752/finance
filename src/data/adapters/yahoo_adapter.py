"""
Yahoo Finance data adapter.

Provides FREE daily/weekly/monthly historical data for Indian stocks.
"""
import yfinance as yf
from .base_adapter import BaseDataAdapter
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class YahooFinanceAdapter(BaseDataAdapter):
    """Yahoo Finance data adapter - FREE daily data."""

    def __init__(self):
        self.name = "yahoo_finance"
        # Added 1h and 4h for multi-timeframe analysis
        # Note: Intraday data (1h, 4h) is limited to ~730 days by Yahoo Finance
        self.supported_timeframes = ['1h', '4h', '1d', '1wk', '1mo']

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch historical data from Yahoo Finance.

        Args:
            symbol: Stock symbol (will be converted to Yahoo format)
            start_date: Start date
            end_date: End date
            timeframe: Timeframe (1h, 4h, 1d, 1wk, 1mo)
                Note: 1h and 4h data limited to ~730 days by Yahoo Finance

        Returns:
            DataFrame with standardized OHLCV columns
        """
        try:
            # Validate timeframe
            if timeframe not in self.supported_timeframes:
                raise ValueError(
                    f"Timeframe '{timeframe}' not supported. "
                    f"Supported: {self.supported_timeframes}"
                )

            # Format symbol for Yahoo Finance
            yahoo_symbol = self._format_symbol(symbol)

            logger.info(f"Fetching data for {yahoo_symbol} from {start_date} to {end_date}")

            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=timeframe
            )

            if df.empty:
                logger.warning(f"No data found for {yahoo_symbol}")
                return pd.DataFrame()

            # Normalize column names to lowercase
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Add metadata columns
            df['source'] = self.name
            df['timeframe'] = timeframe

            # Select only required columns
            columns = ['open', 'high', 'low', 'close', 'volume', 'source', 'timeframe']
            df = df[columns]

            # Validate data
            if not self.validate_data(df):
                raise ValueError(f"Invalid data format for {yahoo_symbol}")

            logger.info(f"Successfully fetched {len(df)} rows for {yahoo_symbol}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise

    def get_current_price(self, symbol: str) -> float:
        """
        Get latest price for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Latest close price or None if error
        """
        try:
            yahoo_symbol = self._format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period='1d')

            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None

        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate that symbol exists in Yahoo Finance.

        Args:
            symbol: Stock symbol

        Returns:
            True if symbol exists, False otherwise
        """
        try:
            yahoo_symbol = self._format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period='1d')
            return not data.empty

        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False

    def get_supported_timeframes(self) -> list:
        """Return list of supported timeframes."""
        return self.supported_timeframes

    def _format_symbol(self, symbol: str) -> str:
        """
        Convert symbol to Yahoo Finance format.

        Indian stocks on Yahoo Finance use:
        - NSE: SYMBOL.NS (e.g., RELIANCE.NS)
        - BSE: SYMBOL.BO (e.g., RELIANCE.BO)

        Args:
            symbol: Stock symbol

        Returns:
            Yahoo Finance formatted symbol
        """
        symbol = self.normalize_symbol(symbol)

        # If already has exchange suffix, return as-is
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return symbol

        # Default to NSE
        return f"{symbol}.NS"

    def get_company_info(self, symbol: str) -> dict:
        """
        Get company information (bonus method).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company info or None
        """
        try:
            yahoo_symbol = self._format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info

            return {
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
            }

        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return None
