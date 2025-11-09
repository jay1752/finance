"""
Strategy Registry - Central registry for all trading strategies.

This registry allows dynamic loading and discovery of strategies.
"""
from typing import Dict, Type
from .base import BaseStrategy
import logging

logger = logging.getLogger(__name__)


class StrategyRegistry:
    """
    Central registry for all trading strategies.

    Strategies are registered here to make them discoverable by the UI
    and other parts of the application.
    """

    # Dictionary of registered strategies: name -> class
    _strategies: Dict[str, Type[BaseStrategy]] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy]):
        """
        Register a new strategy.

        Args:
            name: Strategy identifier (lowercase, underscores)
            strategy_class: Strategy class that extends BaseStrategy

        Raises:
            ValueError: If strategy doesn't extend BaseStrategy or name is duplicate

        Example:
            StrategyRegistry.register_strategy('sma_crossover', SMACrossover)
        """
        # Validate strategy class
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(
                f"Strategy class must extend BaseStrategy, got {strategy_class}"
            )

        # Check for duplicate
        if name in cls._strategies:
            logger.warning(f"Strategy '{name}' already registered, overwriting")

        cls._strategies[name] = strategy_class
        logger.info(f"Registered strategy: {name} -> {strategy_class.__name__}")

    @classmethod
    def get_strategy(cls, name: str, **params) -> BaseStrategy:
        """
        Get a strategy instance by name.

        Args:
            name: Strategy identifier
            **params: Parameters to pass to strategy constructor

        Returns:
            Instance of the requested strategy

        Raises:
            ValueError: If strategy not found

        Example:
            strategy = StrategyRegistry.get_strategy('sma_crossover', fast_period=10, slow_period=20)
        """
        if name not in cls._strategies:
            available = ", ".join(cls._strategies.keys())
            raise ValueError(
                f"Strategy '{name}' not found. Available strategies: {available}"
            )

        strategy_class = cls._strategies[name]
        return strategy_class(**params)

    @classmethod
    def list_strategies(cls) -> list:
        """
        List all registered strategy names.

        Returns:
            List of strategy identifiers
        """
        return list(cls._strategies.keys())

    @classmethod
    def get_strategy_info(cls, name: str) -> Dict[str, any]:
        """
        Get information about a strategy.

        Args:
            name: Strategy identifier

        Returns:
            Dictionary with strategy metadata

        Raises:
            ValueError: If strategy not found
        """
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")

        strategy_class = cls._strategies[name]
        strategy = strategy_class()  # Create instance to get defaults

        return {
            'name': name,
            'class_name': strategy_class.__name__,
            'description': strategy.get_description(),
            'default_params': strategy.get_default_params(),
        }

    @classmethod
    def get_all_strategies_info(cls) -> Dict[str, Dict]:
        """
        Get information about all registered strategies.

        Returns:
            Dictionary mapping strategy names to their info
        """
        return {
            name: cls.get_strategy_info(name)
            for name in cls._strategies.keys()
        }

    @classmethod
    def unregister_strategy(cls, name: str):
        """
        Unregister a strategy.

        Args:
            name: Strategy identifier

        Raises:
            ValueError: If strategy not found
        """
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")

        del cls._strategies[name]
        logger.info(f"Unregistered strategy: {name}")

    @classmethod
    def clear_registry(cls):
        """Clear all registered strategies (use with caution!)."""
        cls._strategies.clear()
        logger.warning("Strategy registry cleared")


# Convenience function for registration
def register_strategy(name: str):
    """
    Decorator for registering strategies.

    Usage:
        @register_strategy('my_strategy')
        class MyStrategy(BaseStrategy):
            ...
    """
    def decorator(strategy_class):
        StrategyRegistry.register_strategy(name, strategy_class)
        return strategy_class
    return decorator
