"""
Trading strategies module.
"""
from .base import BaseStrategy, Signal
from .registry import StrategyRegistry, register_strategy

__all__ = [
    'BaseStrategy',
    'Signal',
    'StrategyRegistry',
    'register_strategy',
]
