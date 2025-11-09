"""
VWAP Strategy.

Volume Weighted Average Price (VWAP) is a trading benchmark that gives
the average price a stock has traded at, weighted by volume.

Strategy:
- BUY when price crosses above VWAP
- SELL when price crosses below VWAP
"""
import pandas as pd
from ..base import BaseStrategy, Signal
from ..registry import register_strategy
import logging

logger = logging.getLogger(__name__)


@register_strategy('vwap')
class VWAPStrategy(BaseStrategy):
    """
    VWAP (Volume Weighted Average Price) Strategy.

    VWAP is calculated by taking the sum of dollars traded for every transaction
    (price multiplied by volume) and dividing it by the total shares traded.

    This strategy generates signals when price crosses VWAP:
    - Above VWAP = bullish (BUY)
    - Below VWAP = bearish (SELL)

    Parameters:
        period (int): Rolling VWAP period (default: 20)
        threshold (float): Minimum % difference for signal (default: 0.5%)
    """

    def get_default_params(self):
        return {
            'period': 20,  # Rolling window
            'threshold': 0.5  # Minimum % difference from VWAP to generate signal
        }

    def get_description(self) -> str:
        return (
            f"VWAP strategy with {self.params['period']}-day rolling period. "
            f"Generates signals when price crosses VWAP with at least "
            f"{self.params['threshold']}% difference."
        )

    def analyze(self, data: pd.DataFrame) -> list:
        """
        Generate signals based on VWAP crossover.

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
        period = self.params['period']
        threshold = self.params['threshold']

        logger.debug(f"Running VWAP Strategy with period={period}, threshold={threshold}%")

        # Need at least period rows
        if len(data) < period:
            logger.warning(
                f"Insufficient data: need at least {period} rows, got {len(data)}"
            )
            return []

        # Calculate VWAP
        data = data.copy()
        data['vwap'] = self._calculate_vwap(data, period)

        # Calculate price distance from VWAP
        data['price_vs_vwap'] = ((data['close'] - data['vwap']) / data['vwap']) * 100

        # Generate signals
        signals = []

        for i in range(1, len(data)):
            # Skip if VWAP not yet calculated
            if pd.isna(data['vwap'].iloc[i]) or pd.isna(data['vwap'].iloc[i-1]):
                continue

            prev_close = data['close'].iloc[i-1]
            curr_close = data['close'].iloc[i]
            prev_vwap = data['vwap'].iloc[i-1]
            curr_vwap = data['vwap'].iloc[i]
            price_vs_vwap = data['price_vs_vwap'].iloc[i]

            signal_type = None

            # Price crosses above VWAP (bullish)
            if prev_close <= prev_vwap and curr_close > curr_vwap:
                if abs(price_vs_vwap) >= threshold:
                    signal_type = 'BUY'

            # Price crosses below VWAP (bearish)
            elif prev_close >= prev_vwap and curr_close < curr_vwap:
                if abs(price_vs_vwap) >= threshold:
                    signal_type = 'SELL'

            # Create signal if crossover detected
            if signal_type:
                confidence = self._calculate_confidence(
                    price_vs_vwap, data['volume'].iloc[i], data['volume'].rolling(20).mean().iloc[i]
                )

                signal = Signal(
                    date=str(data.index[i].date()),
                    signal_type=signal_type,
                    price=float(data['close'].iloc[i]),
                    confidence=confidence,
                    metadata={
                        'vwap': float(curr_vwap),
                        'price_vs_vwap_pct': float(price_vs_vwap),
                        'volume': int(data['volume'].iloc[i]),
                        'period': period,
                        'threshold': threshold
                    }
                )

                signals.append(signal)
                logger.debug(f"Generated signal: {signal}")

        self.signals = signals
        logger.info(f"Generated {len(signals)} signals for VWAP Strategy")

        return signals

    def _calculate_vwap(self, data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate rolling VWAP.

        VWAP = Sum(Price * Volume) / Sum(Volume)

        Args:
            data: DataFrame with OHLCV data
            period: Rolling window period

        Returns:
            VWAP series
        """
        # Use typical price (HLC/3)
        typical_price = (data['high'] + data['low'] + data['close']) / 3

        # Calculate VWAP
        vwap = (typical_price * data['volume']).rolling(window=period).sum() / \
               data['volume'].rolling(window=period).sum()

        return vwap

    def _calculate_confidence(
        self,
        price_vs_vwap_pct: float,
        current_volume: float,
        avg_volume: float
    ) -> float:
        """
        Calculate signal confidence.

        Confidence factors:
        1. Distance from VWAP (larger = more confidence)
        2. Volume (higher than average = more confidence)

        Args:
            price_vs_vwap_pct: Price distance from VWAP (%)
            current_volume: Current bar volume
            avg_volume: Average volume

        Returns:
            Confidence score (0-100)
        """
        # Base confidence from price distance
        # 0.5% = 50, 1% = 60, 2% = 80, 3%+ = 90+
        distance_confidence = min(abs(price_vs_vwap_pct) * 30, 90)

        # Volume factor
        volume_confidence = 50  # Default

        if not pd.isna(avg_volume) and avg_volume > 0:
            volume_ratio = current_volume / avg_volume

            if volume_ratio >= 1.5:
                volume_confidence = 80  # High volume
            elif volume_ratio >= 1.0:
                volume_confidence = 65  # Average volume
            else:
                volume_confidence = 40  # Low volume

        # Weighted average: 70% distance, 30% volume
        confidence = (distance_confidence * 0.7) + (volume_confidence * 0.3)

        return round(min(confidence, 100), 2)
