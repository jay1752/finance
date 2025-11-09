"""
RSI Strategy.

Relative Strength Index (RSI) is a momentum oscillator that measures
the speed and magnitude of price changes.

Strategy:
- BUY when RSI crosses above oversold level (default: 30)
- SELL when RSI crosses below overbought level (default: 70)
"""
import pandas as pd
from ..base import BaseStrategy, Signal
from ..registry import register_strategy
import logging

logger = logging.getLogger(__name__)


@register_strategy('rsi')
class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Mean Reversion Strategy.

    RSI is a momentum indicator that measures overbought/oversold conditions.
    This strategy exploits mean reversion by buying when oversold and selling when overbought.

    Parameters:
        period (int): RSI calculation period (default: 14)
        oversold (int): Oversold threshold (default: 30)
        overbought (int): Overbought threshold (default: 70)
    """

    def get_default_params(self):
        return {
            'period': 14,
            'oversold': 30,
            'overbought': 70
        }

    def get_description(self) -> str:
        return (
            f"RSI strategy with {self.params['period']}-period RSI. "
            f"Buys when RSI crosses above {self.params['oversold']} "
            f"and sells when RSI crosses below {self.params['overbought']}."
        )

    def analyze(self, data: pd.DataFrame) -> list:
        """
        Generate signals based on RSI levels.

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
        oversold = self.params['oversold']
        overbought = self.params['overbought']

        logger.debug(
            f"Running RSI Strategy with period={period}, "
            f"oversold={oversold}, overbought={overbought}"
        )

        # Need at least period + 1 rows
        if len(data) < period + 1:
            logger.warning(
                f"Insufficient data: need at least {period + 1} rows, got {len(data)}"
            )
            return []

        # Calculate RSI
        data = data.copy()
        data['rsi'] = self._calculate_rsi(data['close'], period)

        # Generate signals
        signals = []

        for i in range(1, len(data)):
            # Skip if RSI not yet calculated
            if pd.isna(data['rsi'].iloc[i]) or pd.isna(data['rsi'].iloc[i-1]):
                continue

            prev_rsi = data['rsi'].iloc[i-1]
            curr_rsi = data['rsi'].iloc[i]

            signal_type = None

            # Oversold → BUY (crossing above oversold threshold)
            if prev_rsi <= oversold and curr_rsi > oversold:
                signal_type = 'BUY'

            # Overbought → SELL (crossing below overbought threshold)
            elif prev_rsi >= overbought and curr_rsi < overbought:
                signal_type = 'SELL'

            # Create signal if threshold crossed
            if signal_type:
                confidence = self._calculate_confidence(
                    curr_rsi, signal_type, oversold, overbought
                )

                signal = Signal(
                    date=str(data.index[i].date()),
                    signal_type=signal_type,
                    price=float(data['close'].iloc[i]),
                    confidence=confidence,
                    metadata={
                        'rsi': float(curr_rsi),
                        'period': period,
                        'oversold': oversold,
                        'overbought': overbought,
                        'rsi_range': 'oversold' if curr_rsi < 40 else 'overbought' if curr_rsi > 60 else 'neutral'
                    }
                )

                signals.append(signal)
                logger.debug(f"Generated signal: {signal}")

        self.signals = signals
        logger.info(f"Generated {len(signals)} signals for RSI Strategy")

        return signals

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Relative Strength Index.

        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over period

        Args:
            prices: Price series (typically close prices)
            period: RSI period

        Returns:
            RSI series
        """
        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Calculate average gain and loss using exponential moving average
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_confidence(
        self,
        rsi: float,
        signal_type: str,
        oversold: float,
        overbought: float
    ) -> float:
        """
        Calculate signal confidence based on how extreme the RSI level is.

        More extreme RSI = higher confidence
        - For BUY: RSI closer to 0 = higher confidence
        - For SELL: RSI closer to 100 = higher confidence

        Args:
            rsi: Current RSI value
            signal_type: BUY or SELL
            oversold: Oversold threshold
            overbought: Overbought threshold

        Returns:
            Confidence score (0-100)
        """
        if signal_type == 'BUY':
            # Closer to 0 = higher confidence
            # RSI 0-20 = very high confidence
            # RSI 20-30 = high confidence
            # RSI 30+ = decreasing confidence
            if rsi <= 20:
                confidence = 90 + (20 - rsi) / 2  # 90-100%
            elif rsi <= oversold:
                confidence = 70 + (oversold - rsi) * 2  # 70-90%
            else:
                confidence = 50 + (40 - rsi) / 2  # 50-70%

        else:  # SELL
            # Closer to 100 = higher confidence
            if rsi >= 80:
                confidence = 90 + (rsi - 80) / 2  # 90-100%
            elif rsi >= overbought:
                confidence = 70 + (rsi - overbought) * 2  # 70-90%
            else:
                confidence = 50 + (rsi - 60) / 2  # 50-70%

        return round(max(0, min(100, confidence)), 2)
