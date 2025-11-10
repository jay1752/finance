"""
Performance Tracker - Track and analyze strategy performance over time.

Stores backtest results and provides performance analytics:
- Strategy win rates
- Profit/Loss trends
- Performance comparison
- Historical metrics
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceRecord:
    """Single performance record from a backtest."""
    timestamp: datetime
    symbol: str
    strategy_name: str
    timeframe: str
    period_days: int

    # Core metrics
    total_return_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float

    # Trade metrics
    total_trades: int
    win_rate_pct: float
    profit_factor: float
    avg_win_pct: float
    avg_loss_pct: float

    # Additional info
    initial_capital: float
    final_capital: float
    metadata: Dict[str, Any]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'PerformanceRecord':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class PerformanceTracker:
    """
    Track and analyze strategy performance over time.

    Stores backtest results in JSON files and provides analytics.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize performance tracker.

        Args:
            storage_dir: Directory to store performance records
                        Defaults to ./data/performance/
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / 'data' / 'performance'

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.records_file = self.storage_dir / 'performance_records.json'
        self.records: List[PerformanceRecord] = []

        # Load existing records
        self._load_records()

        logger.info(f"PerformanceTracker initialized with {len(self.records)} records")

    def add_record(
        self,
        symbol: str,
        strategy_name: str,
        backtest_results: Dict[str, Any],
        timeframe: str = '1d',
        metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceRecord:
        """
        Add a new performance record from backtest results.

        Args:
            symbol: Stock symbol
            strategy_name: Strategy name
            backtest_results: Results from BacktestEngine.run()
            timeframe: Timeframe used
            metadata: Additional metadata

        Returns:
            Created PerformanceRecord
        """
        if metadata is None:
            metadata = {}

        record = PerformanceRecord(
            timestamp=datetime.now(),
            symbol=symbol,
            strategy_name=strategy_name,
            timeframe=timeframe,
            period_days=backtest_results.get('period_days', 0),
            total_return_pct=backtest_results.get('total_return_pct', 0.0),
            sharpe_ratio=backtest_results.get('sharpe_ratio', 0.0),
            sortino_ratio=backtest_results.get('sortino_ratio', 0.0),
            max_drawdown_pct=backtest_results.get('max_drawdown', 0.0),
            total_trades=backtest_results.get('total_trades', 0),
            win_rate_pct=backtest_results.get('win_rate', 0.0),
            profit_factor=backtest_results.get('profit_factor', 0.0),
            avg_win_pct=backtest_results.get('avg_win_pct', 0.0),
            avg_loss_pct=backtest_results.get('avg_loss_pct', 0.0),
            initial_capital=backtest_results.get('initial_capital', 100000.0),
            final_capital=backtest_results.get('final_capital', 100000.0),
            metadata=metadata
        )

        self.records.append(record)
        self._save_records()

        logger.info(f"Added performance record for {symbol}/{strategy_name}")

        return record

    def get_strategy_performance(
        self,
        strategy_name: str,
        days_back: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get performance history for a specific strategy.

        Args:
            strategy_name: Strategy name
            days_back: Only include records from last N days

        Returns:
            DataFrame with performance records
        """
        filtered = [r for r in self.records if r.strategy_name == strategy_name]

        if days_back:
            cutoff = datetime.now() - timedelta(days=days_back)
            filtered = [r for r in filtered if r.timestamp >= cutoff]

        if not filtered:
            return pd.DataFrame()

        return pd.DataFrame([r.to_dict() for r in filtered])

    def get_symbol_performance(
        self,
        symbol: str,
        days_back: Optional[int] = None
    ) -> pd.DataFrame:
        """Get performance history for a specific symbol."""
        filtered = [r for r in self.records if r.symbol == symbol]

        if days_back:
            cutoff = datetime.now() - timedelta(days=days_back)
            filtered = [r for r in filtered if r.timestamp >= cutoff]

        if not filtered:
            return pd.DataFrame()

        return pd.DataFrame([r.to_dict() for r in filtered])

    def get_all_records(self, days_back: Optional[int] = None) -> pd.DataFrame:
        """Get all performance records."""
        filtered = self.records

        if days_back:
            cutoff = datetime.now() - timedelta(days=days_back)
            filtered = [r for r in self.records if r.timestamp >= cutoff]

        if not filtered:
            return pd.DataFrame()

        return pd.DataFrame([r.to_dict() for r in filtered])

    def get_strategy_stats(self, strategy_name: str) -> Dict[str, Any]:
        """
        Get aggregate statistics for a strategy.

        Returns:
            Dictionary with aggregate metrics
        """
        df = self.get_strategy_performance(strategy_name)

        if df.empty:
            return {}

        return {
            'strategy_name': strategy_name,
            'total_backtests': len(df),
            'avg_return_pct': df['total_return_pct'].mean(),
            'median_return_pct': df['total_return_pct'].median(),
            'avg_sharpe': df['sharpe_ratio'].mean(),
            'avg_win_rate': df['win_rate_pct'].mean(),
            'avg_max_drawdown': df['max_drawdown_pct'].mean(),
            'best_return': df['total_return_pct'].max(),
            'worst_return': df['total_return_pct'].min(),
            'consistency_score': self._calculate_consistency(df),
            'last_updated': df['timestamp'].max()
        }

    def compare_strategies(
        self,
        strategy_names: List[str],
        metric: str = 'sharpe_ratio'
    ) -> pd.DataFrame:
        """
        Compare multiple strategies on a specific metric.

        Args:
            strategy_names: List of strategy names to compare
            metric: Metric to compare ('sharpe_ratio', 'total_return_pct', etc.)

        Returns:
            DataFrame with comparison data
        """
        comparison = []

        for strategy in strategy_names:
            stats = self.get_strategy_stats(strategy)

            if stats:
                comparison.append({
                    'Strategy': strategy,
                    'Avg Return %': stats.get('avg_return_pct', 0),
                    'Avg Sharpe': stats.get('avg_sharpe', 0),
                    'Avg Win Rate %': stats.get('avg_win_rate', 0),
                    'Avg Max DD %': stats.get('avg_max_drawdown', 0),
                    'Consistency': stats.get('consistency_score', 0),
                    'Total Tests': stats.get('total_backtests', 0)
                })

        return pd.DataFrame(comparison)

    def get_performance_trends(
        self,
        strategy_name: str,
        metric: str = 'total_return_pct',
        window_days: int = 30
    ) -> pd.DataFrame:
        """
        Get performance trends over time for a strategy.

        Args:
            strategy_name: Strategy name
            metric: Metric to track
            window_days: Rolling window size in days

        Returns:
            DataFrame with time-series data
        """
        df = self.get_strategy_performance(strategy_name)

        if df.empty:
            return pd.DataFrame()

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Calculate rolling average
        df[f'{metric}_ma'] = df[metric].rolling(window=window_days, min_periods=1).mean()

        return df[['timestamp', metric, f'{metric}_ma']]

    def clear_old_records(self, days_back: int = 90):
        """Delete records older than N days."""
        cutoff = datetime.now() - timedelta(days=days_back)
        original_count = len(self.records)

        self.records = [r for r in self.records if r.timestamp >= cutoff]

        deleted = original_count - len(self.records)
        self._save_records()

        logger.info(f"Deleted {deleted} old records (older than {days_back} days)")

        return deleted

    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """
        Calculate consistency score (0-100).

        Based on standard deviation of returns - lower is more consistent.
        """
        if df.empty or len(df) < 2:
            return 0.0

        # Lower std dev = higher consistency
        std_dev = df['total_return_pct'].std()
        mean_return = df['total_return_pct'].mean()

        if mean_return == 0:
            return 0.0

        # Coefficient of variation (inverted and scaled)
        cv = std_dev / abs(mean_return)
        consistency = max(0, 100 - (cv * 10))

        return min(100, consistency)

    def _load_records(self):
        """Load records from JSON file."""
        if not self.records_file.exists():
            logger.info("No existing performance records found")
            return

        try:
            with open(self.records_file, 'r') as f:
                data = json.load(f)

            self.records = [PerformanceRecord.from_dict(r) for r in data]
            logger.info(f"Loaded {len(self.records)} performance records")

        except Exception as e:
            logger.error(f"Error loading performance records: {e}")
            self.records = []

    def _save_records(self):
        """Save records to JSON file."""
        try:
            data = [r.to_dict() for r in self.records]

            with open(self.records_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(self.records)} performance records")

        except Exception as e:
            logger.error(f"Error saving performance records: {e}")

    def export_to_csv(self, filepath: str):
        """Export all records to CSV."""
        df = self.get_all_records()

        if df.empty:
            logger.warning("No records to export")
            return

        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(df)} records to {filepath}")
