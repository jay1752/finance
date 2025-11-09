"""
Bollinger Bands Strategy.

Bollinger Bands are volatility bands placed above and below a moving average.
The bands expand when volatility increases and contract when volatility decreases.

Components:
- Middle Band = 20-period SMA
- Upper Band = Middle Band + (2 * Standard Deviation)
- Lower Band = Middle Band - (2 * Standard Deviation)

Signals:
- BUY: Price touches or crosses below lower band (oversold)
- SELL: Price touches or crosses above upper band (overbought)
"""
import pandas as pd
from typing import List, Dict, Any
import logging

from ..base import BaseStrategy, Signal
from ..registry import register_strategy

logger = logging.getLogger(__name__)


@register_strategy('bollinger_bands')
class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy - Volatility-based mean reversion.

    Uses price deviation from moving average to identify overbought/oversold conditions.
    """

    name = "Bollinger Bands"
    description = "Volatility bands for mean reversion trading"

    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        oversold_threshold: float = 0.02,
        overbought_threshold: float = 0.02
    ):
        """
        Initialize Bollinger Bands strategy.

        Args:
            period: Moving average period (default: 20)
            std_dev: Number of standard deviations for bands (default: 2.0)
            oversold_threshold: Price distance from lower band to trigger BUY (default: 0.02 = 2%)
            overbought_threshold: Price distance from upper band to trigger SELL (default: 0.02 = 2%)
        """
        super().__init__()
        self.period = period
        self.std_dev = std_dev
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold

        logger.info(
            f"Initialized Bollinger Bands strategy: "
            f"period={period}, std_dev={std_dev}"
        )

    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Analyze data and generate Bollinger Bands signals.

        Args:
            data: OHLCV DataFrame

        Returns:
            List of trading signals
        """
        if len(data) < self.period:
            logger.warning(
                f"Insufficient data for Bollinger Bands: need {self.period} bars, "
                f"got {len(data)}"
            )
            return []

        df = data.copy()

        # Calculate Bollinger Bands
        df['middle_band'] = df['close'].rolling(window=self.period).mean()
        df['std'] = df['close'].rolling(window=self.period).std()
        df['upper_band'] = df['middle_band'] + (self.std_dev * df['std'])
        df['lower_band'] = df['middle_band'] - (self.std_dev * df['std'])

        # Calculate %B (position within bands)
        # %B = (Price - Lower Band) / (Upper Band - Lower Band)
        # %B > 1 means price above upper band
        # %B < 0 means price below lower band
        # %B = 0.5 means price at middle band
        df['percent_b'] = (df['close'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])

        # Calculate bandwidth (volatility measure)
        df['bandwidth'] = (df['upper_band'] - df['lower_band']) / df['middle_band']

        signals = []

        # Look for band touches and crossings
        for i in range(1, len(df)):
            current_idx = df.index[i]
            prev_idx = df.index[i - 1]

            price = df.loc[current_idx, 'close']
            upper_band = df.loc[current_idx, 'upper_band']
            middle_band = df.loc[current_idx, 'middle_band']
            lower_band = df.loc[current_idx, 'lower_band']
            percent_b = df.loc[current_idx, 'percent_b']
            bandwidth = df.loc[current_idx, 'bandwidth']

            prev_price = df.loc[prev_idx, 'close']
            prev_lower = df.loc[prev_idx, 'lower_band']
            prev_upper = df.loc[prev_idx, 'upper_band']

            signal_type = None
            confidence = 0.0
            metadata = {}

            # BUY signal: Price touches or crosses below lower band (oversold)
            if percent_b < self.oversold_threshold or (prev_price >= prev_lower and price < lower_band):
                signal_type = 'BUY'

                # Calculate confidence based on:
                # 1. How far below lower band (more extreme = higher confidence)
                # 2. Bandwidth (higher volatility = lower confidence for mean reversion)
                # 3. Distance from middle band (further = higher confidence for bounce)

                band_penetration = max(0, (lower_band - price) / price) * 100  # How far below in %
                penetration_score = min(band_penetration * 20, 40)  # Max 40 points

                # Lower bandwidth = more confidence (tight bands suggest breakout less likely)
                bandwidth_score = max(0, 30 - (bandwidth * 100))  # Max 30 points

                # Distance from middle
                distance_from_mid = abs(price - middle_band) / middle_band * 100
                distance_score = min(distance_from_mid * 10, 30)  # Max 30 points

                confidence = penetration_score + bandwidth_score + distance_score

                metadata = {
                    'upper_band': float(upper_band),
                    'middle_band': float(middle_band),
                    'lower_band': float(lower_band),
                    'percent_b': float(percent_b),
                    'bandwidth': float(bandwidth),
                    'signal_reason': 'oversold'
                }

            # SELL signal: Price touches or crosses above upper band (overbought)
            elif percent_b > (1 - self.overbought_threshold) or (prev_price <= prev_upper and price > upper_band):
                signal_type = 'SELL'

                band_penetration = max(0, (price - upper_band) / price) * 100
                penetration_score = min(band_penetration * 20, 40)

                bandwidth_score = max(0, 30 - (bandwidth * 100))

                distance_from_mid = abs(price - middle_band) / middle_band * 100
                distance_score = min(distance_from_mid * 10, 30)

                confidence = penetration_score + bandwidth_score + distance_score

                metadata = {
                    'upper_band': float(upper_band),
                    'middle_band': float(middle_band),
                    'lower_band': float(lower_band),
                    'percent_b': float(percent_b),
                    'bandwidth': float(bandwidth),
                    'signal_reason': 'overbought'
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
                    f"Price={price:.2f}, %B={percent_b:.2f}, "
                    f"Bands=[{lower_band:.2f}, {middle_band:.2f}, {upper_band:.2f}], "
                    f"Confidence={signal.confidence:.1f}%"
                )

        logger.info(f"Generated {len(signals)} Bollinger Bands signals")
        return signals

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this strategy."""
        return {
            'period': 20,
            'std_dev': 2.0,
            'oversold_threshold': 0.02,
            'overbought_threshold': 0.02
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
    strategy = BollingerBandsStrategy(period=20, std_dev=2.0)
    signals = strategy.analyze(data)

    print(f"\n{'='*60}")
    print(f"Bollinger Bands Strategy - {symbol}")
    print(f"{'='*60}")
    print(f"Total signals: {len(signals)}")
    print(f"\nRecent signals:")
    for signal in signals[-5:]:
        print(f"  {signal.date}: {signal.signal_type} at ₹{signal.price:.2f} "
              f"(confidence: {signal.confidence:.1f}%)")
        print(f"    Bands: Lower={signal.metadata['lower_band']:.2f}, "
              f"Mid={signal.metadata['middle_band']:.2f}, "
              f"Upper={signal.metadata['upper_band']:.2f}")
        print(f"    %B={signal.metadata['percent_b']:.3f}, "
              f"Bandwidth={signal.metadata['bandwidth']:.3f}")
