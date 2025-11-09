"""
Position Sizing Module.

Calculate optimal position sizes using various methods.
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PositionSize:
    """Result of position size calculation."""
    shares: int
    capital_allocation: float
    risk_amount: float
    method: str
    metadata: Dict[str, Any]

    def __repr__(self):
        return (
            f"PositionSize(shares={self.shares}, "
            f"allocation=₹{self.capital_allocation:,.2f}, "
            f"risk=₹{self.risk_amount:,.2f}, method={self.method})"
        )


class PositionSizer:
    """
    Calculate position sizes using various methods.

    Supports:
    - Kelly Criterion: Optimal bet sizing based on win probability and payoff
    - Fixed Fractional: Risk fixed percentage of capital per trade
    - Risk-Based: Position size based on volatility (ATR)
    - Equal Weight: Simple equal distribution
    - Fixed Amount: Fixed rupee amount per position
    """

    def __init__(
        self,
        capital: float,
        max_position_size: float = 0.20,
        max_risk_per_trade: float = 0.02
    ):
        """
        Initialize position sizer.

        Args:
            capital: Total available capital
            max_position_size: Maximum % of capital per position (default: 20%)
            max_risk_per_trade: Maximum % risk per trade (default: 2%)
        """
        self.capital = capital
        self.max_position_size = max_position_size
        self.max_risk_per_trade = max_risk_per_trade

        logger.info(
            f"PositionSizer initialized: capital=₹{capital:,.0f}, "
            f"max_position={max_position_size*100:.0f}%, "
            f"max_risk={max_risk_per_trade*100:.1f}%"
        )

    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        price: float,
        kelly_fraction: float = 0.25
    ) -> PositionSize:
        """
        Calculate position size using Kelly Criterion.

        Formula: f = (p * b - q) / b
        where:
            f = fraction of capital to bet
            p = probability of winning
            q = probability of losing (1 - p)
            b = ratio of average win to average loss

        Args:
            win_rate: Probability of winning (0-1)
            avg_win: Average win amount (%)
            avg_loss: Average loss amount (%)
            price: Current stock price
            kelly_fraction: Fraction of Kelly to use (default: 0.25 = quarter Kelly)
                          Full Kelly can be aggressive, fractional Kelly is safer

        Returns:
            PositionSize with shares and allocation
        """
        # Validate inputs
        if not 0 <= win_rate <= 1:
            raise ValueError("win_rate must be between 0 and 1")
        if avg_win <= 0 or avg_loss <= 0:
            raise ValueError("avg_win and avg_loss must be positive")

        # Calculate Kelly percentage
        p = win_rate
        q = 1 - win_rate
        b = avg_win / avg_loss

        kelly_pct = (p * b - q) / b

        # Apply Kelly fraction for safety (quarter Kelly is common)
        kelly_pct = kelly_pct * kelly_fraction

        # Cap at max position size
        kelly_pct = max(0, min(kelly_pct, self.max_position_size))

        # Calculate allocation and shares
        allocation = self.capital * kelly_pct
        shares = int(allocation / price)
        actual_allocation = shares * price

        # Calculate risk (assuming stop-loss at avg_loss %)
        risk_amount = actual_allocation * (avg_loss / 100)

        logger.debug(
            f"Kelly: win_rate={win_rate:.1%}, b={b:.2f}, "
            f"kelly={kelly_pct:.2%}, shares={shares}"
        )

        return PositionSize(
            shares=shares,
            capital_allocation=actual_allocation,
            risk_amount=risk_amount,
            method='kelly_criterion',
            metadata={
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'kelly_percentage': kelly_pct,
                'kelly_fraction_used': kelly_fraction,
                'price': price
            }
        )

    def fixed_fractional(
        self,
        price: float,
        risk_percentage: Optional[float] = None,
        stop_loss_pct: float = 5.0
    ) -> PositionSize:
        """
        Calculate position size risking fixed percentage of capital.

        Position Size = (Capital * Risk%) / (Stop Loss %)

        Args:
            price: Current stock price
            risk_percentage: % of capital to risk (default: self.max_risk_per_trade)
            stop_loss_pct: Stop-loss distance as % (default: 5%)

        Returns:
            PositionSize with shares and allocation
        """
        if risk_percentage is None:
            risk_percentage = self.max_risk_per_trade

        # Calculate risk amount
        risk_amount = self.capital * risk_percentage

        # Calculate position size
        # If stop-loss is 5% and we risk ₹2000, we can buy ₹40,000 worth
        max_allocation = risk_amount / (stop_loss_pct / 100)

        # Cap at max position size
        max_by_position_limit = self.capital * self.max_position_size
        allocation = min(max_allocation, max_by_position_limit)

        # Calculate shares
        shares = int(allocation / price)
        actual_allocation = shares * price
        actual_risk = actual_allocation * (stop_loss_pct / 100)

        logger.debug(
            f"Fixed Fractional: risk={risk_percentage:.2%}, "
            f"stop_loss={stop_loss_pct}%, shares={shares}"
        )

        return PositionSize(
            shares=shares,
            capital_allocation=actual_allocation,
            risk_amount=actual_risk,
            method='fixed_fractional',
            metadata={
                'risk_percentage': risk_percentage,
                'stop_loss_pct': stop_loss_pct,
                'price': price
            }
        )

    def risk_based(
        self,
        price: float,
        atr: float,
        atr_multiplier: float = 2.0,
        risk_percentage: Optional[float] = None
    ) -> PositionSize:
        """
        Calculate position size based on volatility (ATR).

        Stop-loss = ATR * multiplier
        Position Size = (Capital * Risk%) / Stop-loss amount

        Args:
            price: Current stock price
            atr: Average True Range (volatility measure)
            atr_multiplier: Multiplier for stop-loss distance (default: 2.0)
            risk_percentage: % of capital to risk (default: self.max_risk_per_trade)

        Returns:
            PositionSize with shares and allocation
        """
        if risk_percentage is None:
            risk_percentage = self.max_risk_per_trade

        # Calculate stop-loss distance in rupees
        stop_loss_distance = atr * atr_multiplier

        # Risk amount in rupees
        risk_amount = self.capital * risk_percentage

        # Calculate shares based on risk and stop-loss
        shares = int(risk_amount / stop_loss_distance)

        # Cap by max position size
        max_shares_by_limit = int((self.capital * self.max_position_size) / price)
        shares = min(shares, max_shares_by_limit)

        # Calculate actual values
        actual_allocation = shares * price
        actual_risk = shares * stop_loss_distance

        logger.debug(
            f"Risk-based: ATR={atr:.2f}, stop_distance={stop_loss_distance:.2f}, "
            f"shares={shares}"
        )

        return PositionSize(
            shares=shares,
            capital_allocation=actual_allocation,
            risk_amount=actual_risk,
            method='risk_based_atr',
            metadata={
                'atr': atr,
                'atr_multiplier': atr_multiplier,
                'stop_loss_distance': stop_loss_distance,
                'risk_percentage': risk_percentage,
                'price': price
            }
        )

    def equal_weight(
        self,
        price: float,
        num_positions: int
    ) -> PositionSize:
        """
        Calculate equal-weight position size.

        Divides capital equally among all positions.

        Args:
            price: Current stock price
            num_positions: Total number of positions in portfolio

        Returns:
            PositionSize with shares and allocation
        """
        # Allocation per position
        allocation_per_position = self.capital / num_positions

        # Cap at max position size
        max_allocation = self.capital * self.max_position_size
        allocation = min(allocation_per_position, max_allocation)

        # Calculate shares
        shares = int(allocation / price)
        actual_allocation = shares * price

        # Risk is unknown for equal weight (depends on stop-loss)
        risk_amount = actual_allocation * self.max_risk_per_trade

        logger.debug(
            f"Equal Weight: num_positions={num_positions}, "
            f"allocation={allocation:,.0f}, shares={shares}"
        )

        return PositionSize(
            shares=shares,
            capital_allocation=actual_allocation,
            risk_amount=risk_amount,
            method='equal_weight',
            metadata={
                'num_positions': num_positions,
                'allocation_per_position': allocation_per_position,
                'price': price
            }
        )

    def fixed_amount(
        self,
        price: float,
        amount: float
    ) -> PositionSize:
        """
        Calculate position size for fixed rupee amount.

        Args:
            price: Current stock price
            amount: Fixed amount to invest

        Returns:
            PositionSize with shares and allocation
        """
        # Cap at max position size
        max_allocation = self.capital * self.max_position_size
        allocation = min(amount, max_allocation)

        # Calculate shares
        shares = int(allocation / price)
        actual_allocation = shares * price

        # Risk is unknown (depends on stop-loss)
        risk_amount = actual_allocation * self.max_risk_per_trade

        logger.debug(
            f"Fixed Amount: amount={amount:,.0f}, shares={shares}"
        )

        return PositionSize(
            shares=shares,
            capital_allocation=actual_allocation,
            risk_amount=risk_amount,
            method='fixed_amount',
            metadata={
                'requested_amount': amount,
                'price': price
            }
        )

    def calculate(
        self,
        method: str,
        price: float,
        **kwargs
    ) -> PositionSize:
        """
        Calculate position size using specified method.

        Args:
            method: Sizing method ('kelly', 'fixed_fractional', 'risk_based',
                   'equal_weight', 'fixed_amount')
            price: Current stock price
            **kwargs: Method-specific parameters

        Returns:
            PositionSize
        """
        method_map = {
            'kelly': self.kelly_criterion,
            'kelly_criterion': self.kelly_criterion,
            'fixed_fractional': self.fixed_fractional,
            'risk_based': self.risk_based,
            'risk_based_atr': self.risk_based,
            'equal_weight': self.equal_weight,
            'fixed_amount': self.fixed_amount
        }

        if method not in method_map:
            raise ValueError(
                f"Unknown method: {method}. "
                f"Available: {list(method_map.keys())}"
            )

        return method_map[method](price=price, **kwargs)
