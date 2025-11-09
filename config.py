"""
Central configuration management for the application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/market_analysis')

    # Data Sources
    YAHOO_FINANCE_ENABLED = os.getenv('YAHOO_FINANCE_ENABLED', 'true').lower() == 'true'
    NSE_SCRAPING_ENABLED = os.getenv('NSE_SCRAPING_ENABLED', 'false').lower() == 'true'

    # API Keys
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
    UPSTOX_API_KEY = os.getenv('UPSTOX_API_KEY', '')
    UPSTOX_API_SECRET = os.getenv('UPSTOX_API_SECRET', '')
    ZERODHA_API_KEY = os.getenv('ZERODHA_API_KEY', '')
    ZERODHA_API_SECRET = os.getenv('ZERODHA_API_SECRET', '')

    # Application Settings
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DATA_UPDATE_TIME = os.getenv('DATA_UPDATE_TIME', '17:00')

    # Redis (Phase 3)
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    # Rate Limiting (requests per hour/day)
    RATE_LIMITS = {
        'yahoo': 2000,  # requests per hour
        'nse': 100,
        'screener': 50,
        'newsapi': 100  # per day on free tier
    }

    # Cache Settings (TTL in seconds)
    CACHE_TTL = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '1h': 3600,
        '1d': 86400,
        'fundamental': 604800  # 1 week
    }

    # Supported Timeframes
    SUPPORTED_TIMEFRAMES = {
        'free': ['1d', '1wk', '1mo'],
        'paid': ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
    }

    # Backtesting Defaults
    DEFAULT_INITIAL_CAPITAL = 100000  # ₹1 Lakh
    DEFAULT_COMMISSION = 0.0003  # 0.03% per trade


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


# Select configuration based on environment
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
