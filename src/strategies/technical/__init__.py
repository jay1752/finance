"""
Technical analysis strategies.
"""
# Import strategies to auto-register them
from .sma_crossover import SMACrossover
from .rsi_strategy import RSIStrategy
from .vwap_strategy import VWAPStrategy
from .macd_strategy import MACDStrategy
from .bollinger_bands_strategy import BollingerBandsStrategy
from .stochastic_strategy import StochasticStrategy
from .supertrend_strategy import SupertrendStrategy
from .adx_strategy import ADXStrategy

__all__ = [
    'SMACrossover',
    'RSIStrategy',
    'VWAPStrategy',
    'MACDStrategy',
    'BollingerBandsStrategy',
    'StochasticStrategy',
    'SupertrendStrategy',
    'ADXStrategy',
]
