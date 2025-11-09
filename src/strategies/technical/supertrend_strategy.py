"""
Supertrend Strategy.

Supertrend is a trend-following indicator that uses ATR (Average True Range)
to calculate dynamic support and resistance levels.

Components:
- ATR = Average True Range (volatility measure)
- Basic Upper Band = (High + Low) / 2 + (Multiplier × ATR)
- Basic Lower Band = (High + Low) / 2 - (Multiplier × ATR)
- Supertrend adjusts based on trend direction

Signals:
- BUY: Price crosses above Supertrend (trend changes to bullish)
- SELL: Price crosses below Supertrend (trend changes to bearish)
"""
import pandas as pd
from typing import List, Dict, Any
import logging

from ..base import BaseStrategy, Signal
from ..registry import register_strategy

logger = logging.getLogger(__name__)


@register_strategy('supertrend')
class SupertrendStrategy(BaseStrategy):
    """
    Supertrend Strategy - ATR-based trend following indicator.

    Uses volatility-adjusted bands to identify trend direction and reversals.
    """

    name = "Supertrend"
    description = "ATR-based trend following with dynamic support/resistance"

    def __init__(
        self,
        period: int = 10,
        multiplier: float = 3.0
    ):
        """
        Initialize Supertrend strategy.

        Args:
            period: ATR period (default: 10)
            multiplier: ATR multiplier for bands (default: 3.0)
        """
        super().__init__()
        self.period = period
        self.multiplier = multiplier

        logger.info(
            f"Initialized Supertrend strategy: "
            f"period={period}, multiplier={multiplier}"
        )

    def _calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=self.period).mean()

        return atr

    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Analyze data and generate Supertrend signals.

        Args:
            data: OHLCV DataFrame

        Returns:
            List of trading signals
        """
        if len(data) < self.period:
            logger.warning(
                f"Insufficient data for Supertrend: need {self.period} bars, "
                f"got {len(data)}"
            )
            return []

        df = data.copy()

        # Calculate ATR
        df['atr'] = self._calculate_atr(df)

        # Calculate basic bands
        df['hl_avg'] = (df['high'] + df['low']) / 2
        df['basic_upper'] = df['hl_avg'] + (self.multiplier * df['atr'])
        df['basic_lower'] = df['hl_avg'] - (self.multiplier * df['atr'])

        # Initialize Supertrend columns
        df['supertrend'] = 0.0
        df['trend'] = 1  # 1 = bullish, -1 = bearish

        # Calculate Supertrend
        for i in range(self.period, len(df)):
            curr_idx = df.index[i]
            prev_idx = df.index[i - 1]

            # Get current values
            close = df.loc[curr_idx, 'close']
            basic_upper = df.loc[curr_idx, 'basic_upper']
            basic_lower = df.loc[curr_idx, 'basic_lower']

            # Get previous values
            prev_supertrend = df.loc[prev_idx, 'supertrend']
            prev_trend = df.loc[prev_idx, 'trend']
            prev_close = df.loc[prev_idx, 'close']
            prev_basic_upper = df.loc[prev_idx, 'basic_upper']
            prev_basic_lower = df.loc[prev_idx, 'basic_lower']

            # Adjust bands (don't let them move against the trend)
            final_upper = basic_upper if basic_upper < prev_basic_upper or prev_close > prev_basic_upper else prev_basic_upper
            final_lower = basic_lower if basic_lower > prev_basic_lower or prev_close < prev_basic_lower else prev_basic_lower

            # Determine trend
            if prev_trend == 1:
                # Currently in uptrend
                if close <= final_lower:
                    trend = -1  # Switch to downtrend
                    supertrend = final_upper
                else:
                    trend = 1  # Stay in uptrend
                    supertrend = final_lower
            else:
                # Currently in downtrend
                if close >= final_upper:
                    trend = 1  # Switch to uptrend
                    supertrend = final_lower
                else:
                    trend = -1  # Stay in downtrend
                    supertrend = final_upper

            df.loc[curr_idx, 'supertrend'] = supertrend
            df.loc[curr_idx, 'trend'] = trend

        signals = []

        # Look for trend changes
        for i in range(self.period + 1, len(df)):
            current_idx = df.index[i]
            prev_idx = df.index[i - 1]

            trend_curr = df.loc[current_idx, 'trend']
            trend_prev = df.loc[prev_idx, 'trend']
            price = df.loc[current_idx, 'close']
            supertrend = df.loc[current_idx, 'supertrend']
            atr = df.loc[current_idx, 'atr']

            signal_type = None
            confidence = 0.0
            metadata = {}

            # BUY signal: Trend changes from bearish to bullish
            if trend_prev == -1 and trend_curr == 1:
                signal_type = 'BUY'

                # Calculate confidence based on:
                # 1. Distance from Supertrend (further = higher confidence)
                # 2. ATR relative to price (higher volatility = lower confidence)
                # 3. Momentum (price change)

                distance_from_st = (price - supertrend) / price * 100
                distance_score = min(distance_from_st * 10, 40)  # Max 40 points

                atr_ratio = atr / price
                volatility_score = max(0, 30 - (atr_ratio * 1000))  # Max 30 points

                prev_price = df.loc[prev_idx, 'close']
                momentum = (price - prev_price) / prev_price * 100
                momentum_score = min(momentum * 10, 30)  # Max 30 points

                confidence = distance_score + volatility_score + momentum_score

                metadata = {
                    'supertrend': float(supertrend),
                    'atr': float(atr),
                    'trend': 'bullish',
                    'distance_from_st': float(distance_from_st)
                }

            # SELL signal: Trend changes from bullish to bearish
            elif trend_prev == 1 and trend_curr == -1:
                signal_type = 'SELL'

                distance_from_st = (supertrend - price) / price * 100
                distance_score = min(distance_from_st * 10, 40)

                atr_ratio = atr / price
                volatility_score = max(0, 30 - (atr_ratio * 1000))

                prev_price = df.loc[prev_idx, 'close']
                momentum = abs((price - prev_price) / prev_price * 100)
                momentum_score = min(momentum * 10, 30)

                confidence = distance_score + volatility_score + momentum_score

                metadata = {
                    'supertrend': float(supertrend),
                    'atr': float(atr),
                    'trend': 'bearish',
                    'distance_from_st': float(distance_from_st)
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
                    f"Price={price:.2f}, Supertrend={supertrend:.2f}, "
                    f"Trend={metadata['trend']}, Confidence={signal.confidence:.1f}%"
                )

        logger.info(f"Generated {len(signals)} Supertrend signals")
        return signals

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this strategy."""
        return {
            'period': 10,
            'multiplier': 3.0
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
    strategy = SupertrendStrategy(period=10, multiplier=3.0)
    signals = strategy.analyze(data)

    print(f"\n{'='*60}")
    print(f"Supertrend Strategy - {symbol}")
    print(f"{'='*60}")
    print(f"Total signals: {len(signals)}")
    print(f"\nRecent signals:")
    for signal in signals[-5:]:
        print(f"  {signal.date}: {signal.signal_type} at ₹{signal.price:.2f} "
              f"(confidence: {signal.confidence:.1f}%)")
        print(f"    Supertrend={signal.metadata['supertrend']:.2f}, "
              f"Trend={signal.metadata['trend']}, "
              f"ATR={signal.metadata['atr']:.2f}")
