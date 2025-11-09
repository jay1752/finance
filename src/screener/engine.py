"""
Stock Screener Engine.

Scans multiple stocks with multiple strategies to find trading opportunities.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

from src.strategies.base import BaseStrategy, Signal
from src.strategies.registry import StrategyRegistry
from src.data.adapters.adapter_factory import AdapterFactory

logger = logging.getLogger(__name__)


@dataclass
class ScreenerResult:
    """Result from screening a single stock with a strategy."""
    stock_symbol: str
    strategy_name: str
    signal_type: str  # BUY, SELL, or HOLD
    price: float
    confidence: float
    signal_date: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self):
        return (
            f"ScreenerResult({self.stock_symbol}: {self.signal_type} "
            f"via {self.strategy_name}, confidence={self.confidence:.1f}%)"
        )


class StockScreener:
    """
    Multi-stock, multi-strategy screener.

    Scans a list of stocks with selected strategies to find trading opportunities.
    """

    def __init__(
        self,
        lookback_days: int = 365,
        min_confidence: float = 0.0
    ):
        """
        Initialize stock screener.

        Args:
            lookback_days: Days of historical data to fetch (default: 365)
            min_confidence: Minimum confidence threshold for signals (default: 0.0)
        """
        self.lookback_days = lookback_days
        self.min_confidence = min_confidence
        self.results: List[ScreenerResult] = []

        logger.info(
            f"Initialized StockScreener with {lookback_days} days lookback, "
            f"min confidence {min_confidence}%"
        )

    def scan(
        self,
        stock_symbols: List[str],
        strategy_names: Optional[List[str]] = None,
        signal_types: Optional[List[str]] = None
    ) -> List[ScreenerResult]:
        """
        Scan multiple stocks with multiple strategies.

        Args:
            stock_symbols: List of stock symbols to scan (e.g., ['RELIANCE', 'TCS'])
            strategy_names: List of strategy names to use (None = all strategies)
            signal_types: Filter by signal type ['BUY', 'SELL'] (None = both)

        Returns:
            List of ScreenerResult objects
        """
        logger.info(
            f"Starting scan of {len(stock_symbols)} stocks with "
            f"{len(strategy_names) if strategy_names else 'all'} strategies"
        )

        # Get strategies to use
        available_strategies = StrategyRegistry.list_strategies()
        if strategy_names:
            strategies_to_use = [s for s in strategy_names if s in available_strategies]
        else:
            strategies_to_use = available_strategies

        logger.info(f"Using strategies: {strategies_to_use}")

        # Prepare date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)

        # Scan each stock
        self.results = []
        adapter = AdapterFactory.get_adapter(timeframe='1d')

        total_combinations = len(stock_symbols) * len(strategies_to_use)
        processed = 0

        for symbol in stock_symbols:
            # Add .NS suffix if not present (for NSE stocks)
            if not symbol.endswith('.NS'):
                full_symbol = f"{symbol}.NS"
            else:
                full_symbol = symbol

            # Fetch data
            try:
                logger.debug(f"Fetching data for {full_symbol}...")
                data = adapter.get_historical_data(
                    symbol=full_symbol,
                    start_date=start_date,
                    end_date=end_date,
                    timeframe='1d'
                )

                if data.empty:
                    logger.warning(f"No data for {symbol}, skipping")
                    continue

                # Test each strategy on this stock
                for strategy_name in strategies_to_use:
                    processed += 1

                    try:
                        # Create strategy instance
                        strategy = StrategyRegistry.get_strategy(strategy_name)

                        # Generate signals
                        signals = strategy.analyze(data)

                        # Get most recent signal
                        if signals:
                            latest_signal = signals[-1]

                            # Check if meets criteria
                            if latest_signal.confidence >= self.min_confidence:
                                if signal_types is None or latest_signal.signal_type in signal_types:
                                    result = ScreenerResult(
                                        stock_symbol=symbol,
                                        strategy_name=strategy.name,
                                        signal_type=latest_signal.signal_type,
                                        price=latest_signal.price,
                                        confidence=latest_signal.confidence,
                                        signal_date=latest_signal.date,
                                        metadata=latest_signal.metadata
                                    )
                                    self.results.append(result)

                    except Exception as e:
                        logger.error(f"Error testing {strategy_name} on {symbol}: {e}")
                        continue

                    # Log progress
                    if processed % 10 == 0:
                        logger.info(f"Progress: {processed}/{total_combinations} combinations tested")

            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue

        logger.info(
            f"Scan complete: Found {len(self.results)} signals from "
            f"{processed} combinations tested"
        )

        return self.results

    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get screening results as a DataFrame.

        Returns:
            DataFrame with all screening results
        """
        if not self.results:
            return pd.DataFrame()

        data = [result.to_dict() for result in self.results]
        df = pd.DataFrame(data)

        # Sort by confidence (descending)
        df = df.sort_values('confidence', ascending=False)

        return df

    def filter_results(
        self,
        min_confidence: Optional[float] = None,
        signal_types: Optional[List[str]] = None,
        strategy_names: Optional[List[str]] = None,
        stock_symbols: Optional[List[str]] = None
    ) -> List[ScreenerResult]:
        """
        Filter screening results.

        Args:
            min_confidence: Minimum confidence threshold
            signal_types: Filter by signal type (BUY/SELL)
            strategy_names: Filter by strategy name
            stock_symbols: Filter by stock symbol

        Returns:
            Filtered list of results
        """
        filtered = self.results

        if min_confidence is not None:
            filtered = [r for r in filtered if r.confidence >= min_confidence]

        if signal_types:
            filtered = [r for r in filtered if r.signal_type in signal_types]

        if strategy_names:
            filtered = [r for r in filtered if r.strategy_name in strategy_names]

        if stock_symbols:
            filtered = [r for r in filtered if r.stock_symbol in stock_symbols]

        return filtered

    def get_top_signals(
        self,
        n: int = 10,
        signal_type: Optional[str] = None
    ) -> List[ScreenerResult]:
        """
        Get top N signals by confidence.

        Args:
            n: Number of top results to return
            signal_type: Filter by signal type (BUY/SELL)

        Returns:
            Top N screening results
        """
        filtered = self.results

        if signal_type:
            filtered = [r for r in filtered if r.signal_type == signal_type]

        # Sort by confidence
        sorted_results = sorted(filtered, key=lambda x: x.confidence, reverse=True)

        return sorted_results[:n]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of screening results.

        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'stocks_scanned': 0,
                'strategies_used': 0,
                'avg_confidence': 0
            }

        buy_signals = [r for r in self.results if r.signal_type == 'BUY']
        sell_signals = [r for r in self.results if r.signal_type == 'SELL']

        unique_stocks = len(set(r.stock_symbol for r in self.results))
        unique_strategies = len(set(r.strategy_name for r in self.results))
        avg_confidence = sum(r.confidence for r in self.results) / len(self.results)

        return {
            'total_signals': len(self.results),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'stocks_scanned': unique_stocks,
            'strategies_used': unique_strategies,
            'avg_confidence': round(avg_confidence, 2),
            'top_buy': self.get_top_signals(1, 'BUY')[0] if buy_signals else None,
            'top_sell': self.get_top_signals(1, 'SELL')[0] if sell_signals else None
        }

    def export_to_csv(self, filepath: str):
        """
        Export screening results to CSV.

        Args:
            filepath: Path to save CSV file
        """
        df = self.get_results_dataframe()
        df.to_csv(filepath, index=False)
        logger.info(f"Results exported to {filepath}")

    def get_signals_by_stock(self) -> Dict[str, List[ScreenerResult]]:
        """
        Group signals by stock symbol.

        Returns:
            Dictionary mapping stock symbols to their signals
        """
        signals_by_stock = {}

        for result in self.results:
            if result.stock_symbol not in signals_by_stock:
                signals_by_stock[result.stock_symbol] = []
            signals_by_stock[result.stock_symbol].append(result)

        return signals_by_stock

    def get_signals_by_strategy(self) -> Dict[str, List[ScreenerResult]]:
        """
        Group signals by strategy name.

        Returns:
            Dictionary mapping strategy names to their signals
        """
        signals_by_strategy = {}

        for result in self.results:
            if result.strategy_name not in signals_by_strategy:
                signals_by_strategy[result.strategy_name] = []
            signals_by_strategy[result.strategy_name].append(result)

        return signals_by_strategy
