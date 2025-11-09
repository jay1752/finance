"""
Simple backtesting engine for strategy validation.

This engine simulates trading based on strategy signals and calculates performance metrics.
"""
import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from src.strategies.base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a completed trade."""
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: int
    profit_loss: float
    profit_loss_pct: float
    trade_type: str  # LONG, SHORT

    def to_dict(self) -> dict:
        """Convert trade to dictionary."""
        return asdict(self)

    def __repr__(self):
        return (
            f"Trade({self.trade_type}: {self.entry_date} → {self.exit_date}, "
            f"P&L: ₹{self.profit_loss:.2f} ({self.profit_loss_pct:.2f}%))"
        )


class BacktestEngine:
    """
    Simple backtesting engine for strategy validation.

    This engine:
    1. Takes historical price data and a strategy
    2. Generates signals using the strategy
    3. Simulates trades based on signals
    4. Calculates performance metrics

    Assumptions:
    - Trades execute at closing price on signal day
    - No slippage or transaction costs (can be added later)
    - Trades full capital on each signal (no position sizing yet)
    - Only long positions (no short selling in Phase 1)
    """

    def __init__(self, initial_capital: float = 100000):
        """
        Initialize backtesting engine.

        Args:
            initial_capital: Starting capital in rupees (default: ₹1,00,000)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None  # Current open position
        self.trades: List[Trade] = []

        logger.info(f"Initialized BacktestEngine with capital: ₹{initial_capital:,.2f}")

    def run(
        self,
        data: pd.DataFrame,
        strategy: BaseStrategy
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data.

        Args:
            data: Historical OHLCV data
            strategy: Strategy instance to test

        Returns:
            Dictionary with backtest results and metrics
        """
        logger.info(f"Running backtest for {strategy.name} on {len(data)} days of data")

        # Reset state
        self.capital = self.initial_capital
        self.position = None
        self.trades = []

        # Generate signals
        signals = strategy.analyze(data)
        logger.info(f"Generated {len(signals)} signals")

        if not signals:
            logger.warning("No signals generated, returning empty results")
            return self._empty_results()

        # Execute trades based on signals
        for signal in signals:
            self._execute_signal(signal, data)

        # Close any open position at end of period
        if self.position:
            last_price = float(data['close'].iloc[-1])
            last_date = str(data.index[-1].date())
            self._close_position(last_date, last_price)
            logger.info(f"Closed final position at {last_date}")

        # Calculate performance metrics
        results = self._calculate_metrics(data, strategy.name)

        logger.info(
            f"Backtest complete: {results['total_trades']} trades, "
            f"{results['total_return_pct']:.2f}% return"
        )

        return results

    def _execute_signal(self, signal: Signal, data: pd.DataFrame):
        """
        Execute trade based on signal.

        Args:
            signal: Trading signal
            data: Price data for validation
        """
        if signal.signal_type == 'BUY' and self.position is None:
            # Open long position
            quantity = int(self.capital / signal.price)

            if quantity == 0:
                logger.warning(f"Insufficient capital to buy at ₹{signal.price}")
                return

            self.position = {
                'type': 'LONG',
                'entry_date': signal.date,
                'entry_price': signal.price,
                'quantity': quantity
            }

            # Deduct capital
            self.capital -= quantity * signal.price

            logger.debug(
                f"Opened LONG position: {quantity} shares @ ₹{signal.price} "
                f"on {signal.date}"
            )

        elif signal.signal_type == 'SELL' and self.position and self.position['type'] == 'LONG':
            # Close long position
            self._close_position(signal.date, signal.price)

    def _close_position(self, exit_date: str, exit_price: float):
        """
        Close current position and record trade.

        Args:
            exit_date: Exit date (YYYY-MM-DD)
            exit_price: Exit price
        """
        if not self.position:
            return

        entry_price = self.position['entry_price']
        quantity = self.position['quantity']

        # Calculate P&L
        exit_value = quantity * exit_price
        entry_value = quantity * entry_price
        profit_loss = exit_value - entry_value
        profit_loss_pct = (profit_loss / entry_value) * 100

        # Record trade
        trade = Trade(
            entry_date=self.position['entry_date'],
            exit_date=exit_date,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct,
            trade_type=self.position['type']
        )

        self.trades.append(trade)

        # Update capital
        self.capital += exit_value

        logger.debug(
            f"Closed {trade.trade_type} position: "
            f"{quantity} shares @ ₹{exit_price}, "
            f"P&L: ₹{profit_loss:,.2f} ({profit_loss_pct:.2f}%)"
        )

        # Clear position
        self.position = None

    def _calculate_metrics(self, data: pd.DataFrame, strategy_name: str) -> Dict[str, Any]:
        """
        Calculate backtest performance metrics.

        Args:
            data: Price data
            strategy_name: Name of strategy

        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return self._empty_results()

        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.profit_loss > 0]
        losing_trades = [t for t in self.trades if t.profit_loss <= 0]

        total_return = self.capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0

        avg_profit = (
            sum(t.profit_loss for t in winning_trades) / len(winning_trades)
            if winning_trades else 0
        )
        avg_loss = (
            sum(t.profit_loss for t in losing_trades) / len(losing_trades)
            if losing_trades else 0
        )

        max_profit = max((t.profit_loss for t in self.trades), default=0)
        max_loss = min((t.profit_loss for t in self.trades), default=0)

        # Calculate additional metrics
        start_date = str(data.index[0].date())
        end_date = str(data.index[-1].date())

        # Calculate advanced metrics
        returns = [t.profit_loss_pct for t in self.trades]

        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe_ratio = 0
        if len(returns) > 1:
            import numpy as np
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0

        # Sortino Ratio (only downside deviation)
        sortino_ratio = 0
        if len(returns) > 1:
            import numpy as np
            avg_return = np.mean(returns)
            downside_returns = [r for r in returns if r < 0]
            if downside_returns:
                downside_std = np.std(downside_returns)
                sortino_ratio = (avg_return / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        # Max Drawdown
        max_drawdown = self._calculate_max_drawdown()

        # Calmar Ratio (annualized return / max drawdown)
        calmar_ratio = 0
        if max_drawdown != 0:
            days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
            years = days / 365.25
            annualized_return = ((1 + total_return_pct / 100) ** (1 / years) - 1) * 100 if years > 0 else total_return_pct
            calmar_ratio = abs(annualized_return / max_drawdown)

        return {
            'strategy_name': strategy_name,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_capital': round(self.capital, 2),
            'total_return': round(total_return, 2),
            'total_return_pct': round(total_return_pct, 2),
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'max_profit': round(max_profit, 2),
            'max_loss': round(max_loss, 2),
            'profit_factor': round(
                abs(sum(t.profit_loss for t in winning_trades) / sum(t.profit_loss for t in losing_trades))
                if losing_trades and sum(t.profit_loss for t in losing_trades) != 0 else 0,
                2
            ),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'sortino_ratio': round(sortino_ratio, 3),
            'max_drawdown': round(max_drawdown, 2),
            'calmar_ratio': round(calmar_ratio, 3),
            'trades': self.trades
        }

    def _calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown from trades.

        Returns:
            Maximum drawdown as percentage
        """
        if not self.trades:
            return 0

        # Build equity curve
        equity = [self.initial_capital]
        for trade in self.trades:
            equity.append(equity[-1] + trade.profit_loss)

        # Calculate drawdown at each point
        peak = equity[0]
        max_dd = 0

        for value in equity:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd

    def _empty_results(self) -> Dict[str, Any]:
        """Return empty results when no trades executed."""
        return {
            'strategy_name': '',
            'start_date': None,
            'end_date': None,
            'initial_capital': self.initial_capital,
            'final_capital': self.initial_capital,
            'total_return': 0,
            'total_return_pct': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'max_profit': 0,
            'max_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'max_drawdown': 0,
            'calmar_ratio': 0,
            'trades': []
        }

    def get_equity_curve(self) -> pd.DataFrame:
        """
        Generate equity curve from trades.

        Returns:
            DataFrame with date and portfolio value
        """
        if not self.trades:
            return pd.DataFrame()

        equity_data = []
        current_capital = self.initial_capital

        # Add initial capital
        first_trade = self.trades[0]
        equity_data.append({
            'date': first_trade.entry_date,
            'capital': current_capital
        })

        # Add each trade's effect on capital
        for trade in self.trades:
            current_capital += trade.profit_loss
            equity_data.append({
                'date': trade.exit_date,
                'capital': current_capital
            })

        df = pd.DataFrame(equity_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        return df
