"""
Portfolio Management Module.

Track positions, calculate P&L, and manage portfolio-level metrics.
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import yfinance as yf

from .risk_manager import StopLoss, TakeProfit

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents a single position in the portfolio."""
    symbol: str
    shares: int
    entry_price: float
    entry_date: datetime
    stop_loss: Optional[StopLoss] = None
    take_profit: Optional[TakeProfit] = None
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    direction: str = 'LONG'
    notes: str = ''

    def __post_init__(self):
        """Validate position data."""
        if self.shares <= 0:
            raise ValueError("shares must be positive")
        if self.entry_price <= 0:
            raise ValueError("entry_price must be positive")
        if self.direction.upper() not in ['LONG', 'SHORT']:
            raise ValueError("direction must be LONG or SHORT")

    @property
    def is_open(self) -> bool:
        """Check if position is still open."""
        return self.exit_price is None

    @property
    def entry_value(self) -> float:
        """Total value at entry."""
        return self.shares * self.entry_price

    def calculate_pnl(self, current_price: float) -> Dict[str, float]:
        """
        Calculate P&L for the position.

        Args:
            current_price: Current market price

        Returns:
            Dict with pnl, pnl_pct, unrealized_pnl, realized_pnl
        """
        if self.direction.upper() == 'LONG':
            if self.is_open:
                pnl = (current_price - self.entry_price) * self.shares
                pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
                return {
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'unrealized_pnl': pnl,
                    'realized_pnl': 0.0
                }
            else:
                pnl = (self.exit_price - self.entry_price) * self.shares
                pnl_pct = ((self.exit_price - self.entry_price) / self.entry_price) * 100
                return {
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'unrealized_pnl': 0.0,
                    'realized_pnl': pnl
                }
        else:  # SHORT
            if self.is_open:
                pnl = (self.entry_price - current_price) * self.shares
                pnl_pct = ((self.entry_price - current_price) / self.entry_price) * 100
                return {
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'unrealized_pnl': pnl,
                    'realized_pnl': 0.0
                }
            else:
                pnl = (self.entry_price - self.exit_price) * self.shares
                pnl_pct = ((self.entry_price - self.exit_price) / self.entry_price) * 100
                return {
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'unrealized_pnl': 0.0,
                    'realized_pnl': pnl
                }

    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop-loss has been hit."""
        if self.stop_loss is None:
            return False

        if self.direction.upper() == 'LONG':
            return current_price <= self.stop_loss.price
        else:  # SHORT
            return current_price >= self.stop_loss.price

    def check_take_profit(self, current_price: float) -> bool:
        """Check if take-profit has been hit."""
        if self.take_profit is None:
            return False

        if self.direction.upper() == 'LONG':
            return current_price >= self.take_profit.price
        else:  # SHORT
            return current_price <= self.take_profit.price

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'shares': self.shares,
            'entry_price': self.entry_price,
            'entry_date': self.entry_date.isoformat(),
            'entry_value': self.entry_value,
            'stop_loss': self.stop_loss.price if self.stop_loss else None,
            'take_profit': self.take_profit.price if self.take_profit else None,
            'exit_price': self.exit_price,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'direction': self.direction,
            'is_open': self.is_open,
            'notes': self.notes
        }


class Portfolio:
    """
    Manage a portfolio of positions.

    Features:
    - Track multiple positions
    - Calculate portfolio-level P&L
    - Monitor risk exposure
    - Auto-check stop-loss and take-profit
    - Generate portfolio reports
    """

    def __init__(
        self,
        initial_capital: float,
        name: str = "My Portfolio"
    ):
        """
        Initialize portfolio.

        Args:
            initial_capital: Starting capital
            name: Portfolio name
        """
        self.initial_capital = initial_capital
        self.name = name
        self.positions: List[Position] = []
        self.cash = initial_capital
        self.created_at = datetime.now()

        logger.info(
            f"Portfolio '{name}' created with ₹{initial_capital:,.0f} capital"
        )

    # ==================== POSITION MANAGEMENT ====================

    def open_position(
        self,
        symbol: str,
        shares: int,
        entry_price: float,
        stop_loss: Optional[StopLoss] = None,
        take_profit: Optional[TakeProfit] = None,
        direction: str = 'LONG',
        notes: str = ''
    ) -> Position:
        """
        Open a new position.

        Args:
            symbol: Stock symbol
            shares: Number of shares
            entry_price: Entry price per share
            stop_loss: Optional stop-loss configuration
            take_profit: Optional take-profit configuration
            direction: 'LONG' or 'SHORT'
            notes: Optional notes

        Returns:
            Created Position object
        """
        # Calculate cost
        cost = shares * entry_price

        # Check if enough cash
        if cost > self.cash:
            raise ValueError(
                f"Insufficient cash: need ₹{cost:,.0f}, have ₹{self.cash:,.0f}"
            )

        # Create position
        position = Position(
            symbol=symbol,
            shares=shares,
            entry_price=entry_price,
            entry_date=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            direction=direction,
            notes=notes
        )

        # Update portfolio
        self.positions.append(position)
        self.cash -= cost

        logger.info(
            f"Opened {direction} position: {shares} shares of {symbol} "
            f"at ₹{entry_price:.2f} (cost: ₹{cost:,.0f})"
        )

        return position

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        notes: str = ''
    ) -> Position:
        """
        Close an existing position.

        Args:
            symbol: Stock symbol
            exit_price: Exit price per share
            notes: Optional notes

        Returns:
            Closed Position object
        """
        # Find open position
        position = self.get_position(symbol)
        if position is None:
            raise ValueError(f"No open position for {symbol}")

        if not position.is_open:
            raise ValueError(f"Position for {symbol} is already closed")

        # Close position
        position.exit_price = exit_price
        position.exit_date = datetime.now()
        if notes:
            position.notes += f" | Exit: {notes}"

        # Update cash
        proceeds = position.shares * exit_price
        self.cash += proceeds

        # Calculate P&L
        pnl_data = position.calculate_pnl(exit_price)

        logger.info(
            f"Closed {position.direction} position: {position.shares} shares of {symbol} "
            f"at ₹{exit_price:.2f} (P&L: ₹{pnl_data['pnl']:,.2f}, {pnl_data['pnl_pct']:.2f}%)"
        )

        return position

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get open position for a symbol."""
        for pos in self.positions:
            if pos.symbol == symbol and pos.is_open:
                return pos
        return None

    def get_all_positions(self, include_closed: bool = False) -> List[Position]:
        """
        Get all positions.

        Args:
            include_closed: Include closed positions

        Returns:
            List of positions
        """
        if include_closed:
            return self.positions
        return [p for p in self.positions if p.is_open]

    def update_stop_loss(self, symbol: str, stop_loss: StopLoss):
        """Update stop-loss for a position."""
        position = self.get_position(symbol)
        if position:
            position.stop_loss = stop_loss
            logger.info(f"Updated stop-loss for {symbol}: ₹{stop_loss.price:.2f}")
        else:
            raise ValueError(f"No open position for {symbol}")

    def update_take_profit(self, symbol: str, take_profit: TakeProfit):
        """Update take-profit for a position."""
        position = self.get_position(symbol)
        if position:
            position.take_profit = take_profit
            logger.info(f"Updated take-profit for {symbol}: ₹{take_profit.price:.2f}")
        else:
            raise ValueError(f"No open position for {symbol}")

    # ==================== P&L CALCULATION ====================

    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch current prices for symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dict mapping symbol to current price
        """
        prices = {}

        for symbol in symbols:
            try:
                # Add .NS suffix if not present
                full_symbol = symbol if symbol.endswith('.NS') else f"{symbol}.NS"

                ticker = yf.Ticker(full_symbol)
                data = ticker.history(period='1d')

                if not data.empty:
                    prices[symbol] = data['Close'].iloc[-1]
                else:
                    logger.warning(f"No price data for {symbol}")
                    prices[symbol] = 0.0
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
                prices[symbol] = 0.0

        return prices

    def calculate_portfolio_value(self, current_prices: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Calculate total portfolio value.

        Args:
            current_prices: Optional dict of current prices (fetched if not provided)

        Returns:
            Dict with portfolio metrics
        """
        open_positions = self.get_all_positions(include_closed=False)

        if not open_positions:
            return {
                'total_value': self.cash,
                'cash': self.cash,
                'positions_value': 0.0,
                'total_pnl': self.cash - self.initial_capital,
                'total_pnl_pct': ((self.cash - self.initial_capital) / self.initial_capital) * 100,
                'unrealized_pnl': 0.0,
                'realized_pnl': self.cash - self.initial_capital
            }

        # Fetch current prices if not provided
        if current_prices is None:
            symbols = [pos.symbol for pos in open_positions]
            current_prices = self.get_current_prices(symbols)

        # Calculate position values
        positions_value = 0.0
        unrealized_pnl = 0.0

        for pos in open_positions:
            current_price = current_prices.get(pos.symbol, pos.entry_price)
            pnl_data = pos.calculate_pnl(current_price)

            positions_value += pos.shares * current_price
            unrealized_pnl += pnl_data['unrealized_pnl']

        # Calculate realized P&L from closed positions
        realized_pnl = 0.0
        for pos in self.positions:
            if not pos.is_open:
                pnl_data = pos.calculate_pnl(pos.exit_price)
                realized_pnl += pnl_data['realized_pnl']

        # Total portfolio value
        total_value = self.cash + positions_value
        total_pnl = total_value - self.initial_capital
        total_pnl_pct = (total_pnl / self.initial_capital) * 100

        return {
            'total_value': total_value,
            'cash': self.cash,
            'positions_value': positions_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'unrealized_pnl': unrealized_pnl,
            'realized_pnl': realized_pnl
        }

    # ==================== RISK MONITORING ====================

    def check_stops_and_targets(self, current_prices: Optional[Dict[str, float]] = None) -> Dict[str, List[str]]:
        """
        Check if any positions have hit stop-loss or take-profit.

        Args:
            current_prices: Optional dict of current prices

        Returns:
            Dict with 'stop_loss_hit' and 'take_profit_hit' lists
        """
        open_positions = self.get_all_positions(include_closed=False)

        if not open_positions:
            return {'stop_loss_hit': [], 'take_profit_hit': []}

        # Fetch current prices if not provided
        if current_prices is None:
            symbols = [pos.symbol for pos in open_positions]
            current_prices = self.get_current_prices(symbols)

        stop_loss_hit = []
        take_profit_hit = []

        for pos in open_positions:
            current_price = current_prices.get(pos.symbol, pos.entry_price)

            if pos.check_stop_loss(current_price):
                stop_loss_hit.append(pos.symbol)
                logger.warning(
                    f"STOP-LOSS HIT: {pos.symbol} at ₹{current_price:.2f} "
                    f"(stop: ₹{pos.stop_loss.price:.2f})"
                )

            if pos.check_take_profit(current_price):
                take_profit_hit.append(pos.symbol)
                logger.info(
                    f"TAKE-PROFIT HIT: {pos.symbol} at ₹{current_price:.2f} "
                    f"(target: ₹{pos.take_profit.price:.2f})"
                )

        return {
            'stop_loss_hit': stop_loss_hit,
            'take_profit_hit': take_profit_hit
        }

    def get_risk_exposure(self) -> Dict[str, float]:
        """
        Calculate total risk exposure across portfolio.

        Returns:
            Dict with risk metrics
        """
        open_positions = self.get_all_positions(include_closed=False)

        if not open_positions:
            return {
                'total_risk': 0.0,
                'total_risk_pct': 0.0,
                'num_positions': 0
            }

        total_risk = 0.0

        for pos in open_positions:
            if pos.stop_loss:
                # Calculate risk per position
                if pos.direction.upper() == 'LONG':
                    risk_per_share = pos.entry_price - pos.stop_loss.price
                else:  # SHORT
                    risk_per_share = pos.stop_loss.price - pos.entry_price

                position_risk = risk_per_share * pos.shares
                total_risk += max(0, position_risk)

        total_risk_pct = (total_risk / self.initial_capital) * 100

        return {
            'total_risk': total_risk,
            'total_risk_pct': total_risk_pct,
            'num_positions': len(open_positions)
        }

    # ==================== REPORTING ====================

    def get_positions_dataframe(self, include_closed: bool = False) -> pd.DataFrame:
        """
        Get positions as DataFrame.

        Args:
            include_closed: Include closed positions

        Returns:
            DataFrame with position data
        """
        positions = self.get_all_positions(include_closed=include_closed)

        if not positions:
            return pd.DataFrame()

        data = [pos.to_dict() for pos in positions]
        df = pd.DataFrame(data)

        return df

    def get_summary(self, current_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Get portfolio summary.

        Args:
            current_prices: Optional dict of current prices

        Returns:
            Dict with summary statistics
        """
        portfolio_value = self.calculate_portfolio_value(current_prices)
        risk_exposure = self.get_risk_exposure()

        open_positions = self.get_all_positions(include_closed=False)
        closed_positions = [p for p in self.positions if not p.is_open]

        # Calculate win rate from closed positions
        if closed_positions:
            winning_trades = sum(
                1 for p in closed_positions
                if p.calculate_pnl(p.exit_price)['pnl'] > 0
            )
            win_rate = (winning_trades / len(closed_positions)) * 100
        else:
            win_rate = 0.0

        return {
            'portfolio_name': self.name,
            'initial_capital': self.initial_capital,
            'current_value': portfolio_value['total_value'],
            'cash': portfolio_value['cash'],
            'positions_value': portfolio_value['positions_value'],
            'total_pnl': portfolio_value['total_pnl'],
            'total_pnl_pct': portfolio_value['total_pnl_pct'],
            'unrealized_pnl': portfolio_value['unrealized_pnl'],
            'realized_pnl': portfolio_value['realized_pnl'],
            'num_open_positions': len(open_positions),
            'num_closed_positions': len(closed_positions),
            'total_risk': risk_exposure['total_risk'],
            'total_risk_pct': risk_exposure['total_risk_pct'],
            'win_rate': win_rate,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        summary = self.get_summary()
        return (
            f"Portfolio('{self.name}', "
            f"value=₹{summary['current_value']:,.0f}, "
            f"pnl=₹{summary['total_pnl']:,.0f} ({summary['total_pnl_pct']:.2f}%), "
            f"positions={summary['num_open_positions']})"
        )
