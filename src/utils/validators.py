"""
Input validation utilities.
"""
import re
import pandas as pd
from datetime import datetime
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def validate_stock_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Validate stock symbol format.

    Args:
        symbol: Stock symbol to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not symbol:
        return False, "Symbol cannot be empty"

    # Clean symbol
    symbol = symbol.strip().upper()

    # Check length
    if len(symbol) < 1 or len(symbol) > 20:
        return False, "Symbol must be between 1 and 20 characters"

    # Check format (alphanumeric, periods, hyphens, ampersands)
    pattern = r'^[A-Z0-9\.\-&]+$'
    if not re.match(pattern, symbol):
        return False, "Symbol can only contain letters, numbers, periods, hyphens, and ampersands"

    return True, ""


def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
    """
    Validate date range for data fetching.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if dates are provided
    if not start_date or not end_date:
        return False, "Both start and end dates are required"

    # Convert to datetime if needed
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return False, "Invalid start date format. Use YYYY-MM-DD"

    if isinstance(end_date, str):
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return False, "Invalid end date format. Use YYYY-MM-DD"

    # Check if start is before end
    if start_date >= end_date:
        return False, "Start date must be before end date"

    # Check if end date is not in future
    if end_date > datetime.now():
        return False, "End date cannot be in the future"

    # Check if date range is reasonable (at least 1 day)
    days_diff = (end_date - start_date).days
    if days_diff < 1:
        return False, "Date range must be at least 1 day"

    # Warn if date range is very long (>5 years)
    if days_diff > 1825:  # 5 years
        logger.warning(f"Large date range requested: {days_diff} days")

    return True, ""


def validate_ohlcv_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate OHLCV data quality.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty or None"

    # Check required columns
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"

    # Check for null values
    null_counts = df[required_columns].isnull().sum()
    if null_counts.any():
        null_cols = null_counts[null_counts > 0]
        return False, f"Null values found in columns: {null_cols.to_dict()}"

    # Check OHLC relationships
    invalid_ohlc = df[
        (df['high'] < df['low']) |
        (df['high'] < df['open']) |
        (df['high'] < df['close']) |
        (df['low'] > df['open']) |
        (df['low'] > df['close'])
    ]

    if not invalid_ohlc.empty:
        return False, f"Invalid OHLC relationships found in {len(invalid_ohlc)} rows"

    # Check for negative values
    negative = df[(df[required_columns] < 0).any(axis=1)]
    if not negative.empty:
        return False, f"Negative values found in {len(negative)} rows"

    # Check for zero volume (warning, not error)
    zero_volume = df[df['volume'] == 0]
    if not zero_volume.empty:
        logger.warning(f"Zero volume found in {len(zero_volume)} rows")

    return True, ""


def validate_strategy_params(params: dict, strategy_name: str) -> Tuple[bool, str]:
    """
    Validate strategy parameters.

    Args:
        params: Strategy parameters
        strategy_name: Name of the strategy

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not params:
        return False, "Parameters cannot be empty"

    # Strategy-specific validation
    if strategy_name == 'sma_crossover':
        if 'fast_period' not in params or 'slow_period' not in params:
            return False, "SMA Crossover requires fast_period and slow_period"

        if params['fast_period'] >= params['slow_period']:
            return False, "Fast period must be less than slow period"

        if params['fast_period'] < 1 or params['slow_period'] < 1:
            return False, "Periods must be positive integers"

    elif strategy_name == 'rsi':
        if 'period' not in params:
            return False, "RSI requires period parameter"

        if params['period'] < 2:
            return False, "RSI period must be at least 2"

        if 'oversold' in params and 'overbought' in params:
            if params['oversold'] >= params['overbought']:
                return False, "Oversold threshold must be less than overbought threshold"

    elif strategy_name == 'vwap':
        if 'period' not in params:
            return False, "VWAP requires period parameter"

        if params['period'] < 1:
            return False, "VWAP period must be positive"

    return True, ""


def validate_capital(capital: float) -> Tuple[bool, str]:
    """
    Validate initial capital for backtesting.

    Args:
        capital: Initial capital amount

    Returns:
        Tuple of (is_valid, error_message)
    """
    if capital is None:
        return False, "Capital cannot be None"

    if capital <= 0:
        return False, "Capital must be positive"

    if capital < 1000:
        return False, "Capital must be at least ₹1,000"

    if capital > 100000000:  # 10 crores
        logger.warning(f"Very large capital amount: ₹{capital:,.2f}")

    return True, ""
