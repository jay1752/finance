"""
Parameter Optimization Engine for Strategy Tuning.

This module provides grid search optimization to find the best parameters
for trading strategies based on historical performance.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from itertools import product
import logging

from src.strategies.base import BaseStrategy
from src.backtesting.engine import BacktestEngine

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result from a single parameter combination test."""
    params: Dict[str, Any]
    metrics: Dict[str, Any]

    def __repr__(self):
        return (
            f"OptimizationResult("
            f"params={self.params}, "
            f"return={self.metrics.get('total_return_pct', 0):.2f}%)"
        )


class ParameterOptimizer:
    """
    Grid search parameter optimization for trading strategies.

    This optimizer:
    1. Takes parameter ranges to test
    2. Generates all combinations (grid search)
    3. Runs backtest for each combination
    4. Ranks results by chosen metric
    5. Returns best parameters
    """

    def __init__(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        initial_capital: float = 100000,
        optimization_metric: str = 'total_return_pct'
    ):
        """
        Initialize parameter optimizer.

        Args:
            strategy_class: Strategy class to optimize (not instance)
            data: Historical OHLCV data for backtesting
            initial_capital: Starting capital for each backtest
            optimization_metric: Metric to optimize (default: total_return_pct)
                Options: total_return_pct, win_rate, profit_factor, sharpe_ratio
        """
        self.strategy_class = strategy_class
        self.data = data
        self.initial_capital = initial_capital
        self.optimization_metric = optimization_metric
        self.results: List[OptimizationResult] = []

        logger.info(
            f"Initialized ParameterOptimizer for {strategy_class.__name__} "
            f"optimizing {optimization_metric}"
        )

    def optimize(
        self,
        param_ranges: Dict[str, List],
        max_combinations: int = 1000,
        min_trades: int = 5
    ) -> List[OptimizationResult]:
        """
        Run grid search optimization over parameter ranges.

        Args:
            param_ranges: Dictionary mapping parameter names to lists of values to test
                Example: {'period': [10, 20, 30], 'threshold': [0.5, 1.0, 1.5]}
            max_combinations: Maximum number of combinations to test (default: 1000)
            min_trades: Minimum trades required for valid result (default: 5)

        Returns:
            List of OptimizationResult objects, sorted by optimization metric (best first)
        """
        logger.info(f"Starting optimization with parameter ranges: {param_ranges}")

        # Generate all parameter combinations
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(product(*param_values))

        total_combinations = len(combinations)
        logger.info(f"Total combinations to test: {total_combinations}")

        if total_combinations > max_combinations:
            logger.warning(
                f"Too many combinations ({total_combinations}). "
                f"Limiting to first {max_combinations}"
            )
            combinations = combinations[:max_combinations]

        # Test each combination
        self.results = []
        for i, values in enumerate(combinations, 1):
            params = dict(zip(param_names, values))

            try:
                # Create strategy instance with these parameters
                strategy = self.strategy_class(**params)

                # Run backtest
                engine = BacktestEngine(initial_capital=self.initial_capital)
                metrics = engine.run(self.data, strategy)

                # Only include results with minimum trades
                if metrics['total_trades'] >= min_trades:
                    result = OptimizationResult(
                        params=params,
                        metrics=metrics
                    )
                    self.results.append(result)

                    if i % 50 == 0:
                        logger.info(
                            f"Progress: {i}/{len(combinations)} - "
                            f"Current: {params}, "
                            f"Return: {metrics['total_return_pct']:.2f}%"
                        )
                else:
                    logger.debug(
                        f"Skipping {params}: only {metrics['total_trades']} trades "
                        f"(min: {min_trades})"
                    )

            except Exception as e:
                logger.error(f"Error testing params {params}: {e}")
                continue

        # Sort results by optimization metric (descending)
        self.results.sort(
            key=lambda x: x.metrics.get(self.optimization_metric, 0),
            reverse=True
        )

        logger.info(
            f"Optimization complete: {len(self.results)} valid results from "
            f"{len(combinations)} combinations tested"
        )

        if self.results:
            best = self.results[0]
            logger.info(
                f"Best parameters: {best.params} → "
                f"{self.optimization_metric}={best.metrics[self.optimization_metric]:.2f}"
            )

        return self.results

    def get_best_params(self, top_n: int = 1) -> List[Dict[str, Any]]:
        """
        Get the best parameter combinations.

        Args:
            top_n: Number of top results to return (default: 1)

        Returns:
            List of parameter dictionaries
        """
        if not self.results:
            logger.warning("No optimization results available")
            return []

        return [r.params for r in self.results[:top_n]]

    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get optimization results as a DataFrame for analysis.

        Returns:
            DataFrame with parameters and metrics for each combination
        """
        if not self.results:
            return pd.DataFrame()

        data = []
        for result in self.results:
            row = {**result.params, **result.metrics}
            data.append(row)

        df = pd.DataFrame(data)

        # Sort by optimization metric
        df = df.sort_values(
            by=self.optimization_metric,
            ascending=False
        )

        return df

    def get_optimization_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of optimization results.

        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {}

        df = self.get_results_dataframe()

        return {
            'total_combinations_tested': len(self.results),
            'best_params': self.results[0].params if self.results else {},
            'best_score': self.results[0].metrics.get(self.optimization_metric, 0) if self.results else 0,
            'worst_score': self.results[-1].metrics.get(self.optimization_metric, 0) if self.results else 0,
            'avg_score': df[self.optimization_metric].mean() if not df.empty else 0,
            'std_score': df[self.optimization_metric].std() if not df.empty else 0,
            'optimization_metric': self.optimization_metric
        }


class WalkForwardOptimizer:
    """
    Walk-forward analysis for strategy validation.

    Walk-forward analysis:
    1. Splits data into train/test windows
    2. Optimizes parameters on train window
    3. Tests on out-of-sample test window
    4. Rolls forward and repeats

    This helps avoid overfitting and validates robustness.
    """

    def __init__(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        train_size: int = 252,  # 1 year
        test_size: int = 63,    # 3 months
        initial_capital: float = 100000
    ):
        """
        Initialize walk-forward optimizer.

        Args:
            strategy_class: Strategy class to test
            data: Historical OHLCV data
            train_size: Number of days for training window
            test_size: Number of days for testing window
            initial_capital: Starting capital
        """
        self.strategy_class = strategy_class
        self.data = data
        self.train_size = train_size
        self.test_size = test_size
        self.initial_capital = initial_capital
        self.walk_results = []

        logger.info(
            f"Initialized WalkForwardOptimizer: "
            f"train={train_size} days, test={test_size} days"
        )

    def run_walk_forward(
        self,
        param_ranges: Dict[str, List],
        optimization_metric: str = 'total_return_pct'
    ) -> List[Dict[str, Any]]:
        """
        Run walk-forward analysis.

        Args:
            param_ranges: Parameter ranges for optimization
            optimization_metric: Metric to optimize

        Returns:
            List of results for each walk period
        """
        total_bars = len(self.data)
        window_size = self.train_size + self.test_size

        if total_bars < window_size:
            logger.error(
                f"Insufficient data: need {window_size} bars, "
                f"have {total_bars}"
            )
            return []

        # Calculate number of walk-forward periods
        num_periods = (total_bars - self.train_size) // self.test_size

        logger.info(f"Running {num_periods} walk-forward periods")

        self.walk_results = []

        for period in range(num_periods):
            train_start = period * self.test_size
            train_end = train_start + self.train_size
            test_start = train_end
            test_end = test_start + self.test_size

            if test_end > total_bars:
                break

            # Split data
            train_data = self.data.iloc[train_start:train_end]
            test_data = self.data.iloc[test_start:test_end]

            logger.info(
                f"Period {period + 1}/{num_periods}: "
                f"Train {train_data.index[0].date()} - {train_data.index[-1].date()}, "
                f"Test {test_data.index[0].date()} - {test_data.index[-1].date()}"
            )

            # Optimize on training data
            optimizer = ParameterOptimizer(
                strategy_class=self.strategy_class,
                data=train_data,
                initial_capital=self.initial_capital,
                optimization_metric=optimization_metric
            )

            train_results = optimizer.optimize(param_ranges)

            if not train_results:
                logger.warning(f"No valid results for period {period + 1}")
                continue

            best_params = train_results[0].params
            train_metrics = train_results[0].metrics

            # Test on out-of-sample data
            strategy = self.strategy_class(**best_params)
            engine = BacktestEngine(initial_capital=self.initial_capital)
            test_metrics = engine.run(test_data, strategy)

            # Record results
            result = {
                'period': period + 1,
                'train_start': str(train_data.index[0].date()),
                'train_end': str(train_data.index[-1].date()),
                'test_start': str(test_data.index[0].date()),
                'test_end': str(test_data.index[-1].date()),
                'best_params': best_params,
                'train_return': train_metrics['total_return_pct'],
                'test_return': test_metrics['total_return_pct'],
                'train_trades': train_metrics['total_trades'],
                'test_trades': test_metrics['total_trades'],
                'train_win_rate': train_metrics['win_rate'],
                'test_win_rate': test_metrics['win_rate']
            }

            self.walk_results.append(result)

            logger.info(
                f"Period {period + 1} complete: "
                f"Train={train_metrics['total_return_pct']:.2f}%, "
                f"Test={test_metrics['total_return_pct']:.2f}%"
            )

        return self.walk_results

    def get_summary(self) -> Dict[str, Any]:
        """Get walk-forward analysis summary."""
        if not self.walk_results:
            return {}

        train_returns = [r['train_return'] for r in self.walk_results]
        test_returns = [r['test_return'] for r in self.walk_results]

        return {
            'total_periods': len(self.walk_results),
            'avg_train_return': np.mean(train_returns),
            'avg_test_return': np.mean(test_returns),
            'std_train_return': np.std(train_returns),
            'std_test_return': np.std(test_returns),
            'periods_profitable': sum(1 for r in test_returns if r > 0),
            'consistency_score': np.corrcoef(train_returns, test_returns)[0, 1] if len(train_returns) > 1 else 0
        }
