"""
Strategy Comparison Module.

Compare multiple trading strategies side-by-side on the same data
to identify the best performers.
"""
import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

from src.strategies.base import BaseStrategy
from src.backtesting.engine import BacktestEngine

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Result from comparing a single strategy."""
    strategy_name: str
    strategy: BaseStrategy
    metrics: Dict[str, Any]
    equity_curve: pd.DataFrame

    def __repr__(self):
        return (
            f"ComparisonResult({self.strategy_name}: "
            f"{self.metrics.get('total_return_pct', 0):.2f}% return, "
            f"{self.metrics.get('total_trades', 0)} trades)"
        )


class StrategyComparator:
    """
    Compare multiple trading strategies on the same dataset.

    This comparator:
    1. Runs backtests for all strategies
    2. Collects performance metrics
    3. Ranks strategies by various metrics
    4. Generates comparison tables and charts
    """

    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 100000
    ):
        """
        Initialize strategy comparator.

        Args:
            data: Historical OHLCV data
            initial_capital: Starting capital for all backtests
        """
        self.data = data
        self.initial_capital = initial_capital
        self.results: List[ComparisonResult] = []

        logger.info(
            f"Initialized StrategyComparator with {len(data)} bars "
            f"and ₹{initial_capital:,.0f} initial capital"
        )

    def add_strategy(
        self,
        strategy: BaseStrategy,
        name: str = None
    ):
        """
        Add a strategy to compare.

        Args:
            strategy: Strategy instance to test
            name: Optional custom name (uses strategy.name if not provided)
        """
        strategy_name = name or strategy.name

        logger.info(f"Running backtest for {strategy_name}...")

        # Run backtest
        engine = BacktestEngine(initial_capital=self.initial_capital)
        metrics = engine.run(self.data, strategy)
        equity_curve = engine.get_equity_curve()

        # Store result
        result = ComparisonResult(
            strategy_name=strategy_name,
            strategy=strategy,
            metrics=metrics,
            equity_curve=equity_curve
        )

        self.results.append(result)

        logger.info(
            f"{strategy_name}: {metrics['total_trades']} trades, "
            f"{metrics['total_return_pct']:.2f}% return"
        )

    def add_strategies(
        self,
        strategies: List[BaseStrategy],
        names: List[str] = None
    ):
        """
        Add multiple strategies at once.

        Args:
            strategies: List of strategy instances
            names: Optional list of custom names
        """
        if names and len(names) != len(strategies):
            raise ValueError("Number of names must match number of strategies")

        for i, strategy in enumerate(strategies):
            name = names[i] if names else None
            self.add_strategy(strategy, name)

    def get_comparison_table(
        self,
        metrics: List[str] = None
    ) -> pd.DataFrame:
        """
        Get comparison table with key metrics for all strategies.

        Args:
            metrics: List of metric names to include (None = all common metrics)

        Returns:
            DataFrame with strategies as rows and metrics as columns
        """
        if not self.results:
            logger.warning("No strategies to compare")
            return pd.DataFrame()

        # Default metrics to compare
        if metrics is None:
            metrics = [
                'total_return_pct',
                'total_trades',
                'win_rate',
                'profit_factor',
                'avg_profit',
                'avg_loss',
                'max_profit',
                'max_loss'
            ]

        # Build comparison data
        data = []
        for result in self.results:
            row = {'strategy': result.strategy_name}
            for metric in metrics:
                row[metric] = result.metrics.get(metric, 0)
            data.append(row)

        df = pd.DataFrame(data)

        # Sort by total return (descending)
        if 'total_return_pct' in df.columns:
            df = df.sort_values('total_return_pct', ascending=False)

        return df

    def get_rankings(
        self,
        metric: str = 'total_return_pct'
    ) -> List[Dict[str, Any]]:
        """
        Get strategies ranked by a specific metric.

        Args:
            metric: Metric to rank by (default: total_return_pct)

        Returns:
            List of dictionaries with rank, strategy name, and metric value
        """
        if not self.results:
            return []

        # Sort results by metric
        sorted_results = sorted(
            self.results,
            key=lambda x: x.metrics.get(metric, 0),
            reverse=True
        )

        rankings = []
        for i, result in enumerate(sorted_results, 1):
            rankings.append({
                'rank': i,
                'strategy': result.strategy_name,
                metric: result.metrics.get(metric, 0)
            })

        return rankings

    def get_best_strategy(
        self,
        metric: str = 'total_return_pct'
    ) -> ComparisonResult:
        """
        Get the best performing strategy by a metric.

        Args:
            metric: Metric to evaluate (default: total_return_pct)

        Returns:
            ComparisonResult for best strategy
        """
        if not self.results:
            raise ValueError("No strategies to compare")

        return max(
            self.results,
            key=lambda x: x.metrics.get(metric, 0)
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics across all strategies.

        Returns:
            Dictionary with comparison statistics
        """
        if not self.results:
            return {}

        returns = [r.metrics['total_return_pct'] for r in self.results]
        trades = [r.metrics['total_trades'] for r in self.results]
        win_rates = [r.metrics['win_rate'] for r in self.results]

        best = max(self.results, key=lambda x: x.metrics['total_return_pct'])
        worst = min(self.results, key=lambda x: x.metrics['total_return_pct'])

        return {
            'total_strategies': len(self.results),
            'best_strategy': best.strategy_name,
            'best_return': best.metrics['total_return_pct'],
            'worst_strategy': worst.strategy_name,
            'worst_return': worst.metrics['total_return_pct'],
            'avg_return': sum(returns) / len(returns),
            'avg_trades': sum(trades) / len(trades),
            'avg_win_rate': sum(win_rates) / len(win_rates),
            'strategies_profitable': sum(1 for r in returns if r > 0),
            'strategies_unprofitable': sum(1 for r in returns if r <= 0)
        }

    def get_equity_curves(self) -> Dict[str, pd.DataFrame]:
        """
        Get equity curves for all strategies.

        Returns:
            Dictionary mapping strategy names to equity curve DataFrames
        """
        return {
            result.strategy_name: result.equity_curve
            for result in self.results
        }

    def get_combined_equity_curve(self) -> pd.DataFrame:
        """
        Get combined equity curve with all strategies.

        Returns:
            DataFrame with date index and columns for each strategy
        """
        if not self.results:
            return pd.DataFrame()

        # Combine all equity curves
        curves = {}
        for result in self.results:
            if not result.equity_curve.empty:
                curves[result.strategy_name] = result.equity_curve['capital']

        if not curves:
            return pd.DataFrame()

        # Create combined DataFrame
        df = pd.DataFrame(curves)

        # Forward fill missing values
        df = df.fillna(method='ffill')
        df = df.fillna(self.initial_capital)

        return df

    def get_detailed_comparison(self) -> List[Dict[str, Any]]:
        """
        Get detailed comparison with all metrics for each strategy.

        Returns:
            List of dictionaries with full metrics for each strategy
        """
        comparison = []
        for result in self.results:
            entry = {
                'strategy': result.strategy_name,
                **result.metrics
            }
            comparison.append(entry)

        # Sort by return
        comparison.sort(
            key=lambda x: x.get('total_return_pct', 0),
            reverse=True
        )

        return comparison

    def export_to_csv(self, filepath: str):
        """
        Export comparison results to CSV.

        Args:
            filepath: Path to save CSV file
        """
        df = self.get_comparison_table()
        df.to_csv(filepath, index=False)
        logger.info(f"Comparison results exported to {filepath}")

    def get_winner_summary(self) -> str:
        """
        Get a human-readable summary of the comparison.

        Returns:
            String summarizing the comparison results
        """
        if not self.results:
            return "No strategies compared yet."

        stats = self.get_statistics()

        summary = f"""
Strategy Comparison Summary
{'=' * 70}
Strategies Compared: {stats['total_strategies']}
Data Period: {self.data.index[0].date()} to {self.data.index[-1].date()}
Initial Capital: ₹{self.initial_capital:,.0f}

🏆 Best Performer: {stats['best_strategy']}
   Return: {stats['best_return']:.2f}%

📉 Worst Performer: {stats['worst_strategy']}
   Return: {stats['worst_return']:.2f}%

📊 Overall Statistics:
   Average Return: {stats['avg_return']:.2f}%
   Average Trades: {stats['avg_trades']:.1f}
   Average Win Rate: {stats['avg_win_rate']:.1f}%
   Profitable Strategies: {stats['strategies_profitable']}/{stats['total_strategies']}

{'=' * 70}
"""
        return summary
