"""
Technical analysis strategies.
"""
# Import strategies to auto-register them
from .sma_crossover import SMACrossover
from .rsi_strategy import RSIStrategy
from .vwap_strategy import VWAPStrategy

__all__ = [
    'SMACrossover',
    'RSIStrategy',
    'VWAPStrategy',
]
