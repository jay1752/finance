"""
MACD (Moving Average Convergence Divergence) Strategy.

MACD is a trend-following momentum indicator that shows the relationship
between two moving averages of a security's price.

Components:
- MACD Line = 12-period EMA - 26-period EMA
- Signal Line = 9-period EMA of MACD Line
- MACD Histogram = MACD Line - Signal Line

Signals:
- BUY: MACD line crosses above signal line (bullish crossover)
- SELL: MACD line crosses below signal line (bearish crossover)
"""
import pandas as pd
from typing import List, Dict, Any
import logging

from ..base import BaseStrategy, Signal
from ..registry import register_strategy

logger = logging.getLogger(__name__)


@register_strategy('macd')
class MACDStrategy(BaseStrategy):
    """
    MACD Strategy - Moving Average Convergence Divergence.

    Classic momentum strategy using MACD line and signal line crossovers.
    """

    name = "MACD"
    description = "Moving Average Convergence Divergence - Trend following momentum indicator"

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        min_histogram: float = 0.0
    ):
        """
        Initialize MACD strategy.

        Args:
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line EMA period (default: 9)
            min_histogram: Minimum histogram value for signal validation (default: 0.0)
        """
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.min_histogram = min_histogram

        logger.info(
            f"Initialized MACD strategy: "
            f"fast={fast_period}, slow={slow_period}, signal={signal_period}"
        )

    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Analyze data and generate MACD signals.

        Args:
            data: OHLCV DataFrame

        Returns:
            List of trading signals
        """
        if len(data) < self.slow_period + self.signal_period:
            logger.warning(
                f"Insufficient data for MACD: need {self.slow_period + self.signal_period} bars, "
                f"got {len(data)}"
            )
            return []

        df = data.copy()

        # Calculate MACD components
        df['ema_fast'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        df['macd_line'] = df['ema_fast'] - df['ema_slow']
        df['signal_line'] = df['macd_line'].ewm(span=self.signal_period, adjust=False).mean()
        df['macd_histogram'] = df['macd_line'] - df['signal_line']

        signals = []

        # Look for crossovers
        for i in range(1, len(df)):
            current_idx = df.index[i]
            prev_idx = df.index[i - 1]

            macd_curr = df.loc[current_idx, 'macd_line']
            macd_prev = df.loc[prev_idx, 'macd_line']
            signal_curr = df.loc[current_idx, 'signal_line']
            signal_prev = df.loc[prev_idx, 'signal_line']
            histogram = df.loc[current_idx, 'macd_histogram']
            price = df.loc[current_idx, 'close']

            signal_type = None
            confidence = 0.0
            metadata = {}

            # Bullish crossover: MACD crosses above signal line
            if macd_prev <= signal_prev and macd_curr > signal_curr:
                signal_type = 'BUY'

                # Calculate confidence based on:
                # 1. Histogram strength
                # 2. Whether MACD is above zero (trend confirmation)
                # 3. Distance from crossover

                histogram_strength = min(abs(histogram) / (price * 0.01), 40)  # Max 40 points
                trend_confirmation = 30 if macd_curr > 0 else 0  # 30 points if above zero
                crossover_gap = min(abs(macd_curr - signal_curr) / (price * 0.01), 30)  # Max 30 points

                confidence = histogram_strength + trend_confirmation + crossover_gap

                metadata = {
                    'macd_line': float(macd_curr),
                    'signal_line': float(signal_curr),
                    'macd_histogram': float(histogram),
                    'crossover_type': 'bullish',
                    'trend': 'bullish' if macd_curr > 0 else 'bearish'
                }

            # Bearish crossover: MACD crosses below signal line
            elif macd_prev >= signal_prev and macd_curr < signal_curr:
                signal_type = 'SELL'

                histogram_strength = min(abs(histogram) / (price * 0.01), 40)
                trend_confirmation = 30 if macd_curr < 0 else 0  # 30 points if below zero
                crossover_gap = min(abs(macd_curr - signal_curr) / (price * 0.01), 30)

                confidence = histogram_strength + trend_confirmation + crossover_gap

                metadata = {
                    'macd_line': float(macd_curr),
                    'signal_line': float(signal_curr),
                    'macd_histogram': float(histogram),
                    'crossover_type': 'bearish',
                    'trend': 'bullish' if macd_curr > 0 else 'bearish'
                }

            # Only create signal if histogram meets minimum threshold
            if signal_type and abs(histogram) >= self.min_histogram:
                signal = Signal(
                    date=str(current_idx.date()),
                    signal_type=signal_type,
                    price=float(price),
                    confidence=min(confidence, 100),  # Cap at 100
                    metadata=metadata
                )
                signals.append(signal)

                logger.debug(
                    f"{signal_type} signal at {signal.date}: "
                    f"MACD={macd_curr:.2f}, Signal={signal_curr:.2f}, "
                    f"Histogram={histogram:.2f}, Confidence={signal.confidence:.1f}%"
                )

        logger.info(f"Generated {len(signals)} MACD signals")
        return signals

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this strategy."""
        return {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'min_histogram': 0.0
        }


# Example usage
if __name__ == '__main__':
    import yfinance as yf
    from datetime import datetime, timedelta

    logging.basicConfig(level=logging.INFO)

    # Fetch sample data
    symbol = "RELIANCE.NS"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date)
    data.columns = data.columns.str.lower()

    # Run strategy
    strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    signals = strategy.analyze(data)

    print(f"\n{'='*60}")
    print(f"MACD Strategy - {symbol}")
    print(f"{'='*60}")
    print(f"Total signals: {len(signals)}")
    print(f"\nRecent signals:")
    for signal in signals[-5:]:
        print(f"  {signal.date}: {signal.signal_type} at ₹{signal.price:.2f} "
              f"(confidence: {signal.confidence:.1f}%)")
        print(f"    MACD: {signal.metadata['macd_line']:.2f}, "
              f"Signal: {signal.metadata['signal_line']:.2f}, "
              f"Histogram: {signal.metadata['macd_histogram']:.2f}")
