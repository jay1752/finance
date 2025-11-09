"""
Risk Management Module.

Calculate stop-loss, take-profit, and manage risk limits.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class StopLoss:
    """Stop-loss configuration."""
    price: float
    method: str
    metadata: Dict[str, Any]

    def __repr__(self):
        return f"StopLoss(price=₹{self.price:.2f}, method={self.method})"


@dataclass
class TakeProfit:
    """Take-profit configuration."""
    price: float
    method: str
    metadata: Dict[str, Any]

    def __repr__(self):
        return f"TakeProfit(price=₹{self.price:.2f}, method={self.method})"


class RiskManager:
    """
    Manage trading risk through stop-loss, take-profit, and position limits.

    Features:
    - Multiple stop-loss methods (fixed %, ATR-based, support/resistance)
    - Take-profit targets (fixed %, risk-reward ratio, trailing)
    - Daily loss limits
    - Portfolio-level risk controls
    """

    def __init__(
        self,
        max_daily_loss_pct: float = 0.05,
        max_portfolio_risk_pct: float = 0.10,
        max_position_risk_pct: float = 0.02
    ):
        """
        Initialize risk manager.

        Args:
            max_daily_loss_pct: Maximum daily loss as % of capital (default: 5%)
            max_portfolio_risk_pct: Maximum portfolio risk at any time (default: 10%)
            max_position_risk_pct: Maximum risk per position (default: 2%)
        """
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_portfolio_risk_pct = max_portfolio_risk_pct
        self.max_position_risk_pct = max_position_risk_pct

        logger.info(
            f"RiskManager initialized: daily_loss_limit={max_daily_loss_pct*100}%, "
            f"portfolio_risk_limit={max_portfolio_risk_pct*100}%, "
            f"position_risk_limit={max_position_risk_pct*100}%"
        )

    # ==================== STOP-LOSS METHODS ====================

    def fixed_stop_loss(
        self,
        entry_price: float,
        stop_pct: float = 5.0,
        direction: str = 'LONG'
    ) -> StopLoss:
        """
        Calculate fixed percentage stop-loss.

        Args:
            entry_price: Entry price of position
            stop_pct: Stop-loss percentage (default: 5%)
            direction: 'LONG' or 'SHORT'

        Returns:
            StopLoss configuration
        """
        if direction.upper() == 'LONG':
            stop_price = entry_price * (1 - stop_pct / 100)
        else:  # SHORT
            stop_price = entry_price * (1 + stop_pct / 100)

        logger.debug(
            f"Fixed Stop-Loss: entry={entry_price:.2f}, "
            f"stop={stop_price:.2f} ({stop_pct}%)"
        )

        return StopLoss(
            price=stop_price,
            method='fixed_percentage',
            metadata={
                'entry_price': entry_price,
                'stop_percentage': stop_pct,
                'direction': direction
            }
        )

    def atr_stop_loss(
        self,
        entry_price: float,
        atr: float,
        multiplier: float = 2.0,
        direction: str = 'LONG'
    ) -> StopLoss:
        """
        Calculate ATR-based stop-loss.

        Stop distance = ATR * multiplier

        Args:
            entry_price: Entry price of position
            atr: Average True Range (volatility measure)
            multiplier: ATR multiplier (default: 2.0)
            direction: 'LONG' or 'SHORT'

        Returns:
            StopLoss configuration
        """
        stop_distance = atr * multiplier

        if direction.upper() == 'LONG':
            stop_price = entry_price - stop_distance
        else:  # SHORT
            stop_price = entry_price + stop_distance

        logger.debug(
            f"ATR Stop-Loss: entry={entry_price:.2f}, ATR={atr:.2f}, "
            f"stop={stop_price:.2f}"
        )

        return StopLoss(
            price=stop_price,
            method='atr_based',
            metadata={
                'entry_price': entry_price,
                'atr': atr,
                'multiplier': multiplier,
                'stop_distance': stop_distance,
                'direction': direction
            }
        )

    def support_resistance_stop(
        self,
        entry_price: float,
        support_level: float,
        buffer_pct: float = 0.5,
        direction: str = 'LONG'
    ) -> StopLoss:
        """
        Calculate stop-loss based on support/resistance levels.

        Args:
            entry_price: Entry price of position
            support_level: Support level (for LONG) or resistance (for SHORT)
            buffer_pct: Buffer below support/above resistance (default: 0.5%)
            direction: 'LONG' or 'SHORT'

        Returns:
            StopLoss configuration
        """
        if direction.upper() == 'LONG':
            # Stop below support
            stop_price = support_level * (1 - buffer_pct / 100)
        else:  # SHORT
            # Stop above resistance
            stop_price = support_level * (1 + buffer_pct / 100)

        logger.debug(
            f"S/R Stop-Loss: entry={entry_price:.2f}, "
            f"level={support_level:.2f}, stop={stop_price:.2f}"
        )

        return StopLoss(
            price=stop_price,
            method='support_resistance',
            metadata={
                'entry_price': entry_price,
                'support_resistance_level': support_level,
                'buffer_percentage': buffer_pct,
                'direction': direction
            }
        )

    def trailing_stop_loss(
        self,
        entry_price: float,
        current_price: float,
        trail_pct: float = 5.0,
        direction: str = 'LONG'
    ) -> StopLoss:
        """
        Calculate trailing stop-loss.

        Moves stop-loss up (for LONG) as price increases.

        Args:
            entry_price: Entry price of position
            current_price: Current market price
            trail_pct: Trailing percentage (default: 5%)
            direction: 'LONG' or 'SHORT'

        Returns:
            StopLoss configuration
        """
        if direction.upper() == 'LONG':
            # Trail below current price
            stop_price = current_price * (1 - trail_pct / 100)
            # Never go below initial stop
            initial_stop = entry_price * (1 - trail_pct / 100)
            stop_price = max(stop_price, initial_stop)
        else:  # SHORT
            # Trail above current price
            stop_price = current_price * (1 + trail_pct / 100)
            # Never go above initial stop
            initial_stop = entry_price * (1 + trail_pct / 100)
            stop_price = min(stop_price, initial_stop)

        logger.debug(
            f"Trailing Stop: current={current_price:.2f}, "
            f"stop={stop_price:.2f}"
        )

        return StopLoss(
            price=stop_price,
            method='trailing',
            metadata={
                'entry_price': entry_price,
                'current_price': current_price,
                'trail_percentage': trail_pct,
                'direction': direction
            }
        )

    # ==================== TAKE-PROFIT METHODS ====================

    def fixed_take_profit(
        self,
        entry_price: float,
        profit_pct: float = 10.0,
        direction: str = 'LONG'
    ) -> TakeProfit:
        """
        Calculate fixed percentage take-profit.

        Args:
            entry_price: Entry price of position
            profit_pct: Take-profit percentage (default: 10%)
            direction: 'LONG' or 'SHORT'

        Returns:
            TakeProfit configuration
        """
        if direction.upper() == 'LONG':
            target_price = entry_price * (1 + profit_pct / 100)
        else:  # SHORT
            target_price = entry_price * (1 - profit_pct / 100)

        logger.debug(
            f"Fixed Take-Profit: entry={entry_price:.2f}, "
            f"target={target_price:.2f} ({profit_pct}%)"
        )

        return TakeProfit(
            price=target_price,
            method='fixed_percentage',
            metadata={
                'entry_price': entry_price,
                'profit_percentage': profit_pct,
                'direction': direction
            }
        )

    def risk_reward_take_profit(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_reward_ratio: float = 2.0,
        direction: str = 'LONG'
    ) -> TakeProfit:
        """
        Calculate take-profit based on risk-reward ratio.

        If risking ₹100, target ₹200 profit (2:1 ratio).

        Args:
            entry_price: Entry price of position
            stop_loss_price: Stop-loss price
            risk_reward_ratio: Target reward:risk ratio (default: 2.0)
            direction: 'LONG' or 'SHORT'

        Returns:
            TakeProfit configuration
        """
        # Calculate risk amount
        risk_amount = abs(entry_price - stop_loss_price)

        # Calculate reward amount
        reward_amount = risk_amount * risk_reward_ratio

        if direction.upper() == 'LONG':
            target_price = entry_price + reward_amount
        else:  # SHORT
            target_price = entry_price - reward_amount

        logger.debug(
            f"R:R Take-Profit: entry={entry_price:.2f}, "
            f"risk={risk_amount:.2f}, target={target_price:.2f} ({risk_reward_ratio}:1)"
        )

        return TakeProfit(
            price=target_price,
            method='risk_reward_ratio',
            metadata={
                'entry_price': entry_price,
                'stop_loss_price': stop_loss_price,
                'risk_amount': risk_amount,
                'reward_amount': reward_amount,
                'risk_reward_ratio': risk_reward_ratio,
                'direction': direction
            }
        )

    def multiple_targets(
        self,
        entry_price: float,
        targets: list,
        direction: str = 'LONG'
    ) -> list:
        """
        Calculate multiple take-profit targets.

        Args:
            entry_price: Entry price of position
            targets: List of profit percentages [5%, 10%, 15%]
            direction: 'LONG' or 'SHORT'

        Returns:
            List of TakeProfit configurations
        """
        take_profits = []

        for target_pct in targets:
            tp = self.fixed_take_profit(entry_price, target_pct, direction)
            take_profits.append(tp)

        logger.debug(f"Multiple targets: {len(take_profits)} levels")

        return take_profits

    # ==================== RISK CHECKS ====================

    def check_position_risk(
        self,
        capital: float,
        position_value: float,
        stop_loss_pct: float
    ) -> Tuple[bool, str]:
        """
        Check if position risk is acceptable.

        Args:
            capital: Total capital
            position_value: Value of position
            stop_loss_pct: Stop-loss percentage

        Returns:
            (is_acceptable, message)
        """
        # Calculate risk amount
        risk_amount = position_value * (stop_loss_pct / 100)
        risk_pct = (risk_amount / capital) * 100

        if risk_pct > self.max_position_risk_pct * 100:
            return False, (
                f"Position risk {risk_pct:.2f}% exceeds limit "
                f"{self.max_position_risk_pct*100}%"
            )

        return True, f"Position risk {risk_pct:.2f}% is acceptable"

    def check_daily_loss_limit(
        self,
        capital: float,
        daily_pnl: float
    ) -> Tuple[bool, str]:
        """
        Check if daily loss limit has been hit.

        Args:
            capital: Total capital
            daily_pnl: Today's P&L (negative for loss)

        Returns:
            (can_trade, message)
        """
        if daily_pnl >= 0:
            return True, "No losses today"

        loss_pct = abs(daily_pnl / capital) * 100

        if loss_pct >= self.max_daily_loss_pct * 100:
            return False, (
                f"Daily loss limit hit: {loss_pct:.2f}% "
                f"(limit: {self.max_daily_loss_pct*100}%)"
            )

        remaining = (self.max_daily_loss_pct * 100) - loss_pct
        return True, f"Daily loss: {loss_pct:.2f}%, remaining: {remaining:.2f}%"

    def check_portfolio_risk(
        self,
        capital: float,
        total_risk_amount: float
    ) -> Tuple[bool, str]:
        """
        Check if total portfolio risk is acceptable.

        Args:
            capital: Total capital
            total_risk_amount: Total amount at risk across all positions

        Returns:
            (is_acceptable, message)
        """
        risk_pct = (total_risk_amount / capital) * 100

        if risk_pct > self.max_portfolio_risk_pct * 100:
            return False, (
                f"Portfolio risk {risk_pct:.2f}% exceeds limit "
                f"{self.max_portfolio_risk_pct*100}%"
            )

        return True, f"Portfolio risk {risk_pct:.2f}% is acceptable"

    def calculate_stop_and_target(
        self,
        entry_price: float,
        method: str = 'fixed',
        direction: str = 'LONG',
        **kwargs
    ) -> Tuple[StopLoss, TakeProfit]:
        """
        Calculate both stop-loss and take-profit together.

        Args:
            entry_price: Entry price
            method: 'fixed', 'atr', 'risk_reward'
            direction: 'LONG' or 'SHORT'
            **kwargs: Method-specific parameters

        Returns:
            (StopLoss, TakeProfit)
        """
        if method == 'fixed':
            stop_pct = kwargs.get('stop_pct', 5.0)
            profit_pct = kwargs.get('profit_pct', 10.0)

            stop = self.fixed_stop_loss(entry_price, stop_pct, direction)
            target = self.fixed_take_profit(entry_price, profit_pct, direction)

        elif method == 'atr':
            atr = kwargs.get('atr')
            if atr is None:
                raise ValueError("ATR required for atr method")

            multiplier = kwargs.get('multiplier', 2.0)
            risk_reward = kwargs.get('risk_reward_ratio', 2.0)

            stop = self.atr_stop_loss(entry_price, atr, multiplier, direction)
            target = self.risk_reward_take_profit(
                entry_price, stop.price, risk_reward, direction
            )

        elif method == 'risk_reward':
            stop_pct = kwargs.get('stop_pct', 5.0)
            risk_reward = kwargs.get('risk_reward_ratio', 2.0)

            stop = self.fixed_stop_loss(entry_price, stop_pct, direction)
            target = self.risk_reward_take_profit(
                entry_price, stop.price, risk_reward, direction
            )

        else:
            raise ValueError(f"Unknown method: {method}")

        logger.info(
            f"Stop & Target: entry={entry_price:.2f}, "
            f"stop={stop.price:.2f}, target={target.price:.2f}"
        )

        return stop, target
