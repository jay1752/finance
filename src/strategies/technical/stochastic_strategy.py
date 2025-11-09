"""
Stochastic Oscillator Strategy.

The Stochastic Oscillator is a momentum indicator that shows the location
of the close price relative to the high-low range over a set period.

Components:
- %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
- %D = 3-period SMA of %K (signal line)

Signals:
- BUY: %K crosses above %D in oversold zone (< 20)
- SELL: %K crosses below %D in overbought zone (> 80)
"""
import pandas as pd
from typing import List, Dict, Any
import logging

from ..base import BaseStrategy, Signal
from ..registry import register_strategy

logger = logging.getLogger(__name__)


@register_strategy('stochastic')
class StochasticStrategy(BaseStrategy):
    """
    Stochastic Oscillator Strategy - Momentum indicator for overbought/oversold conditions.

    Identifies potential reversals by comparing closing price to price range.
    """

    name = "Stochastic Oscillator"
    description = "Momentum oscillator for overbought/oversold conditions"

    def __init__(
        self,
        k_period: int = 14,
        d_period: int = 3,
        oversold_level: float = 20.0,
        overbought_level: float = 80.0
    ):
        """
        Initialize Stochastic Oscillator strategy.

        Args:
            k_period: %K period (default: 14)
            d_period: %D SMA period (default: 3)
            oversold_level: Oversold threshold (default: 20)
            overbought_level: Overbought threshold (default: 80)
        """
        super().__init__()
        self.k_period = k_period
        self.d_period = d_period
        self.oversold_level = oversold_level
        self.overbought_level = overbought_level

        logger.info(
            f"Initialized Stochastic strategy: "
            f"k={k_period}, d={d_period}, oversold={oversold_level}, overbought={overbought_level}"
        )

    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Analyze data and generate Stochastic signals.

        Args:
            data: OHLCV DataFrame

        Returns:
            List of trading signals
        """
        if len(data) < self.k_period + self.d_period:
            logger.warning(
                f"Insufficient data for Stochastic: need {self.k_period + self.d_period} bars, "
                f"got {len(data)}"
            )
            return []

        df = data.copy()

        # Calculate %K
        low_min = df['low'].rolling(window=self.k_period).min()
        high_max = df['high'].rolling(window=self.k_period).max()
        df['stoch_k'] = 100 * (df['close'] - low_min) / (high_max - low_min)

        # Calculate %D (signal line)
        df['stoch_d'] = df['stoch_k'].rolling(window=self.d_period).mean()

        signals = []

        # Look for crossovers in oversold/overbought zones
        for i in range(1, len(df)):
            current_idx = df.index[i]
            prev_idx = df.index[i - 1]

            k_curr = df.loc[current_idx, 'stoch_k']
            k_prev = df.loc[prev_idx, 'stoch_k']
            d_curr = df.loc[current_idx, 'stoch_d']
            d_prev = df.loc[prev_idx, 'stoch_d']
            price = df.loc[current_idx, 'close']

            # Skip if NaN
            if pd.isna(k_curr) or pd.isna(d_curr) or pd.isna(k_prev) or pd.isna(d_prev):
                continue

            signal_type = None
            confidence = 0.0
            metadata = {}

            # BUY signal: %K crosses above %D in oversold zone
            if k_prev <= d_prev and k_curr > d_curr and k_curr < self.oversold_level:
                signal_type = 'BUY'

                # Calculate confidence based on:
                # 1. How deep in oversold territory (deeper = higher confidence)
                # 2. Crossover strength (larger gap after crossover = higher confidence)
                # 3. Rate of change in %K (faster rise = higher confidence)

                oversold_depth = max(0, self.oversold_level - k_curr) / self.oversold_level * 100
                oversold_score = min(oversold_depth * 2, 40)  # Max 40 points

                crossover_gap = abs(k_curr - d_curr)
                gap_score = min(crossover_gap, 30)  # Max 30 points

                k_momentum = k_curr - k_prev
                momentum_score = min(k_momentum, 30)  # Max 30 points

                confidence = oversold_score + gap_score + momentum_score

                metadata = {
                    'stoch_k': float(k_curr),
                    'stoch_d': float(d_curr),
                    'zone': 'oversold',
                    'crossover_type': 'bullish'
                }

            # SELL signal: %K crosses below %D in overbought zone
            elif k_prev >= d_prev and k_curr < d_curr and k_curr > self.overbought_level:
                signal_type = 'SELL'

                overbought_depth = max(0, k_curr - self.overbought_level) / (100 - self.overbought_level) * 100
                overbought_score = min(overbought_depth * 2, 40)

                crossover_gap = abs(k_curr - d_curr)
                gap_score = min(crossover_gap, 30)

                k_momentum = abs(k_curr - k_prev)
                momentum_score = min(k_momentum, 30)

                confidence = overbought_score + gap_score + momentum_score

                metadata = {
                    'stoch_k': float(k_curr),
                    'stoch_d': float(d_curr),
                    'zone': 'overbought',
                    'crossover_type': 'bearish'
                }

            if signal_type:
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
                    f"%K={k_curr:.1f}, %D={d_curr:.1f}, "
                    f"Zone={metadata['zone']}, Confidence={signal.confidence:.1f}%"
                )

        logger.info(f"Generated {len(signals)} Stochastic signals")
        return signals

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this strategy."""
        return {
            'k_period': 14,
            'd_period': 3,
            'oversold_level': 20.0,
            'overbought_level': 80.0
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
    strategy = StochasticStrategy(k_period=14, d_period=3)
    signals = strategy.analyze(data)

    print(f"\n{'='*60}")
    print(f"Stochastic Oscillator Strategy - {symbol}")
    print(f"{'='*60}")
    print(f"Total signals: {len(signals)}")
    print(f"\nRecent signals:")
    for signal in signals[-5:]:
        print(f"  {signal.date}: {signal.signal_type} at ₹{signal.price:.2f} "
              f"(confidence: {signal.confidence:.1f}%)")
        print(f"    %K={signal.metadata['stoch_k']:.1f}, "
              f"%D={signal.metadata['stoch_d']:.1f}, "
              f"Zone={signal.metadata['zone']}")
