"""
Multi-Timeframe Analysis Module.

Analyzes stocks across multiple timeframes to increase signal confidence.
When signals align across timeframes, it indicates stronger conviction.

Timeframe Hierarchy:
- Weekly (1wk): Long-term trend direction
- Daily (1d): Medium-term trend and key levels
- 4-Hour (4h): Short-term momentum and entry timing
- 1-Hour (1h): Precise entry/exit points

Signal Strength Rules:
- All 4 timeframes aligned: VERY STRONG (90-100% confidence)
- 3 timeframes aligned: STRONG (70-89% confidence)
- 2 timeframes aligned: MODERATE (50-69% confidence)
- 1 timeframe only: WEAK (30-49% confidence)
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import logging

from ..data.adapters.adapter_factory import AdapterFactory
from ..strategies.registry import StrategyRegistry
from ..strategies.base import Signal

logger = logging.getLogger(__name__)


@dataclass
class TimeframeSignal:
    """Signal from a specific timeframe."""
    timeframe: str
    signal: Optional[Signal]
    has_signal: bool
    signal_type: Optional[str]  # 'BUY', 'SELL', or None
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class MultiTimeframeResult:
    """Result of multi-timeframe analysis."""
    symbol: str
    strategy_name: str
    analysis_date: datetime

    # Individual timeframe results
    timeframe_signals: List[TimeframeSignal]

    # Aggregated results
    overall_signal: str  # 'BUY', 'SELL', 'NEUTRAL', 'CONFLICTING'
    overall_confidence: float  # 0-100
    signal_strength: str  # 'VERY STRONG', 'STRONG', 'MODERATE', 'WEAK'
    aligned_timeframes: int  # Number of timeframes with same signal

    # Recommendation
    recommendation: str
    reasoning: str


class MultiTimeframeAnalyzer:
    """
    Analyze stocks across multiple timeframes.

    This analyzer runs the same strategy on different timeframes
    and combines the signals to determine overall conviction.
    """

    # Standard timeframe sets
    TIMEFRAME_SETS = {
        'full': ['1h', '4h', '1d', '1wk'],  # All 4 timeframes
        'intraday': ['1h', '4h', '1d'],     # Short to medium term
        'swing': ['4h', '1d', '1wk'],       # Medium to long term
        'daily_only': ['1d', '1wk'],        # Daily and weekly only
    }

    # Timeframe weights for confidence calculation
    TIMEFRAME_WEIGHTS = {
        '1h': 1.0,    # Least important (noise)
        '4h': 1.5,    # Short-term trend
        '1d': 2.0,    # Medium-term trend
        '1wk': 3.0,   # Most important (main trend)
    }

    def __init__(self, timeframe_set: str = 'full'):
        """
        Initialize multi-timeframe analyzer.

        Args:
            timeframe_set: Which set of timeframes to analyze
                          ('full', 'intraday', 'swing', 'daily_only')
        """
        if timeframe_set not in self.TIMEFRAME_SETS:
            raise ValueError(
                f"Invalid timeframe set: {timeframe_set}. "
                f"Available: {list(self.TIMEFRAME_SETS.keys())}"
            )

        self.timeframe_set = timeframe_set
        self.timeframes = self.TIMEFRAME_SETS[timeframe_set]
        logger.info(f"Initialized MultiTimeframeAnalyzer with timeframes: {self.timeframes}")

    def analyze(
        self,
        symbol: str,
        strategy_name: str,
        strategy_params: Optional[Dict[str, Any]] = None,
        days_back: int = 90
    ) -> MultiTimeframeResult:
        """
        Analyze a stock across multiple timeframes.

        Args:
            symbol: Stock symbol
            strategy_name: Strategy to use (from registry)
            strategy_params: Strategy parameters (optional)
            days_back: How many days of data to fetch

        Returns:
            MultiTimeframeResult with signals from all timeframes
        """
        logger.info(f"Starting multi-timeframe analysis for {symbol} using {strategy_name}")

        if strategy_params is None:
            strategy_params = {}

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Analyze each timeframe
        timeframe_signals = []

        for timeframe in self.timeframes:
            tf_signal = self._analyze_timeframe(
                symbol=symbol,
                timeframe=timeframe,
                strategy_name=strategy_name,
                strategy_params=strategy_params,
                start_date=start_date,
                end_date=end_date
            )
            timeframe_signals.append(tf_signal)

        # Aggregate results
        result = self._aggregate_signals(
            symbol=symbol,
            strategy_name=strategy_name,
            timeframe_signals=timeframe_signals
        )

        logger.info(
            f"Multi-timeframe analysis complete for {symbol}: "
            f"{result.overall_signal} ({result.signal_strength})"
        )

        return result

    def _analyze_timeframe(
        self,
        symbol: str,
        timeframe: str,
        strategy_name: str,
        strategy_params: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> TimeframeSignal:
        """Analyze a single timeframe."""
        try:
            # Fetch data for this timeframe
            adapter = AdapterFactory.get_adapter(timeframe=timeframe)
            data = adapter.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe
            )

            if data.empty:
                logger.warning(f"No data for {symbol} on {timeframe}")
                return TimeframeSignal(
                    timeframe=timeframe,
                    signal=None,
                    has_signal=False,
                    signal_type=None,
                    confidence=0.0,
                    metadata={'error': 'No data'}
                )

            # Run strategy
            strategy = StrategyRegistry.get_strategy(strategy_name, **strategy_params)
            signals = strategy.analyze(data.copy())

            # Get latest signal
            latest_signal = strategy.get_latest_signal()

            if latest_signal:
                return TimeframeSignal(
                    timeframe=timeframe,
                    signal=latest_signal,
                    has_signal=True,
                    signal_type=latest_signal.signal_type,
                    confidence=latest_signal.confidence,
                    metadata={
                        'date': latest_signal.date,
                        'price': latest_signal.price,
                        'signal_metadata': latest_signal.metadata
                    }
                )
            else:
                return TimeframeSignal(
                    timeframe=timeframe,
                    signal=None,
                    has_signal=False,
                    signal_type=None,
                    confidence=0.0,
                    metadata={'info': 'No signal generated'}
                )

        except Exception as e:
            logger.error(f"Error analyzing {timeframe} for {symbol}: {e}")
            return TimeframeSignal(
                timeframe=timeframe,
                signal=None,
                has_signal=False,
                signal_type=None,
                confidence=0.0,
                metadata={'error': str(e)}
            )

    def _aggregate_signals(
        self,
        symbol: str,
        strategy_name: str,
        timeframe_signals: List[TimeframeSignal]
    ) -> MultiTimeframeResult:
        """Aggregate signals from multiple timeframes."""

        # Count signals by type
        buy_signals = [tf for tf in timeframe_signals if tf.signal_type == 'BUY']
        sell_signals = [tf for tf in timeframe_signals if tf.signal_type == 'SELL']
        total_signals = len([tf for tf in timeframe_signals if tf.has_signal])

        # Determine overall signal
        overall_signal = 'NEUTRAL'
        aligned_timeframes = 0

        if len(buy_signals) > len(sell_signals) and len(buy_signals) > 0:
            overall_signal = 'BUY'
            aligned_timeframes = len(buy_signals)
        elif len(sell_signals) > len(buy_signals) and len(sell_signals) > 0:
            overall_signal = 'SELL'
            aligned_timeframes = len(sell_signals)
        elif len(buy_signals) == len(sell_signals) and len(buy_signals) > 0:
            overall_signal = 'CONFLICTING'
            aligned_timeframes = 0

        # Calculate weighted confidence
        overall_confidence = self._calculate_confidence(
            timeframe_signals=timeframe_signals,
            dominant_signal=overall_signal
        )

        # Determine signal strength
        signal_strength = self._determine_strength(
            aligned_timeframes=aligned_timeframes,
            total_timeframes=len(self.timeframes),
            overall_confidence=overall_confidence
        )

        # Generate recommendation and reasoning
        recommendation, reasoning = self._generate_recommendation(
            overall_signal=overall_signal,
            signal_strength=signal_strength,
            aligned_timeframes=aligned_timeframes,
            total_timeframes=len(self.timeframes),
            timeframe_signals=timeframe_signals
        )

        return MultiTimeframeResult(
            symbol=symbol,
            strategy_name=strategy_name,
            analysis_date=datetime.now(),
            timeframe_signals=timeframe_signals,
            overall_signal=overall_signal,
            overall_confidence=overall_confidence,
            signal_strength=signal_strength,
            aligned_timeframes=aligned_timeframes,
            recommendation=recommendation,
            reasoning=reasoning
        )

    def _calculate_confidence(
        self,
        timeframe_signals: List[TimeframeSignal],
        dominant_signal: str
    ) -> float:
        """
        Calculate overall confidence using weighted average.

        Higher timeframes have more weight in the calculation.
        """
        if dominant_signal in ['NEUTRAL', 'CONFLICTING']:
            return 0.0

        total_weight = 0.0
        weighted_confidence = 0.0

        for tf_signal in timeframe_signals:
            if tf_signal.signal_type == dominant_signal:
                weight = self.TIMEFRAME_WEIGHTS.get(tf_signal.timeframe, 1.0)
                total_weight += weight
                weighted_confidence += tf_signal.confidence * weight

        if total_weight == 0:
            return 0.0

        return min(100.0, weighted_confidence / total_weight)

    def _determine_strength(
        self,
        aligned_timeframes: int,
        total_timeframes: int,
        overall_confidence: float
    ) -> str:
        """Determine signal strength based on alignment and confidence."""

        if aligned_timeframes == 0:
            return 'NONE'

        alignment_ratio = aligned_timeframes / total_timeframes

        # All or almost all timeframes aligned
        if alignment_ratio >= 0.75 and overall_confidence >= 70:
            return 'VERY STRONG'

        # Majority aligned
        elif alignment_ratio >= 0.5 and overall_confidence >= 60:
            return 'STRONG'

        # Some alignment
        elif alignment_ratio >= 0.4 and overall_confidence >= 50:
            return 'MODERATE'

        # Weak alignment
        else:
            return 'WEAK'

    def _generate_recommendation(
        self,
        overall_signal: str,
        signal_strength: str,
        aligned_timeframes: int,
        total_timeframes: int,
        timeframe_signals: List[TimeframeSignal]
    ) -> tuple[str, str]:
        """Generate trading recommendation and reasoning."""

        # Get signal types per timeframe
        tf_breakdown = {
            tf.timeframe: tf.signal_type or 'NONE'
            for tf in timeframe_signals
        }

        # Build reasoning
        reasoning_parts = []

        # Overall signal
        if overall_signal == 'BUY':
            reasoning_parts.append(
                f"{aligned_timeframes}/{total_timeframes} timeframes show BUY signals"
            )
        elif overall_signal == 'SELL':
            reasoning_parts.append(
                f"{aligned_timeframes}/{total_timeframes} timeframes show SELL signals"
            )
        elif overall_signal == 'CONFLICTING':
            reasoning_parts.append("Timeframes show conflicting signals")
        else:
            reasoning_parts.append("No clear signal across timeframes")

        # Add timeframe breakdown
        for tf in sorted(tf_breakdown.keys(), key=lambda x: ['1h', '4h', '1d', '1wk'].index(x)):
            signal_type = tf_breakdown[tf]
            if signal_type != 'NONE':
                tf_signal = next(t for t in timeframe_signals if t.timeframe == tf)
                reasoning_parts.append(
                    f"{tf}: {signal_type} ({tf_signal.confidence:.0f}%)"
                )

        reasoning = ". ".join(reasoning_parts)

        # Determine recommendation
        if overall_signal == 'BUY' and signal_strength in ['VERY STRONG', 'STRONG']:
            recommendation = 'STRONG BUY - High confidence across multiple timeframes'
        elif overall_signal == 'BUY' and signal_strength == 'MODERATE':
            recommendation = 'BUY - Moderate confidence, consider position sizing carefully'
        elif overall_signal == 'BUY' and signal_strength == 'WEAK':
            recommendation = 'WEAK BUY - Low confidence, wait for better alignment'
        elif overall_signal == 'SELL' and signal_strength in ['VERY STRONG', 'STRONG']:
            recommendation = 'STRONG SELL - High confidence across multiple timeframes'
        elif overall_signal == 'SELL' and signal_strength == 'MODERATE':
            recommendation = 'SELL - Moderate confidence, consider position sizing carefully'
        elif overall_signal == 'SELL' and signal_strength == 'WEAK':
            recommendation = 'WEAK SELL - Low confidence, wait for better alignment'
        elif overall_signal == 'CONFLICTING':
            recommendation = 'HOLD - Conflicting signals, wait for clarity'
        else:
            recommendation = 'HOLD - No clear signal'

        return recommendation, reasoning

    def get_timeframe_alignment_score(self, result: MultiTimeframeResult) -> float:
        """
        Calculate alignment score (0-100).

        100 = all timeframes aligned
        0 = no alignment
        """
        if not result.timeframe_signals:
            return 0.0

        return (result.aligned_timeframes / len(result.timeframe_signals)) * 100
