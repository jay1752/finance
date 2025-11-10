"""
Database module for stock market analysis.

Supports both SQLite (development/single-user) and PostgreSQL (production).
"""
from .connection import DatabaseManager, get_db
from .models import Stock, StockPrice, Signal, BacktestResult

__all__ = [
    'DatabaseManager',
    'get_db',
    'Stock',
    'StockPrice',
    'Signal',
    'BacktestResult',
]
