"""
ADX (Average Directional Index) Strategy.

ADX measures the strength of a trend, regardless of direction.
It uses the Directional Movement System to determine trend strength.

Components:
- +DI (Plus Directional Indicator) = Bullish movement
- -DI (Minus Directional Indicator) = Bearish movement
- ADX = Smoothed average of DX (trend strength)

Interpretation:
- ADX > 25: Strong trend
- ADX < 20: Weak trend or ranging
- +DI > -DI: Bullish trend
- -DI > +DI: Bearish trend

Signals:
- BUY: +DI crosses above -DI with ADX > threshold (strong bullish trend)
- SELL: -DI crosses above +DI with ADX > threshold (strong bearish trend)
"""
import pandas as pd
from typing import List, Dict, Any
import logging

from ..base import BaseStrategy, Signal
from ..registry import register_strategy

logger = logging.getLogger(__name__)


@register_strategy('adx')
class ADXStrategy(BaseStrategy):
    """
    ADX Strategy - Average Directional Index for trend strength.

    Combines trend direction (+DI/-DI) with trend strength (ADX) for high-quality signals.
    """

    name = "ADX"
    description = "Average Directional Index - Trend strength indicator"

    def __init__(
        self,
        period: int = 14,
        adx_threshold: float = 25.0
    ):
        """
        Initialize ADX strategy.

        Args:
            period: Period for DI and ADX calculation (default: 14)
            adx_threshold: Minimum ADX value for signal (default: 25)
        """
        super().__init__()
        self.period = period
        self.adx_threshold = adx_threshold

        logger.info(
            f"Initialized ADX strategy: "
            f"period={period}, threshold={adx_threshold}"
        )

    def _calculate_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ADX, +DI, and -DI."""
        # Calculate True Range
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift())
        df['low_close'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)

        # Calculate Directional Movement
        df['high_diff'] = df['high'] - df['high'].shift()
        df['low_diff'] = df['low'].shift() - df['low']

        # +DM and -DM
        df['plus_dm'] = df.apply(
            lambda row: row['high_diff'] if row['high_diff'] > row['low_diff'] and row['high_diff'] > 0 else 0,
            axis=1
        )
        df['minus_dm'] = df.apply(
            lambda row: row['low_diff'] if row['low_diff'] > row['high_diff'] and row['low_diff'] > 0 else 0,
            axis=1
        )

        # Smooth TR, +DM, -DM using Wilder's smoothing (EMA with alpha = 1/period)
        alpha = 1.0 / self.period
        df['atr'] = df['tr'].ewm(alpha=alpha, adjust=False).mean()
        df['plus_dm_smooth'] = df['plus_dm'].ewm(alpha=alpha, adjust=False).mean()
        df['minus_dm_smooth'] = df['minus_dm'].ewm(alpha=alpha, adjust=False).mean()

        # Calculate +DI and -DI
        df['plus_di'] = 100 * (df['plus_dm_smooth'] / df['atr'])
        df['minus_di'] = 100 * (df['minus_dm_smooth'] / df['atr'])

        # Calculate DX
        df['di_diff'] = abs(df['plus_di'] - df['minus_di'])
        df['di_sum'] = df['plus_di'] + df['minus_di']
        df['dx'] = 100 * (df['di_diff'] / df['di_sum'])

        # Calculate ADX (smoothed DX)
        df['adx'] = df['dx'].ewm(alpha=alpha, adjust=False).mean()

        return df

    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Analyze data and generate ADX signals.

        Args:
            data: OHLCV DataFrame

        Returns:
            List of trading signals
        """
        if len(data) < self.period * 2:
            logger.warning(
                f"Insufficient data for ADX: need {self.period * 2} bars, "
                f"got {len(data)}"
            )
            return []

        df = data.copy()
        df = self._calculate_adx(df)

        signals = []

        # Look for DI crossovers with strong ADX
        for i in range(1, len(df)):
            current_idx = df.index[i]
            prev_idx = df.index[i - 1]

            adx = df.loc[current_idx, 'adx']
            plus_di_curr = df.loc[current_idx, 'plus_di']
            minus_di_curr = df.loc[current_idx, 'minus_di']
            plus_di_prev = df.loc[prev_idx, 'plus_di']
            minus_di_prev = df.loc[prev_idx, 'minus_di']
            price = df.loc[current_idx, 'close']

            # Skip if NaN
            if pd.isna(adx) or pd.isna(plus_di_curr) or pd.isna(minus_di_curr):
                continue

            signal_type = None
            confidence = 0.0
            metadata = {}

            # BUY signal: +DI crosses above -DI with strong trend
            if (plus_di_prev <= minus_di_prev and plus_di_curr > minus_di_curr and
                adx >= self.adx_threshold):
                signal_type = 'BUY'

                # Calculate confidence based on:
                # 1. ADX strength (higher = stronger trend = higher confidence)
                # 2. DI gap (larger separation = clearer signal)
                # 3. Trend momentum (rising ADX = strengthening trend)

                adx_strength = min((adx - self.adx_threshold) / (100 - self.adx_threshold) * 100, 40)
                di_gap = abs(plus_di_curr - minus_di_curr)
                di_gap_score = min(di_gap, 30)

                prev_adx = df.loc[prev_idx, 'adx']
                adx_momentum = adx - prev_adx if not pd.isna(prev_adx) else 0
                momentum_score = min(max(adx_momentum * 3, 0), 30)

                confidence = adx_strength + di_gap_score + momentum_score

                metadata = {
                    'adx': float(adx),
                    'plus_di': float(plus_di_curr),
                    'minus_di': float(minus_di_curr),
                    'trend_strength': 'strong' if adx > 40 else 'moderate',
                    'crossover_type': 'bullish'
                }

            # SELL signal: -DI crosses above +DI with strong trend
            elif (minus_di_prev <= plus_di_prev and minus_di_curr > plus_di_curr and
                  adx >= self.adx_threshold):
                signal_type = 'SELL'

                adx_strength = min((adx - self.adx_threshold) / (100 - self.adx_threshold) * 100, 40)
                di_gap = abs(minus_di_curr - plus_di_curr)
                di_gap_score = min(di_gap, 30)

                prev_adx = df.loc[prev_idx, 'adx']
                adx_momentum = adx - prev_adx if not pd.isna(prev_adx) else 0
                momentum_score = min(max(adx_momentum * 3, 0), 30)

                confidence = adx_strength + di_gap_score + momentum_score

                metadata = {
                    'adx': float(adx),
                    'plus_di': float(plus_di_curr),
                    'minus_di': float(minus_di_curr),
                    'trend_strength': 'strong' if adx > 40 else 'moderate',
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
                    f"ADX={adx:.1f}, +DI={plus_di_curr:.1f}, -DI={minus_di_curr:.1f}, "
                    f"Confidence={signal.confidence:.1f}%"
                )

        logger.info(f"Generated {len(signals)} ADX signals")
        return signals

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this strategy."""
        return {
            'period': 14,
            'adx_threshold': 25.0
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
    strategy = ADXStrategy(period=14, adx_threshold=25.0)
    signals = strategy.analyze(data)

    print(f"\n{'='*60}")
    print(f"ADX Strategy - {symbol}")
    print(f"{'='*60}")
    print(f"Total signals: {len(signals)}")
    print(f"\nRecent signals:")
    for signal in signals[-5:]:
        print(f"  {signal.date}: {signal.signal_type} at ₹{signal.price:.2f} "
              f"(confidence: {signal.confidence:.1f}%)")
        print(f"    ADX={signal.metadata['adx']:.1f}, "
              f"+DI={signal.metadata['plus_di']:.1f}, "
              f"-DI={signal.metadata['minus_di']:.1f}")
        print(f"    Trend Strength: {signal.metadata['trend_strength']}")
