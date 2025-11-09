"""
Base data adapter interface.

This is the KEY architectural component - all data adapters must implement this interface.
This allows swapping data sources without changing strategy code.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from datetime import datetime


class BaseDataAdapter(ABC):
    """
    Base interface for all data adapters.

    All adapters MUST return data in this standard format to ensure
    strategies work regardless of data source.
    """

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            start_date: Start date for data
            end_date: End date for data
            timeframe: Timeframe (1d, 1wk, 1mo, 1h, etc.)

        Returns:
            DataFrame with columns:
            - timestamp (datetime index)
            - open (float)
            - high (float)
            - low (float)
            - close (float)
            - volume (int)
            - source (str) - adapter name
            - timeframe (str)

        Raises:
            ValueError: If symbol is invalid or data not available
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Latest price or None if not available
        """
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol is valid.

        Args:
            symbol: Stock symbol

        Returns:
            True if symbol exists, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """
        Return list of supported timeframes for this adapter.

        Returns:
            List of timeframe strings (e.g., ['1d', '1wk', '1mo'])
        """
        pass

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol format (can be overridden if needed).

        Args:
            symbol: Stock symbol

        Returns:
            Normalized symbol (uppercase, trimmed)
        """
        return symbol.upper().strip()

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame has required columns.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_columns)
