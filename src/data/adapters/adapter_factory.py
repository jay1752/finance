"""
Adapter Factory - Automatically selects the best data adapter for the requested timeframe.

This is the KEY to making the application flexible and future-proof.
"""
from typing import Optional
from .base_adapter import BaseDataAdapter
from .yahoo_adapter import YahooFinanceAdapter
from .nse_adapter import NSEAdapter
import logging

logger = logging.getLogger(__name__)


class AdapterFactory:
    """
    Factory to get the best available data adapter.

    This factory automatically selects the best data source based on:
    1. Requested timeframe
    2. Available/enabled data sources
    3. Priority order

    Phase 1: Only Yahoo Finance (free daily data)
    Phase 2: Yahoo + NSE scraping (free)
    Phase 3: Yahoo + Upstox/Zerodha (paid real-time/intraday)
    """

    # Registry of available adapters
    _adapters = {
        'yahoo': YahooFinanceAdapter,
        # Phase 2: NSE adapter for supplementary data (FII/DII, delivery %)
        'nse': NSEAdapter,
        # Phase 3: Add paid adapters
        # 'upstox': UpstoxAdapter,
        # 'zerodha': ZerodhaAdapter,
    }

    # Priority mapping: timeframe -> [preferred_sources]
    _timeframe_priority = {
        # Phase 1: Free data only
        '1d': ['yahoo'],
        '1wk': ['yahoo'],
        '1mo': ['yahoo'],

        # Phase 2: Free data + NSE
        # '1d': ['yahoo', 'nse'],

        # Phase 3: Paid intraday data
        # '1m': ['upstox', 'zerodha'],
        # '5m': ['upstox', 'zerodha'],
        # '15m': ['upstox', 'zerodha'],
        # '30m': ['upstox', 'zerodha'],
        # '1h': ['upstox', 'zerodha', 'yahoo'],
    }

    @classmethod
    def get_adapter(
        cls,
        timeframe: str = '1d',
        preferred: Optional[str] = None
    ) -> BaseDataAdapter:
        """
        Get the best adapter for the requested timeframe.

        Args:
            timeframe: Desired timeframe (1d, 1wk, 1mo, etc.)
            preferred: Preferred adapter name (optional override)

        Returns:
            Instance of data adapter

        Raises:
            ValueError: If no adapter supports the timeframe

        Examples:
            # Get adapter for daily data
            adapter = AdapterFactory.get_adapter(timeframe='1d')

            # Use specific adapter
            adapter = AdapterFactory.get_adapter(timeframe='1d', preferred='yahoo')
        """

        logger.debug(f"Getting adapter for timeframe: {timeframe}, preferred: {preferred}")

        # If preferred adapter specified, try it first
        if preferred:
            if preferred not in cls._adapters:
                logger.warning(
                    f"Preferred adapter '{preferred}' not found. "
                    f"Available: {list(cls._adapters.keys())}"
                )
            else:
                adapter_class = cls._adapters[preferred]
                adapter = adapter_class()

                # Check if it supports the timeframe
                if timeframe in adapter.get_supported_timeframes():
                    logger.info(f"Using preferred adapter: {preferred} for {timeframe}")
                    return adapter
                else:
                    logger.warning(
                        f"Preferred adapter '{preferred}' doesn't support {timeframe}. "
                        f"Trying alternatives..."
                    )

        # Use priority list for the timeframe
        if timeframe in cls._timeframe_priority:
            for adapter_name in cls._timeframe_priority[timeframe]:
                if adapter_name in cls._adapters:
                    logger.info(f"Using adapter: {adapter_name} for {timeframe}")
                    return cls._adapters[adapter_name]()

        # No specific priority - check all adapters
        for adapter_name, adapter_class in cls._adapters.items():
            adapter = adapter_class()
            if timeframe in adapter.get_supported_timeframes():
                logger.info(f"Using fallback adapter: {adapter_name} for {timeframe}")
                return adapter

        # No adapter found
        raise ValueError(
            f"No adapter found that supports timeframe '{timeframe}'. "
            f"Available timeframes: {cls.get_all_supported_timeframes()}"
        )

    @classmethod
    def get_all_supported_timeframes(cls) -> list:
        """
        Get all supported timeframes across all adapters.

        Returns:
            List of unique timeframe strings
        """
        timeframes = set()

        for adapter_class in cls._adapters.values():
            adapter = adapter_class()
            timeframes.update(adapter.get_supported_timeframes())

        return sorted(list(timeframes))

    @classmethod
    def list_adapters(cls) -> dict:
        """
        List all available adapters and their capabilities.

        Returns:
            Dictionary mapping adapter names to their supported timeframes
        """
        adapters_info = {}

        for name, adapter_class in cls._adapters.items():
            adapter = adapter_class()
            adapters_info[name] = {
                'name': adapter.name,
                'supported_timeframes': adapter.get_supported_timeframes()
            }

        return adapters_info

    @classmethod
    def register_adapter(cls, name: str, adapter_class):
        """
        Register a new adapter (for custom adapters or plugins).

        Args:
            name: Adapter identifier
            adapter_class: Class that extends BaseDataAdapter

        Raises:
            ValueError: If adapter doesn't extend BaseDataAdapter
        """
        if not issubclass(adapter_class, BaseDataAdapter):
            raise ValueError(
                f"Adapter class must extend BaseDataAdapter, got {adapter_class}"
            )

        cls._adapters[name] = adapter_class
        logger.info(f"Registered new adapter: {name}")
