"""
SMA Crossover Strategy.

Simple Moving Average Crossover is a trend-following strategy:
- BUY when fast SMA crosses above slow SMA (bullish crossover)
- SELL when fast SMA crosses below slow SMA (bearish crossover)
"""
import pandas as pd
from ..base import BaseStrategy, Signal
from ..registry import register_strategy
import logging

logger = logging.getLogger(__name__)


@register_strategy('sma_crossover')
class SMACrossover(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.

    This is a classic trend-following strategy that generates signals when
    a fast-moving average crosses a slow-moving average.

    Parameters:
        fast_period (int): Period for fast SMA (default: 20)
        slow_period (int): Period for slow SMA (default: 50)
    """

    def get_default_params(self):
        return {
            'fast_period': 20,
            'slow_period': 50
        }

    def get_description(self) -> str:
        return (
            f"SMA Crossover strategy with {self.params['fast_period']}-day "
            f"and {self.params['slow_period']}-day moving averages. "
            "Generates BUY signals on bullish crossover and SELL signals on bearish crossover."
        )

    def analyze(self, data: pd.DataFrame) -> list:
        """
        Generate signals based on SMA crossover.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        # Validate data
        if not self.validate_data(data):
            raise ValueError(f"Invalid data format for {self.name}")

        # Reset previous signals
        self.reset()

        # Get parameters
        fast = self.params['fast_period']
        slow = self.params['slow_period']

        logger.debug(f"Running SMA Crossover with fast={fast}, slow={slow}")

        # Need at least slow_period + 1 rows for analysis
        if len(data) < slow + 1:
            logger.warning(
                f"Insufficient data: need at least {slow + 1} rows, got {len(data)}"
            )
            return []

        # Calculate SMAs
        data = data.copy()  # Avoid modifying original
        data['sma_fast'] = data['close'].rolling(window=fast).mean()
        data['sma_slow'] = data['close'].rolling(window=slow).mean()

        # Generate signals by detecting crossovers
        signals = []

        for i in range(1, len(data)):
            # Skip if SMAs not yet calculated
            if pd.isna(data['sma_fast'].iloc[i]) or pd.isna(data['sma_slow'].iloc[i]):
                continue

            prev_fast = data['sma_fast'].iloc[i-1]
            prev_slow = data['sma_slow'].iloc[i-1]
            curr_fast = data['sma_fast'].iloc[i]
            curr_slow = data['sma_slow'].iloc[i]

            signal_type = None

            # Bullish crossover: fast crosses above slow
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                signal_type = 'BUY'

            # Bearish crossover: fast crosses below slow
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                signal_type = 'SELL'

            # Create signal if crossover detected
            if signal_type:
                confidence = self._calculate_confidence(
                    data, i, curr_fast, curr_slow
                )

                signal = Signal(
                    date=str(data.index[i].date()),
                    signal_type=signal_type,
                    price=float(data['close'].iloc[i]),
                    confidence=confidence,
                    metadata={
                        'sma_fast': float(curr_fast),
                        'sma_slow': float(curr_slow),
                        'fast_period': fast,
                        'slow_period': slow,
                        'gap_percent': abs((curr_fast - curr_slow) / curr_slow * 100)
                    }
                )

                signals.append(signal)
                logger.debug(f"Generated signal: {signal}")

        self.signals = signals
        logger.info(f"Generated {len(signals)} signals for SMA Crossover")

        return signals

    def _calculate_confidence(
        self,
        data: pd.DataFrame,
        idx: int,
        fast_sma: float,
        slow_sma: float
    ) -> float:
        """
        Calculate signal confidence based on the gap between SMAs.

        Larger gap = stronger trend = higher confidence

        Args:
            data: Price data
            idx: Current index
            fast_sma: Fast SMA value
            slow_sma: Slow SMA value

        Returns:
            Confidence score (0-100)
        """
        price = data['close'].iloc[idx]

        # Calculate gap as percentage of price
        gap_pct = abs((fast_sma - slow_sma) / price) * 100

        # Scale to 0-100, with diminishing returns
        # 0.5% gap = ~50 confidence
        # 1% gap = ~70 confidence
        # 2%+ gap = ~90+ confidence
        confidence = min(gap_pct * 50, 100)

        # Additional factor: volume
        if 'volume' in data.columns:
            avg_volume = data['volume'].rolling(window=20).mean().iloc[idx]
            current_volume = data['volume'].iloc[idx]

            if not pd.isna(avg_volume) and avg_volume > 0:
                volume_factor = min(current_volume / avg_volume, 2)
                confidence = confidence * (0.7 + 0.3 * volume_factor)

        return round(min(confidence, 100), 2)
