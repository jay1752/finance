"""
Application constants and configurations.
"""

# Timeframe configurations
TIMEFRAME_CONFIG = {
    '1m': {
        'name': '1 Minute',
        'interval_seconds': 60,
        'candles_per_day': 375,
        'min_data_points': 100,
        'use_cases': ['scalping', 'high_frequency']
    },
    '5m': {
        'name': '5 Minutes',
        'interval_seconds': 300,
        'candles_per_day': 75,
        'min_data_points': 100,
        'use_cases': ['intraday', 'scalping']
    },
    '15m': {
        'name': '15 Minutes',
        'interval_seconds': 900,
        'candles_per_day': 25,
        'min_data_points': 50,
        'use_cases': ['intraday', 'day_trading']
    },
    '1h': {
        'name': '1 Hour',
        'interval_seconds': 3600,
        'candles_per_day': 6,
        'min_data_points': 50,
        'use_cases': ['swing', 'intraday']
    },
    '1d': {
        'name': '1 Day',
        'interval_seconds': 86400,
        'candles_per_day': 1,
        'min_data_points': 100,
        'use_cases': ['swing', 'positional', 'value_investing']
    },
    '1wk': {
        'name': '1 Week',
        'interval_seconds': 604800,
        'candles_per_day': 0.2,
        'min_data_points': 52,
        'use_cases': ['swing', 'trend_following']
    },
    '1mo': {
        'name': '1 Month',
        'interval_seconds': 2592000,
        'candles_per_day': 0.033,
        'min_data_points': 24,
        'use_cases': ['long_term', 'value_investing']
    }
}

# Indian market trading hours
MARKET_HOURS = {
    'open': '09:15',
    'close': '15:30',
    'pre_open_start': '09:00',
    'pre_open_end': '09:08'
}

# NSE/BSE exchanges
EXCHANGES = {
    'NSE': 'National Stock Exchange',
    'BSE': 'Bombay Stock Exchange'
}

# Signal types
SIGNAL_TYPES = {
    'BUY': 'Buy Signal',
    'SELL': 'Sell Signal',
    'HOLD': 'Hold/No Action'
}

# Common NIFTY indices
INDICES = {
    '^NSEI': 'NIFTY 50',
    '^NSEBANK': 'NIFTY Bank',
    '^CNXIT': 'NIFTY IT',
    '^CNXAUTO': 'NIFTY Auto'
}

# Default parameters
DEFAULT_BACKTEST_CAPITAL = 100000  # ₹1 Lakh
DEFAULT_COMMISSION_PCT = 0.0003  # 0.03% per trade

# Data validation thresholds
DATA_QUALITY_THRESHOLDS = {
    'min_volume': 1000,  # Minimum volume per candle
    'max_price_change_pct': 20,  # Max price change % per day
    'max_missing_data_pct': 5  # Max % of missing data points
}
