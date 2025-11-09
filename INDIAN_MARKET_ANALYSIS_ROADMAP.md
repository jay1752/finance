# Indian Market Analysis Application - Complete Roadmap

**Version:** 1.0
**Last Updated:** 2025-11-09
**Project Type:** Stock Market Analysis & Trading Strategy Platform for Indian Markets

---

## Table of Contents

1. [Project Foundation](#project-foundation)
2. [Phase 1: MVP (2-3 Weeks)](#phase-1-mvp)
3. [Phase 2: Enhancement (2-3 Weeks)](#phase-2-enhancement)
4. [Phase 3: Scale (2-3 Weeks)](#phase-3-scale)
5. [Technical Specifications](#technical-specifications)
6. [Testing Strategy](#testing-strategy)
7. [Useful Additions](#useful-additions)
8. [Appendix](#appendix)

---

## Project Foundation

### Vision & Goals

**Vision:** Build a flexible, data-driven stock market analysis application specifically for Indian markets (NSE/BSE) that can analyze any stock, visualize data effectively, and support multiple trading strategies.

**Core Goals:**
- Pull all available market data and influencing factors
- Analyze any NSE/BSE stock on demand
- Present data visually with interactive charts
- Support multiple trading strategies (technical, fundamental, hybrid)
- Start with free data sources, scale to paid real-time data
- Flexible timeframe support (daily → intraday)

**Success Metrics:**
- Accurately backtest strategies with 90%+ data quality
- Support 10+ trading strategies by Phase 2
- Process NIFTY 50 stocks in < 5 seconds
- Generate actionable buy/sell signals
- Enable smooth migration from free to paid data sources

---

### Technology Stack

#### Backend
```
Language: Python 3.10+
Web Framework: FastAPI (for APIs) + Streamlit (for UI)
Data Processing: Pandas, NumPy
Technical Analysis: TA-Lib, pandas-ta
Backtesting: Backtrader, VectorBT
Task Scheduling: APScheduler
Async Processing: asyncio
```

#### Data Sources
```
Free Tier (Phase 1-2):
- Yahoo Finance (yfinance) - Historical OHLCV data
- NSE India (web scraping) - FII/DII, Delivery %, Corporate actions
- Screener.in (web scraping) - Fundamental data
- NewsAPI - News articles for sentiment
- RBI API - Macroeconomic indicators

Paid Tier (Phase 3):
- Upstox API / Zerodha Kite Connect - Real-time data
- TrueData - Tick-level data
```

#### Database
```
Primary: PostgreSQL 14+
Time-Series Extension: TimescaleDB
Cache: Redis (for Phase 3)
ORM: SQLAlchemy 2.0+
```

#### Visualization
```
Charts: Plotly, mplfinance
UI Framework: Streamlit
Dashboard: Streamlit multipage app
```

#### Testing
```
Unit Testing: pytest
Coverage: pytest-cov
Data Validation: Great Expectations
```

---

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│         PRESENTATION LAYER                  │
│         (Streamlit App)                     │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Dashboard │  │Screener  │  │Backtest  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────┐
│         APPLICATION LAYER                   │
│         (Business Logic)                    │
│                                             │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │Strategy Svc  │  │ Analysis Service │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────┐
│         DATA ADAPTER LAYER                  │
│         (Abstraction - KEY!)                │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Yahoo   │  │   NSE    │  │ Screener │ │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────┐
│         DATA STORAGE                        │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  PostgreSQL + TimescaleDB            │  │
│  │  - Stock prices (time-series)        │  │
│  │  - Fundamental data                  │  │
│  │  - Strategy results                  │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

### Project Directory Structure

```
indian-market-analysis/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config.py                     # Central configuration
├── main.py                       # Application entry point
├── ROADMAP.md                    # This document
│
├── src/
│   │
│   ├── presentation/             # UI Layer
│   │   └── streamlit_app/
│   │       ├── app.py           # Main Streamlit app
│   │       ├── pages/
│   │       │   ├── 01_dashboard.py
│   │       │   ├── 02_screener.py
│   │       │   ├── 03_backtesting.py
│   │       │   └── 04_settings.py
│   │       └── components/
│   │           ├── charts.py
│   │           ├── metrics.py
│   │           └── sidebar.py
│   │
│   ├── services/                # Business Logic
│   │   ├── data_service.py
│   │   ├── strategy_service.py
│   │   ├── analysis_service.py
│   │   └── backtest_service.py
│   │
│   ├── strategies/              # Trading Strategies
│   │   ├── base.py             # Base strategy interface
│   │   ├── registry.py         # Strategy registry
│   │   └── technical/
│   │       ├── sma_crossover.py
│   │       ├── rsi_strategy.py
│   │       ├── macd_strategy.py
│   │       ├── bollinger_bands.py
│   │       └── vwap_strategy.py
│   │
│   ├── analysis/               # Analysis Modules
│   │   ├── technical/
│   │   │   ├── indicators.py
│   │   │   ├── patterns.py
│   │   │   └── oscillators.py
│   │   ├── fundamental/
│   │   │   ├── ratios.py
│   │   │   └── valuation.py
│   │   └── sentiment/
│   │       └── basic_sentiment.py  # Basic keyword-based
│   │
│   ├── backtesting/            # Backtesting Engine
│   │   ├── engine.py
│   │   ├── metrics.py
│   │   └── portfolio.py
│   │
│   ├── data/                   # Data Layer
│   │   ├── adapters/          # Abstraction layer (KEY)
│   │   │   ├── base_adapter.py
│   │   │   ├── yahoo_adapter.py
│   │   │   ├── nse_adapter.py
│   │   │   ├── screener_adapter.py
│   │   │   └── adapter_factory.py
│   │   ├── providers/
│   │   │   └── free/
│   │   │       ├── yahoo_provider.py
│   │   │       ├── nse_scraper.py
│   │   │       └── screener_scraper.py
│   │   ├── repositories/
│   │   │   ├── stock_repository.py
│   │   │   └── strategy_repository.py
│   │   └── models/
│   │       ├── stock.py        # SQLAlchemy models
│   │       ├── strategy.py
│   │       └── signal.py
│   │
│   ├── utils/
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── constants.py
│   │
│   └── visualization/
│       ├── chart_factory.py
│       └── plotly_charts.py
│
├── tasks/                      # Background Tasks
│   ├── scheduler.py
│   └── data_updater.py
│
├── database/
│   ├── migrations/            # Alembic migrations
│   └── schema.sql
│
├── tests/
│   ├── unit/
│   │   ├── test_strategies.py
│   │   ├── test_indicators.py
│   │   └── test_adapters.py
│   ├── integration/
│   │   └── test_data_flow.py
│   └── fixtures/
│       └── sample_data.py
│
├── scripts/
│   ├── setup_db.py
│   ├── fetch_initial_data.py
│   └── run_backtest.py
│
└── docs/
    ├── api_docs.md
    └── strategy_guide.md
```

---

## Phase 1: MVP (2-3 Weeks)

**Goal:** Build a functional daily timeframe analysis tool with 3 core strategies and basic visualization.

### Scope

**In Scope:**
- ✅ 3 trading strategies (SMA Crossover, RSI, VWAP)
- ✅ Yahoo Finance data integration (daily OHLCV)
- ✅ NIFTY 50 stocks support
- ✅ Basic Streamlit UI with charts
- ✅ Simple backtesting on daily data
- ✅ SQLite/PostgreSQL storage
- ✅ Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)

**Out of Scope:**
- ❌ Intraday data
- ❌ Real-time streaming
- ❌ Complex fundamental analysis
- ❌ Options strategies
- ❌ Advanced sentiment analysis
- ❌ Multiple watchlists

---

### Module Breakdown

#### 1.1 Environment Setup

**Checklist:**
- [ ] Create virtual environment (`python -m venv venv`)
- [ ] Install core dependencies
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Initialize Git repository
- [ ] Create `.gitignore` file

**Dependencies (requirements.txt):**
```txt
# Core
python>=3.10
streamlit==1.31.0
pandas==2.1.4
numpy==1.26.3

# Data Fetching
yfinance==0.2.36
requests==2.31.0
beautifulsoup4==4.12.3

# Technical Analysis
TA-Lib==0.4.28
pandas-ta==0.3.14b

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Visualization
plotly==5.18.0
mplfinance==0.12.10b0

# Backtesting
backtrader==1.9.78.123

# Utilities
python-dotenv==1.0.1
APScheduler==3.10.4

# Testing
pytest==8.0.0
pytest-cov==4.1.0
```

**Environment Variables (.env):**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/market_analysis

# Data Sources
YAHOO_FINANCE_ENABLED=true
NSE_SCRAPING_ENABLED=false  # Phase 2

# Application
DEBUG=true
LOG_LEVEL=INFO
DATA_UPDATE_TIME=17:00  # 5 PM IST

# Phase 3 (disabled for now)
UPSTOX_API_KEY=
ZERODHA_API_KEY=
```

---

#### 1.2 Database Schema

**Tables:**

```sql
-- Stock master table
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(10),  -- NSE, BSE
    isin VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time-series price data (use TimescaleDB hypertable)
CREATE TABLE stock_prices (
    id BIGSERIAL,
    stock_id INTEGER REFERENCES stocks(id),
    date DATE NOT NULL,
    open DECIMAL(12, 2),
    high DECIMAL(12, 2),
    low DECIMAL(12, 2),
    close DECIMAL(12, 2),
    volume BIGINT,
    adj_close DECIMAL(12, 2),
    PRIMARY KEY (stock_id, date)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('stock_prices', 'date');

-- Strategy signals
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    strategy_name VARCHAR(100),
    signal_type VARCHAR(20),  -- BUY, SELL, HOLD
    signal_date DATE,
    price DECIMAL(12, 2),
    metadata JSONB,  -- Store strategy-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backtest results
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100),
    stock_id INTEGER REFERENCES stocks(id),
    start_date DATE,
    end_date DATE,
    total_return DECIMAL(10, 2),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 2),
    win_rate DECIMAL(5, 2),
    total_trades INTEGER,
    avg_profit DECIMAL(10, 2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_stock_prices_date ON stock_prices(date DESC);
CREATE INDEX idx_signals_date ON signals(signal_date DESC);
CREATE INDEX idx_signals_stock ON signals(stock_id, signal_date);
```

**Checklist:**
- [ ] Create database schema
- [ ] Set up TimescaleDB extension
- [ ] Create indexes
- [ ] Set up Alembic for migrations
- [ ] Seed NIFTY 50 stocks data

---

#### 1.3 Data Adapter Layer (CRITICAL)

This is the **most important** architectural piece - it allows swapping data sources without changing strategies.

**Base Adapter Interface:**

```python
# src/data/adapters/base_adapter.py

from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from datetime import datetime

class BaseDataAdapter(ABC):
    """
    Base interface for all data adapters.
    All adapters MUST return data in this standard format.
    """

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.

        Returns DataFrame with columns:
        - timestamp (datetime index)
        - open (float)
        - high (float)
        - low (float)
        - close (float)
        - volume (int)
        - source (str) - adapter name
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol."""
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol is valid."""
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """Return list of supported timeframes."""
        pass

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format (override if needed)."""
        return symbol.upper().strip()
```

**Yahoo Finance Adapter:**

```python
# src/data/adapters/yahoo_adapter.py

import yfinance as yf
from .base_adapter import BaseDataAdapter
from datetime import datetime
import pandas as pd

class YahooFinanceAdapter(BaseDataAdapter):
    """Yahoo Finance data adapter - FREE daily data."""

    def __init__(self):
        self.name = "yahoo_finance"
        self.supported_timeframes = ['1d', '1wk', '1mo']

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """Fetch data from Yahoo Finance."""

        # Add .NS suffix for NSE stocks
        yahoo_symbol = self._format_symbol(symbol)

        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=timeframe
        )

        # Normalize column names
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # Add metadata
        df['source'] = self.name
        df['timeframe'] = timeframe

        return df[['open', 'high', 'low', 'close', 'volume', 'source', 'timeframe']]

    def get_current_price(self, symbol: str) -> float:
        """Get latest price."""
        yahoo_symbol = self._format_symbol(symbol)
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period='1d')
        return data['Close'].iloc[-1] if not data.empty else None

    def validate_symbol(self, symbol: str) -> bool:
        """Validate symbol exists."""
        try:
            yahoo_symbol = self._format_symbol(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period='1d')
            return not data.empty
        except:
            return False

    def get_supported_timeframes(self) -> list:
        return self.supported_timeframes

    def _format_symbol(self, symbol: str) -> str:
        """Convert to Yahoo Finance format (add .NS for NSE)."""
        symbol = self.normalize_symbol(symbol)
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            return f"{symbol}.NS"  # Default to NSE
        return symbol
```

**Adapter Factory:**

```python
# src/data/adapters/adapter_factory.py

from typing import Optional
from .base_adapter import BaseDataAdapter
from .yahoo_adapter import YahooFinanceAdapter
# from .nse_adapter import NSEAdapter  # Phase 2
# from .upstox_adapter import UpstoxAdapter  # Phase 3

class AdapterFactory:
    """Factory to get the best available data adapter."""

    _adapters = {
        'yahoo': YahooFinanceAdapter,
        # 'nse': NSEAdapter,  # Phase 2
        # 'upstox': UpstoxAdapter,  # Phase 3
    }

    _timeframe_priority = {
        '1d': ['yahoo', 'nse'],
        '1wk': ['yahoo'],
        '1mo': ['yahoo'],
        # Phase 3:
        # '1m': ['upstox', 'zerodha'],
        # '5m': ['upstox', 'zerodha'],
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
            timeframe: Desired timeframe
            preferred: Preferred adapter name (optional)

        Returns:
            Instance of data adapter
        """

        # If preferred adapter specified, try it first
        if preferred and preferred in cls._adapters:
            adapter_class = cls._adapters[preferred]
            adapter = adapter_class()
            if timeframe in adapter.get_supported_timeframes():
                return adapter

        # Otherwise, use priority list
        if timeframe in cls._timeframe_priority:
            for adapter_name in cls._timeframe_priority[timeframe]:
                if adapter_name in cls._adapters:
                    return cls._adapters[adapter_name]()

        # Default to Yahoo Finance
        return YahooFinanceAdapter()
```

**Checklist:**
- [ ] Implement BaseDataAdapter interface
- [ ] Implement YahooFinanceAdapter
- [ ] Implement AdapterFactory
- [ ] Write unit tests for adapters
- [ ] Test with sample NSE stocks

---

#### 1.4 Core Strategies (3 Strategies)

**Base Strategy Class:**

```python
# src/strategies/base.py

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class Signal:
    """Trading signal."""
    date: str
    signal_type: str  # BUY, SELL, HOLD
    price: float
    confidence: float  # 0-100
    metadata: Dict[str, Any]

class BaseStrategy(ABC):
    """Base class for all trading strategies."""

    def __init__(self, **params):
        self.name = self.__class__.__name__
        self.params = params
        self.signals: List[Signal] = []

    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Analyze data and generate signals.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        pass

    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Return default parameters for the strategy."""
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data has required columns."""
        required = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required)

    def get_signals(self) -> List[Signal]:
        """Return generated signals."""
        return self.signals

    def get_latest_signal(self) -> Signal:
        """Return most recent signal."""
        return self.signals[-1] if self.signals else None
```

**Strategy 1: SMA Crossover**

```python
# src/strategies/technical/sma_crossover.py

import pandas as pd
from ..base import BaseStrategy, Signal

class SMACrossover(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.

    BUY: When fast SMA crosses above slow SMA
    SELL: When fast SMA crosses below slow SMA
    """

    def get_default_params(self):
        return {
            'fast_period': 20,
            'slow_period': 50
        }

    def analyze(self, data: pd.DataFrame) -> list:
        """Generate signals based on SMA crossover."""

        if not self.validate_data(data):
            raise ValueError("Invalid data format")

        # Get parameters
        fast = self.params.get('fast_period', 20)
        slow = self.params.get('slow_period', 50)

        # Calculate SMAs
        data['sma_fast'] = data['close'].rolling(window=fast).mean()
        data['sma_slow'] = data['close'].rolling(window=slow).mean()

        # Generate signals
        signals = []

        for i in range(1, len(data)):
            prev_fast = data['sma_fast'].iloc[i-1]
            prev_slow = data['sma_slow'].iloc[i-1]
            curr_fast = data['sma_fast'].iloc[i]
            curr_slow = data['sma_slow'].iloc[i]

            signal_type = 'HOLD'

            # Bullish crossover
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                signal_type = 'BUY'

            # Bearish crossover
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                signal_type = 'SELL'

            if signal_type != 'HOLD':
                signal = Signal(
                    date=str(data.index[i].date()),
                    signal_type=signal_type,
                    price=data['close'].iloc[i],
                    confidence=self._calculate_confidence(data, i),
                    metadata={
                        'sma_fast': curr_fast,
                        'sma_slow': curr_slow,
                        'fast_period': fast,
                        'slow_period': slow
                    }
                )
                signals.append(signal)

        self.signals = signals
        return signals

    def _calculate_confidence(self, data: pd.DataFrame, idx: int) -> float:
        """Calculate signal confidence based on gap between SMAs."""
        fast = data['sma_fast'].iloc[idx]
        slow = data['sma_slow'].iloc[idx]
        price = data['close'].iloc[idx]

        # Larger gap = higher confidence
        gap_pct = abs((fast - slow) / price) * 100
        confidence = min(gap_pct * 20, 100)  # Scale to 0-100

        return round(confidence, 2)
```

**Strategy 2: RSI Strategy**

```python
# src/strategies/technical/rsi_strategy.py

import pandas as pd
from ..base import BaseStrategy, Signal

class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Mean Reversion Strategy.

    BUY: When RSI crosses above oversold level (default: 30)
    SELL: When RSI crosses below overbought level (default: 70)
    """

    def get_default_params(self):
        return {
            'period': 14,
            'oversold': 30,
            'overbought': 70
        }

    def analyze(self, data: pd.DataFrame) -> list:
        """Generate signals based on RSI levels."""

        if not self.validate_data(data):
            raise ValueError("Invalid data format")

        # Get parameters
        period = self.params.get('period', 14)
        oversold = self.params.get('oversold', 30)
        overbought = self.params.get('overbought', 70)

        # Calculate RSI
        data['rsi'] = self._calculate_rsi(data['close'], period)

        # Generate signals
        signals = []

        for i in range(1, len(data)):
            prev_rsi = data['rsi'].iloc[i-1]
            curr_rsi = data['rsi'].iloc[i]

            signal_type = 'HOLD'

            # Oversold → BUY
            if prev_rsi <= oversold and curr_rsi > oversold:
                signal_type = 'BUY'

            # Overbought → SELL
            elif prev_rsi >= overbought and curr_rsi < overbought:
                signal_type = 'SELL'

            if signal_type != 'HOLD':
                signal = Signal(
                    date=str(data.index[i].date()),
                    signal_type=signal_type,
                    price=data['close'].iloc[i],
                    confidence=self._calculate_confidence(curr_rsi, signal_type, oversold, overbought),
                    metadata={
                        'rsi': curr_rsi,
                        'period': period,
                        'oversold': oversold,
                        'overbought': overbought
                    }
                )
                signals.append(signal)

        self.signals = signals
        return signals

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_confidence(self, rsi: float, signal_type: str, oversold: float, overbought: float) -> float:
        """Calculate signal confidence."""
        if signal_type == 'BUY':
            # Closer to 0 = higher confidence
            confidence = (oversold - rsi) / oversold * 100
        else:  # SELL
            # Closer to 100 = higher confidence
            confidence = (rsi - overbought) / (100 - overbought) * 100

        return round(max(0, min(100, confidence)), 2)
```

**Strategy 3: VWAP Strategy**

```python
# src/strategies/technical/vwap_strategy.py

import pandas as pd
from ..base import BaseStrategy, Signal

class VWAPStrategy(BaseStrategy):
    """
    VWAP (Volume Weighted Average Price) Strategy.

    BUY: When price crosses above VWAP
    SELL: When price crosses below VWAP
    """

    def get_default_params(self):
        return {
            'period': 20,  # Rolling VWAP period
            'threshold': 0.5  # Min % difference for signal
        }

    def analyze(self, data: pd.DataFrame) -> list:
        """Generate signals based on VWAP crossover."""

        if not self.validate_data(data):
            raise ValueError("Invalid data format")

        # Get parameters
        period = self.params.get('period', 20)
        threshold = self.params.get('threshold', 0.5)

        # Calculate VWAP
        data['vwap'] = self._calculate_vwap(data, period)
        data['price_vs_vwap'] = ((data['close'] - data['vwap']) / data['vwap']) * 100

        # Generate signals
        signals = []

        for i in range(1, len(data)):
            prev_close = data['close'].iloc[i-1]
            curr_close = data['close'].iloc[i]
            prev_vwap = data['vwap'].iloc[i-1]
            curr_vwap = data['vwap'].iloc[i]

            signal_type = 'HOLD'

            # Price crosses above VWAP
            if prev_close <= prev_vwap and curr_close > curr_vwap:
                if abs(data['price_vs_vwap'].iloc[i]) >= threshold:
                    signal_type = 'BUY'

            # Price crosses below VWAP
            elif prev_close >= prev_vwap and curr_close < curr_vwap:
                if abs(data['price_vs_vwap'].iloc[i]) >= threshold:
                    signal_type = 'SELL'

            if signal_type != 'HOLD':
                signal = Signal(
                    date=str(data.index[i].date()),
                    signal_type=signal_type,
                    price=data['close'].iloc[i],
                    confidence=min(abs(data['price_vs_vwap'].iloc[i]) * 10, 100),
                    metadata={
                        'vwap': curr_vwap,
                        'price_vs_vwap_pct': data['price_vs_vwap'].iloc[i],
                        'volume': data['volume'].iloc[i]
                    }
                )
                signals.append(signal)

        self.signals = signals
        return signals

    def _calculate_vwap(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate rolling VWAP."""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = (typical_price * data['volume']).rolling(window=period).sum() / \
               data['volume'].rolling(window=period).sum()
        return vwap
```

**Strategy Registry:**

```python
# src/strategies/registry.py

from .technical.sma_crossover import SMACrossover
from .technical.rsi_strategy import RSIStrategy
from .technical.vwap_strategy import VWAPStrategy

class StrategyRegistry:
    """Central registry for all strategies."""

    _strategies = {
        'sma_crossover': SMACrossover,
        'rsi': RSIStrategy,
        'vwap': VWAPStrategy,
    }

    @classmethod
    def get_strategy(cls, name: str, **params):
        """Get strategy instance by name."""
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")

        strategy_class = cls._strategies[name]
        return strategy_class(**params)

    @classmethod
    def list_strategies(cls):
        """List all available strategies."""
        return list(cls._strategies.keys())

    @classmethod
    def register_strategy(cls, name: str, strategy_class):
        """Register a new strategy."""
        cls._strategies[name] = strategy_class
```

**Checklist:**
- [ ] Implement BaseStrategy class
- [ ] Implement SMACrossover strategy
- [ ] Implement RSIStrategy
- [ ] Implement VWAPStrategy
- [ ] Implement StrategyRegistry
- [ ] Write unit tests for each strategy
- [ ] Test with historical NIFTY 50 data

---

#### 1.5 Basic Streamlit UI

**Main App:**

```python
# src/presentation/streamlit_app/app.py

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(
    page_title="Indian Market Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page
st.title("📈 Indian Stock Market Analysis")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    st.markdown("""
    - 📊 Dashboard - Analyze stocks
    - 🔍 Screener - Find opportunities
    - 📉 Backtesting - Test strategies
    - ⚙️ Settings - Configuration
    """)

    st.markdown("---")
    st.info("💡 **Phase 1 MVP**\n\nDaily timeframe analysis with 3 core strategies.")

# Home page content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Strategies Available", "3")
    st.caption("SMA, RSI, VWAP")

with col2:
    st.metric("Stocks Supported", "50+")
    st.caption("NIFTY 50")

with col3:
    st.metric("Data Source", "Free")
    st.caption("Yahoo Finance")

st.markdown("---")

st.subheader("Quick Start")
st.markdown("""
1. Go to **Dashboard** to analyze a specific stock
2. Use **Screener** to find stocks matching criteria
3. Run **Backtesting** to validate strategies
""")
```

**Dashboard Page:**

```python
# src/presentation/streamlit_app/pages/01_dashboard.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.adapters.adapter_factory import AdapterFactory
from src.strategies.registry import StrategyRegistry

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Stock Analysis Dashboard")

# Sidebar controls
with st.sidebar:
    st.header("Configuration")

    # Stock selection
    symbol = st.text_input("Stock Symbol", "RELIANCE", help="Enter NSE symbol (e.g., RELIANCE, TCS, INFY)")

    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    date_range = st.date_input(
        "Date Range",
        value=(start_date, end_date),
        max_value=end_date
    )

    # Strategy selection
    strategies = StrategyRegistry.list_strategies()
    selected_strategy = st.selectbox("Strategy", strategies)

    # Strategy parameters (simplified for MVP)
    st.subheader("Parameters")
    if selected_strategy == 'sma_crossover':
        fast_period = st.slider("Fast SMA", 5, 50, 20)
        slow_period = st.slider("Slow SMA", 20, 200, 50)
        params = {'fast_period': fast_period, 'slow_period': slow_period}
    elif selected_strategy == 'rsi':
        period = st.slider("RSI Period", 5, 30, 14)
        oversold = st.slider("Oversold", 20, 40, 30)
        overbought = st.slider("Overbought", 60, 80, 70)
        params = {'period': period, 'oversold': oversold, 'overbought': overbought}
    elif selected_strategy == 'vwap':
        period = st.slider("VWAP Period", 10, 50, 20)
        params = {'period': period}

    analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

# Main content
if analyze_button:
    with st.spinner(f"Fetching data for {symbol}..."):
        try:
            # Fetch data using adapter
            adapter = AdapterFactory.get_adapter(timeframe='1d')
            data = adapter.get_historical_data(
                symbol=symbol,
                start_date=date_range[0],
                end_date=date_range[1],
                timeframe='1d'
            )

            if data.empty:
                st.error("No data found for this symbol.")
                st.stop()

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)

            latest_price = data['close'].iloc[-1]
            prev_price = data['close'].iloc[-2]
            change = latest_price - prev_price
            change_pct = (change / prev_price) * 100

            with col1:
                st.metric("Latest Price", f"₹{latest_price:.2f}", f"{change_pct:.2f}%")
            with col2:
                st.metric("High (1Y)", f"₹{data['high'].max():.2f}")
            with col3:
                st.metric("Low (1Y)", f"₹{data['low'].min():.2f}")
            with col4:
                st.metric("Avg Volume", f"{data['volume'].mean()/1000000:.2f}M")

            # Run strategy analysis
            st.markdown("---")
            st.subheader(f"Strategy: {selected_strategy.upper()}")

            strategy = StrategyRegistry.get_strategy(selected_strategy, **params)
            signals = strategy.analyze(data.copy())

            # Display signals
            col1, col2 = st.columns([2, 1])

            with col1:
                # Create candlestick chart
                fig = go.Figure()

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name='Price'
                ))

                # Add buy/sell signals
                buy_signals = [s for s in signals if s.signal_type == 'BUY']
                sell_signals = [s for s in signals if s.signal_type == 'SELL']

                if buy_signals:
                    fig.add_trace(go.Scatter(
                        x=[s.date for s in buy_signals],
                        y=[s.price for s in buy_signals],
                        mode='markers',
                        marker=dict(symbol='triangle-up', size=15, color='green'),
                        name='Buy Signal'
                    ))

                if sell_signals:
                    fig.add_trace(go.Scatter(
                        x=[s.date for s in sell_signals],
                        y=[s.price for s in sell_signals],
                        mode='markers',
                        marker=dict(symbol='triangle-down', size=15, color='red'),
                        name='Sell Signal'
                    ))

                fig.update_layout(
                    title=f"{symbol} Price Chart with Signals",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    height=600,
                    xaxis_rangeslider_visible=False
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Recent Signals")

                if signals:
                    # Show last 5 signals
                    recent_signals = signals[-5:]

                    for signal in reversed(recent_signals):
                        if signal.signal_type == 'BUY':
                            st.success(f"🟢 **BUY** - {signal.date}")
                        else:
                            st.error(f"🔴 **SELL** - {signal.date}")

                        st.caption(f"Price: ₹{signal.price:.2f} | Confidence: {signal.confidence}%")
                        st.markdown("---")
                else:
                    st.info("No signals generated in this period.")

                # Latest signal
                latest_signal = strategy.get_latest_signal()
                if latest_signal:
                    st.subheader("Latest Signal")
                    if latest_signal.signal_type == 'BUY':
                        st.success(f"🟢 **{latest_signal.signal_type}**")
                    else:
                        st.error(f"🔴 **{latest_signal.signal_type}**")

                    st.write(f"Date: {latest_signal.date}")
                    st.write(f"Price: ₹{latest_signal.price:.2f}")
                    st.write(f"Confidence: {latest_signal.confidence}%")

            # Signals table
            if signals:
                st.markdown("---")
                st.subheader("All Signals")

                signals_df = pd.DataFrame([
                    {
                        'Date': s.date,
                        'Signal': s.signal_type,
                        'Price': f"₹{s.price:.2f}",
                        'Confidence': f"{s.confidence}%"
                    }
                    for s in signals
                ])

                st.dataframe(signals_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)
else:
    st.info("👈 Configure parameters in the sidebar and click 'Analyze' to get started.")
```

**Checklist:**
- [ ] Create main Streamlit app
- [ ] Implement Dashboard page
- [ ] Add stock symbol input
- [ ] Add date range selector
- [ ] Add strategy selector with parameters
- [ ] Create candlestick chart with Plotly
- [ ] Display buy/sell signals on chart
- [ ] Add metrics display
- [ ] Test with multiple stocks

---

#### 1.6 Simple Backtesting

**Backtesting Engine:**

```python
# src/backtesting/engine.py

import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass
from src.strategies.base import BaseStrategy, Signal

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

class BacktestEngine:
    """Simple backtesting engine for strategy validation."""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None
        self.trades: List[Trade] = []

    def run(
        self,
        data: pd.DataFrame,
        strategy: BaseStrategy
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data.

        Args:
            data: Historical OHLCV data
            strategy: Strategy instance

        Returns:
            Dict with backtest results
        """

        # Generate signals
        signals = strategy.analyze(data)

        # Execute trades based on signals
        for signal in signals:
            self._execute_signal(signal, data)

        # Close any open position
        if self.position:
            last_price = data['close'].iloc[-1]
            self._close_position(str(data.index[-1].date()), last_price)

        # Calculate metrics
        results = self._calculate_metrics()

        return results

    def _execute_signal(self, signal: Signal, data: pd.DataFrame):
        """Execute trade based on signal."""

        if signal.signal_type == 'BUY' and self.position is None:
            # Open long position
            quantity = int(self.capital / signal.price)
            self.position = {
                'type': 'LONG',
                'entry_date': signal.date,
                'entry_price': signal.price,
                'quantity': quantity
            }
            self.capital -= quantity * signal.price

        elif signal.signal_type == 'SELL' and self.position and self.position['type'] == 'LONG':
            # Close long position
            self._close_position(signal.date, signal.price)

    def _close_position(self, exit_date: str, exit_price: float):
        """Close current position and record trade."""

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

        # Clear position
        self.position = None

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate backtest performance metrics."""

        if not self.trades:
            return {
                'total_trades': 0,
                'total_return': 0,
                'total_return_pct': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'max_profit': 0,
                'max_loss': 0,
                'final_capital': self.capital
            }

        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.profit_loss > 0]
        losing_trades = [t for t in self.trades if t.profit_loss <= 0]

        total_return = self.capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0

        avg_profit = sum(t.profit_loss for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.profit_loss for t in losing_trades) / len(losing_trades) if losing_trades else 0

        max_profit = max((t.profit_loss for t in self.trades), default=0)
        max_loss = min((t.profit_loss for t in self.trades), default=0)

        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_return': round(total_return, 2),
            'total_return_pct': round(total_return_pct, 2),
            'win_rate': round(win_rate, 2),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'max_profit': round(max_profit, 2),
            'max_loss': round(max_loss, 2),
            'final_capital': round(self.capital, 2),
            'trades': self.trades
        }
```

**Backtesting Page:**

```python
# src/presentation/streamlit_app/pages/03_backtesting.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.adapters.adapter_factory import AdapterFactory
from src.strategies.registry import StrategyRegistry
from src.backtesting.engine import BacktestEngine

st.set_page_config(page_title="Backtesting", page_icon="📉", layout="wide")

st.title("📉 Strategy Backtesting")

# Sidebar
with st.sidebar:
    st.header("Backtest Configuration")

    symbol = st.text_input("Stock Symbol", "RELIANCE")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years

    date_range = st.date_input(
        "Date Range",
        value=(start_date, end_date),
        max_value=end_date
    )

    initial_capital = st.number_input("Initial Capital (₹)", value=100000, step=10000)

    strategies = StrategyRegistry.list_strategies()
    selected_strategy = st.selectbox("Strategy", strategies)

    run_button = st.button("🚀 Run Backtest", type="primary", use_container_width=True)

# Main content
if run_button:
    with st.spinner("Running backtest..."):
        try:
            # Fetch data
            adapter = AdapterFactory.get_adapter(timeframe='1d')
            data = adapter.get_historical_data(
                symbol=symbol,
                start_date=date_range[0],
                end_date=date_range[1],
                timeframe='1d'
            )

            # Run strategy
            strategy = StrategyRegistry.get_strategy(selected_strategy)

            # Run backtest
            engine = BacktestEngine(initial_capital=initial_capital)
            results = engine.run(data, strategy)

            # Display results
            st.success("✅ Backtest completed!")

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Return",
                    f"₹{results['total_return']:,.2f}",
                    f"{results['total_return_pct']:.2f}%"
                )

            with col2:
                st.metric("Win Rate", f"{results['win_rate']:.2f}%")

            with col3:
                st.metric("Total Trades", results['total_trades'])

            with col4:
                st.metric("Final Capital", f"₹{results['final_capital']:,.2f}")

            # Detailed metrics
            st.markdown("---")
            st.subheader("Performance Details")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Winning Trades:**", results['winning_trades'])
                st.write("**Average Profit:**", f"₹{results['avg_profit']:,.2f}")
                st.write("**Max Profit:**", f"₹{results['max_profit']:,.2f}")

            with col2:
                st.write("**Losing Trades:**", results['losing_trades'])
                st.write("**Average Loss:**", f"₹{results['avg_loss']:,.2f}")
                st.write("**Max Loss:**", f"₹{results['max_loss']:,.2f}")

            # Trade history
            if results['trades']:
                st.markdown("---")
                st.subheader("Trade History")

                trades_df = pd.DataFrame([
                    {
                        'Entry Date': t.entry_date,
                        'Exit Date': t.exit_date,
                        'Entry Price': f"₹{t.entry_price:.2f}",
                        'Exit Price': f"₹{t.exit_price:.2f}",
                        'Quantity': t.quantity,
                        'P&L': f"₹{t.profit_loss:.2f}",
                        'P&L %': f"{t.profit_loss_pct:.2f}%"
                    }
                    for t in results['trades']
                ])

                st.dataframe(trades_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)
else:
    st.info("👈 Configure backtest parameters and click 'Run Backtest'")
```

**Checklist:**
- [ ] Implement BacktestEngine class
- [ ] Implement Trade tracking
- [ ] Calculate performance metrics
- [ ] Create Backtesting Streamlit page
- [ ] Add trade history display
- [ ] Test with multiple strategies
- [ ] Validate results accuracy

---

### Phase 1 Complete Checklist

**Environment & Setup:**
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] PostgreSQL database configured
- [ ] Environment variables set
- [ ] Git repository initialized

**Database:**
- [ ] Schema created
- [ ] TimescaleDB extension enabled
- [ ] NIFTY 50 stocks seeded
- [ ] Indexes created
- [ ] Alembic migrations set up

**Data Layer:**
- [ ] BaseDataAdapter implemented
- [ ] YahooFinanceAdapter implemented
- [ ] AdapterFactory implemented
- [ ] Unit tests passing

**Strategies:**
- [ ] BaseStrategy class implemented
- [ ] SMACrossover strategy implemented
- [ ] RSIStrategy implemented
- [ ] VWAPStrategy implemented
- [ ] StrategyRegistry implemented
- [ ] Unit tests passing

**Backtesting:**
- [ ] BacktestEngine implemented
- [ ] Trade execution logic working
- [ ] Performance metrics calculated
- [ ] Unit tests passing

**UI:**
- [ ] Main Streamlit app created
- [ ] Dashboard page functional
- [ ] Backtesting page functional
- [ ] Charts displaying correctly
- [ ] Signals displaying correctly

**Testing:**
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Tested with 5+ stocks
- [ ] Tested all 3 strategies

---

## Phase 2: Enhancement (2-3 Weeks)

**Goal:** Add Indian market-specific data (FII/DII, delivery %), more strategies, fundamental analysis, and stock screener.

### Scope

**In Scope:**
- ✅ NSE India scraping (FII/DII, Delivery %, Bhavcopy)
- ✅ 5-7 additional strategies
- ✅ Basic fundamental analysis (PE, PB, Debt/Equity ratios)
- ✅ Stock screener with 10-15 criteria
- ✅ Basic sentiment analysis (keyword-based)
- ✅ Alert system (EOD alerts)
- ✅ Weekly/Monthly timeframe support

**Out of Scope:**
- ❌ Intraday data
- ❌ Real-time alerts
- ❌ Complex NLP sentiment
- ❌ Options chain data

---

### Module Breakdown

#### 2.1 NSE India Scraper (CRITICAL for Indian Markets)

**NSE Data Provider:**

```python
# src/data/providers/free/nse_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

class NSEScraper:
    """
    Scraper for NSE India website.

    Fetches:
    - FII/DII data (Foreign/Domestic Institutional Investment)
    - Delivery percentage
    - Bhavcopy (daily summary)
    - Corporate actions
    """

    BASE_URL = "https://www.nseindia.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        # Initialize session with homepage visit
        self._init_session()

    def _init_session(self):
        """Initialize session by visiting homepage (sets cookies)."""
        try:
            self.session.get(self.BASE_URL, timeout=10)
            time.sleep(1)
        except:
            pass

    def get_fii_dii_data(self, date: datetime = None) -> dict:
        """
        Fetch FII/DII data for a given date.

        Returns:
            {
                'date': date,
                'fii_gross_purchase': float,
                'fii_gross_sale': float,
                'fii_net': float,
                'dii_gross_purchase': float,
                'dii_gross_sale': float,
                'dii_net': float
            }
        """
        url = f"{self.BASE_URL}/api/fiidiiTradeReact"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse latest data
            if data and len(data) > 0:
                latest = data[0]
                return {
                    'date': latest.get('date'),
                    'fii_gross_purchase': float(latest.get('fiiGrossPurchase', 0)),
                    'fii_gross_sale': float(latest.get('fiiGrossSale', 0)),
                    'fii_net': float(latest.get('fiiNet', 0)),
                    'dii_gross_purchase': float(latest.get('diiGrossPurchase', 0)),
                    'dii_gross_sale': float(latest.get('diiGrossSale', 0)),
                    'dii_net': float(latest.get('diiNet', 0))
                }
        except Exception as e:
            print(f"Error fetching FII/DII data: {e}")
            return None

    def get_delivery_percentage(self, symbol: str) -> float:
        """
        Get delivery percentage for a stock.

        Higher delivery % indicates genuine buying interest.
        """
        url = f"{self.BASE_URL}/api/quote-equity?symbol={symbol}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'securityWiseDP' in data:
                delivery_data = data['securityWiseDP']
                delivery_pct = delivery_data.get('deliveryToTradedQuantity', 0)
                return float(delivery_pct)
        except Exception as e:
            print(f"Error fetching delivery data for {symbol}: {e}")
            return None

    def get_market_status(self) -> dict:
        """Get current market status."""
        url = f"{self.BASE_URL}/api/marketStatus"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market status: {e}")
            return None
```

**NSE Adapter:**

```python
# src/data/adapters/nse_adapter.py

from .base_adapter import BaseDataAdapter
from ..providers.free.nse_scraper import NSEScraper
import pandas as pd
from datetime import datetime

class NSEAdapter(BaseDataAdapter):
    """NSE India data adapter for Indian market-specific data."""

    def __init__(self):
        self.name = "nse_india"
        self.scraper = NSEScraper()
        self.supported_timeframes = ['1d']

    def get_historical_data(self, symbol, start_date, end_date, timeframe='1d'):
        """
        Note: NSE doesn't provide easy historical access.
        Use this primarily for supplementary data (FII/DII, delivery %).
        """
        raise NotImplementedError("Use Yahoo Finance for historical price data")

    def get_current_price(self, symbol: str) -> float:
        """Get current price from NSE."""
        # Implementation would fetch from NSE quote API
        pass

    def get_fii_dii_data(self) -> dict:
        """Get latest FII/DII data."""
        return self.scraper.get_fii_dii_data()

    def get_delivery_percentage(self, symbol: str) -> float:
        """Get delivery percentage for stock."""
        return self.scraper.get_delivery_percentage(symbol)

    def validate_symbol(self, symbol: str) -> bool:
        """Validate NSE symbol."""
        # Implementation
        pass

    def get_supported_timeframes(self) -> list:
        return self.supported_timeframes
```

**Database Schema Addition:**

```sql
-- FII/DII tracking
CREATE TABLE fii_dii_data (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    fii_gross_purchase DECIMAL(15, 2),
    fii_gross_sale DECIMAL(15, 2),
    fii_net DECIMAL(15, 2),
    dii_gross_purchase DECIMAL(15, 2),
    dii_gross_sale DECIMAL(15, 2),
    dii_net DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery percentage tracking
CREATE TABLE delivery_data (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    date DATE NOT NULL,
    delivery_quantity BIGINT,
    traded_quantity BIGINT,
    delivery_percentage DECIMAL(5, 2),
    UNIQUE(stock_id, date)
);

CREATE INDEX idx_delivery_date ON delivery_data(date DESC);
```

**Checklist:**
- [ ] Implement NSEScraper class
- [ ] Implement FII/DII data fetching
- [ ] Implement delivery percentage fetching
- [ ] Create NSEAdapter
- [ ] Add database schema for FII/DII
- [ ] Add database schema for delivery data
- [ ] Create scheduled task to fetch daily
- [ ] Test scraping with rate limiting

---

#### 2.2 Additional Strategies (5 More)

**Strategy 4: MACD Strategy**
**Strategy 5: Bollinger Bands**
**Strategy 6: Moving Average Ribbon**
**Strategy 7: Breakout Strategy**
**Strategy 8: Volume Spike Strategy**

(Full code templates available in appendix)

**Checklist:**
- [ ] Implement MACD strategy
- [ ] Implement Bollinger Bands strategy
- [ ] Implement MA Ribbon strategy
- [ ] Implement Breakout strategy
- [ ] Implement Volume Spike strategy
- [ ] Add to StrategyRegistry
- [ ] Write unit tests for each
- [ ] Backtest each strategy

---

#### 2.3 Fundamental Analysis

**Financial Ratios Module:**

```python
# src/analysis/fundamental/ratios.py

import pandas as pd

class FundamentalRatios:
    """Calculate fundamental financial ratios."""

    @staticmethod
    def calculate_pe_ratio(price: float, eps: float) -> float:
        """Price to Earnings ratio."""
        if eps <= 0:
            return None
        return round(price / eps, 2)

    @staticmethod
    def calculate_pb_ratio(price: float, book_value_per_share: float) -> float:
        """Price to Book ratio."""
        if book_value_per_share <= 0:
            return None
        return round(price / book_value_per_share, 2)

    @staticmethod
    def calculate_debt_to_equity(total_debt: float, total_equity: float) -> float:
        """Debt to Equity ratio."""
        if total_equity <= 0:
            return None
        return round(total_debt / total_equity, 2)

    @staticmethod
    def calculate_roe(net_income: float, shareholder_equity: float) -> float:
        """Return on Equity (%)."""
        if shareholder_equity <= 0:
            return None
        return round((net_income / shareholder_equity) * 100, 2)

    @staticmethod
    def calculate_roa(net_income: float, total_assets: float) -> float:
        """Return on Assets (%)."""
        if total_assets <= 0:
            return None
        return round((net_income / total_assets) * 100, 2)

    @staticmethod
    def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
        """Current Ratio (liquidity)."""
        if current_liabilities <= 0:
            return None
        return round(current_assets / current_liabilities, 2)
```

**Screener.in Scraper:**

```python
# src/data/providers/free/screener_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

class ScreenerScraper:
    """
    Scraper for Screener.in to get fundamental data.

    IMPORTANT: Be ethical - add delays, respect robots.txt, cache aggressively.
    """

    BASE_URL = "https://www.screener.in"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_company_fundamentals(self, symbol: str) -> dict:
        """
        Fetch fundamental data for a company.

        Returns dict with:
        - pe_ratio
        - pb_ratio
        - debt_to_equity
        - roe
        - roce
        - market_cap
        - etc.
        """
        url = f"{self.BASE_URL}/company/{symbol}/consolidated/"

        try:
            time.sleep(2)  # Rate limiting - be respectful

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse fundamental data
            # (Actual implementation would parse HTML structure)

            data = {
                'symbol': symbol,
                'pe_ratio': None,
                'pb_ratio': None,
                'debt_to_equity': None,
                'roe': None,
                'roce': None,
                'market_cap': None,
                # ... more fields
            }

            return data

        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {e}")
            return None
```

**Database Schema:**

```sql
-- Fundamental data
CREATE TABLE fundamental_data (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    date DATE NOT NULL,
    market_cap DECIMAL(18, 2),
    pe_ratio DECIMAL(10, 2),
    pb_ratio DECIMAL(10, 2),
    debt_to_equity DECIMAL(10, 2),
    roe DECIMAL(10, 2),
    roce DECIMAL(10, 2),
    eps DECIMAL(10, 2),
    book_value DECIMAL(10, 2),
    dividend_yield DECIMAL(5, 2),
    UNIQUE(stock_id, date)
);
```

**Checklist:**
- [ ] Implement FundamentalRatios class
- [ ] Implement ScreenerScraper
- [ ] Add fundamental data schema
- [ ] Create scheduled task for updates
- [ ] Add fundamental data to UI
- [ ] Test with NIFTY 50 stocks

---

#### 2.4 Stock Screener

**Screener Service:**

```python
# src/services/screener_service.py

from typing import List, Dict, Any
from sqlalchemy import and_
from src.data.models.stock import Stock
from src.data.models.fundamental import FundamentalData

class ScreenerService:
    """Stock screening service."""

    def __init__(self, db_session):
        self.db = db_session

    def screen(self, criteria: Dict[str, Any]) -> List[Stock]:
        """
        Screen stocks based on criteria.

        Criteria examples:
        {
            'pe_ratio_max': 20,
            'debt_to_equity_max': 1.0,
            'roe_min': 15,
            'market_cap_min': 1000,  # Crores
            'price_min': 100,
            'price_max': 5000,
            'delivery_pct_min': 50,
            'rsi_max': 70
        }
        """

        # Build query
        # (Implementation would construct SQLAlchemy query)

        results = []

        return results
```

**Screener Page:**

```python
# src/presentation/streamlit_app/pages/02_screener.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Screener", page_icon="🔍", layout="wide")

st.title("🔍 Stock Screener")

# Filters
st.subheader("Screening Criteria")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Valuation**")
    pe_max = st.number_input("Max P/E Ratio", value=25.0)
    pb_max = st.number_input("Max P/B Ratio", value=5.0)

with col2:
    st.write("**Profitability**")
    roe_min = st.number_input("Min ROE (%)", value=15.0)
    debt_to_equity_max = st.number_input("Max Debt/Equity", value=1.0)

with col3:
    st.write("**Technical**")
    rsi_max = st.number_input("Max RSI", value=70.0)
    delivery_min = st.number_input("Min Delivery %", value=50.0)

screen_button = st.button("🔍 Screen Stocks", type="primary")

if screen_button:
    st.info("Screening functionality - Phase 2")
    # Implementation would call ScreenerService
```

**Checklist:**
- [ ] Implement ScreenerService
- [ ] Create Screener UI page
- [ ] Add 10-15 screening criteria
- [ ] Test screener with NIFTY 50
- [ ] Add export to CSV functionality

---

#### 2.5 Basic Sentiment Analysis

**Basic Sentiment Analyzer:**

```python
# src/analysis/sentiment/basic_sentiment.py

from typing import Dict, List
import re

class BasicSentimentAnalyzer:
    """
    Basic keyword-based sentiment analysis.

    For Phase 2, we use simple keyword matching.
    Phase 3 can upgrade to TextBlob or VADER.
    """

    POSITIVE_KEYWORDS = [
        'surge', 'rally', 'gain', 'profit', 'growth', 'strong',
        'rise', 'bullish', 'upgrade', 'beat', 'outperform', 'buy'
    ]

    NEGATIVE_KEYWORDS = [
        'fall', 'drop', 'loss', 'decline', 'weak', 'bearish',
        'downgrade', 'miss', 'underperform', 'sell', 'crash', 'slump'
    ]

    def analyze_text(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text.

        Returns:
        {
            'sentiment': 'positive' | 'negative' | 'neutral',
            'score': float (-1 to 1),
            'confidence': float (0 to 100)
        }
        """
        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)

        # Calculate score
        total = positive_count + negative_count

        if total == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 50.0
            }

        score = (positive_count - negative_count) / total

        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        confidence = min(abs(score) * 100, 100)

        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': round(confidence, 2)
        }

    def analyze_news_batch(self, news_items: List[str]) -> Dict[str, any]:
        """Analyze multiple news items and aggregate sentiment."""

        if not news_items:
            return {'sentiment': 'neutral', 'score': 0.0}

        sentiments = [self.analyze_text(item) for item in news_items]

        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)

        if avg_score > 0.1:
            overall = 'positive'
        elif avg_score < -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'

        return {
            'sentiment': overall,
            'score': round(avg_score, 2),
            'total_articles': len(news_items),
            'positive_count': sum(1 for s in sentiments if s['sentiment'] == 'positive'),
            'negative_count': sum(1 for s in sentiments if s['sentiment'] == 'negative')
        }
```

**News Fetcher:**

```python
# src/data/providers/free/news_fetcher.py

import requests
from datetime import datetime, timedelta

class NewsFetcher:
    """Fetch news from NewsAPI (free tier: 100 requests/day)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"

    def get_stock_news(self, symbol: str, days: int = 7) -> list:
        """Fetch recent news for a stock."""

        url = f"{self.base_url}/everything"

        params = {
            'q': symbol,
            'from': (datetime.now() - timedelta(days=days)).isoformat(),
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = data.get('articles', [])

            return [
                {
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'published_at': article.get('publishedAt'),
                    'source': article.get('source', {}).get('name')
                }
                for article in articles
            ]

        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
```

**Checklist:**
- [ ] Implement BasicSentimentAnalyzer
- [ ] Implement NewsFetcher
- [ ] Add sentiment to Dashboard UI
- [ ] Test with sample news articles
- [ ] Add sentiment to database

---

### Phase 2 Complete Checklist

**NSE Data Integration:**
- [ ] NSEScraper implemented
- [ ] FII/DII data fetching working
- [ ] Delivery percentage fetching working
- [ ] Database schema updated
- [ ] Scheduled tasks configured
- [ ] Data displaying in UI

**Additional Strategies:**
- [ ] 5 new strategies implemented
- [ ] All strategies tested
- [ ] Added to registry
- [ ] UI updated to support all strategies

**Fundamental Analysis:**
- [ ] FundamentalRatios module implemented
- [ ] Screener.in scraper working
- [ ] Database schema created
- [ ] Data fetching scheduled
- [ ] Fundamentals displaying in UI

**Stock Screener:**
- [ ] ScreenerService implemented
- [ ] Screener UI page created
- [ ] 10-15 criteria working
- [ ] Results displaying correctly

**Sentiment Analysis:**
- [ ] BasicSentimentAnalyzer implemented
- [ ] NewsFetcher working
- [ ] Sentiment displaying in UI
- [ ] Database storage configured

**General:**
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Performance acceptable

---

## Phase 3: Scale (2-3 Weeks)

**Goal:** Add paid data sources for real-time/intraday data, enable multiple timeframes, advanced features.

### Scope

**In Scope:**
- ✅ Upstox/Zerodha API integration
- ✅ Real-time data streaming
- ✅ Intraday timeframes (1m, 5m, 15m, 1h)
- ✅ Redis caching for performance
- ✅ Real-time alerts (WebSocket/SSE)
- ✅ Advanced backtesting (Sharpe, Sortino, Drawdown)
- ✅ Portfolio tracking
- ✅ Options basic support

**Out of Scope:**
- ❌ Algo trading execution
- ❌ Complex options strategies
- ❌ Machine learning models

---

### Module Breakdown

#### 3.1 Paid Data Integration

**Upstox Adapter:**

```python
# src/data/adapters/upstox_adapter.py

from .base_adapter import BaseDataAdapter
import requests
from datetime import datetime

class UpstoxAdapter(BaseDataAdapter):
    """Upstox API adapter for real-time data."""

    def __init__(self, api_key: str):
        self.name = "upstox"
        self.api_key = api_key
        self.base_url = "https://api.upstox.com/v2"
        self.supported_timeframes = ['1m', '5m', '15m', '30m', '1h', '1d']

    def get_historical_data(self, symbol, start_date, end_date, timeframe='1d'):
        """Fetch historical intraday data from Upstox."""

        url = f"{self.base_url}/historical-candle"

        # Implementation for Upstox API
        # Returns standardized DataFrame

        pass

    # ... other methods
```

**Update AdapterFactory:**

```python
# Updated src/data/adapters/adapter_factory.py

class AdapterFactory:

    _adapters = {
        'yahoo': YahooFinanceAdapter,
        'nse': NSEAdapter,
        'upstox': UpstoxAdapter,  # NEW
        'zerodha': ZerodhaAdapter,  # NEW
    }

    _timeframe_priority = {
        '1m': ['upstox', 'zerodha'],  # NEW
        '5m': ['upstox', 'zerodha'],  # NEW
        '15m': ['upstox', 'zerodha'],  # NEW
        '1h': ['upstox', 'zerodha'],  # NEW
        '1d': ['upstox', 'yahoo', 'nse'],
        '1wk': ['yahoo'],
        '1mo': ['yahoo'],
    }
```

**Checklist:**
- [ ] Implement UpstoxAdapter
- [ ] Implement ZerodhaAdapter (alternative)
- [ ] Update AdapterFactory
- [ ] Add API credentials to config
- [ ] Test intraday data fetching
- [ ] Update UI to support all timeframes

---

#### 3.2 Redis Caching

**Cache Manager:**

```python
# src/data/cache/cache_manager.py

import redis
import json
from typing import Any, Optional
import pandas as pd

class CacheManager:
    """Redis cache manager for performance optimization."""

    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)

    def get_cached_data(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached DataFrame."""
        cached = self.redis.get(key)
        if cached:
            return pd.read_json(cached)
        return None

    def cache_data(self, key: str, data: pd.DataFrame, ttl: int = 3600):
        """Cache DataFrame with TTL (seconds)."""
        self.redis.setex(key, ttl, data.to_json())

    def invalidate(self, pattern: str):
        """Invalidate cache by pattern."""
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
```

**Checklist:**
- [ ] Install Redis
- [ ] Implement CacheManager
- [ ] Add caching to data fetching
- [ ] Configure TTL strategies
- [ ] Monitor cache hit rates

---

#### 3.3 Real-time Alerts

**Alert Service:**

```python
# src/services/alert_service.py

from typing import List
from src.data.models.alert import Alert

class AlertService:
    """Manage real-time alerts for trading signals."""

    def __init__(self, db_session):
        self.db = db_session

    def create_alert(
        self,
        stock_symbol: str,
        strategy: str,
        condition: str,
        target_value: float
    ):
        """Create new alert."""
        # Implementation
        pass

    def check_alerts(self, stock_symbol: str, current_price: float):
        """Check if any alerts triggered."""
        # Implementation
        pass
```

**Checklist:**
- [ ] Implement AlertService
- [ ] Add alerts database schema
- [ ] Create alerts UI page
- [ ] Add notification system (email/webhook)
- [ ] Test alert triggering

---

#### 3.4 Advanced Backtesting Metrics

**Enhanced Metrics:**

```python
# Add to src/backtesting/metrics.py

class BacktestMetrics:
    """Advanced backtesting metrics."""

    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
        """Calculate Sharpe Ratio."""
        excess_returns = returns - risk_free_rate/252
        return (excess_returns.mean() / excess_returns.std()) * (252 ** 0.5)

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown."""
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        return drawdown.min()

    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
        """Calculate Sortino Ratio (downside deviation)."""
        excess_returns = returns - risk_free_rate/252
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        return (excess_returns.mean() / downside_std) * (252 ** 0.5)
```

**Checklist:**
- [ ] Implement Sharpe Ratio
- [ ] Implement Max Drawdown
- [ ] Implement Sortino Ratio
- [ ] Add to backtesting UI
- [ ] Test calculations

---

### Phase 3 Complete Checklist

**Paid Data Sources:**
- [ ] Upstox adapter implemented
- [ ] Zerodha adapter implemented
- [ ] Intraday data working
- [ ] Real-time streaming working
- [ ] API costs understood and budgeted

**Caching:**
- [ ] Redis installed and configured
- [ ] CacheManager implemented
- [ ] Caching integrated into data flow
- [ ] Performance improvement verified

**Alerts:**
- [ ] AlertService implemented
- [ ] Real-time alert checking working
- [ ] Notification system configured
- [ ] UI for managing alerts created

**Advanced Features:**
- [ ] Advanced metrics implemented
- [ ] Portfolio tracking added
- [ ] Options support (basic) added
- [ ] Performance optimized

**Final Testing:**
- [ ] All tests passing
- [ ] Performance acceptable under load
- [ ] Documentation complete
- [ ] Deployment guide ready

---

## Technical Specifications

### API Endpoints (FastAPI - Optional)

If you decide to separate backend from UI:

```python
# src/presentation/api/main.py

from fastapi import FastAPI
from .routes import stocks, strategies, analysis

app = FastAPI(title="Indian Market Analysis API")

app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

# Example endpoint
@app.get("/api/stocks/{symbol}/price")
def get_stock_price(symbol: str):
    adapter = AdapterFactory.get_adapter()
    price = adapter.get_current_price(symbol)
    return {"symbol": symbol, "price": price}
```

### Timeframe Configuration

```python
# src/utils/constants.py

TIMEFRAME_CONFIG = {
    '1m': {
        'name': '1 Minute',
        'interval_seconds': 60,
        'candles_per_day': 375,  # 6.25 hours trading
        'min_data_points': 100,
        'use_cases': ['scalping', 'high_frequency']
    },
    '5m': {
        'name': '5 Minutes',
        'interval_seconds': 300,
        'candles_per_day': 75,
        'min_data_points': 100,
        'use_cases': ['intraday', 'scalping']
    },
    '15m': {
        'name': '15 Minutes',
        'interval_seconds': 900,
        'candles_per_day': 25,
        'min_data_points': 50,
        'use_cases': ['intraday', 'day_trading']
    },
    '1h': {
        'name': '1 Hour',
        'interval_seconds': 3600,
        'candles_per_day': 6,
        'min_data_points': 50,
        'use_cases': ['swing', 'intraday']
    },
    '1d': {
        'name': '1 Day',
        'interval_seconds': 86400,
        'candles_per_day': 1,
        'min_data_points': 100,
        'use_cases': ['swing', 'positional', 'value_investing']
    },
    '1wk': {
        'name': '1 Week',
        'interval_seconds': 604800,
        'candles_per_day': 0.2,
        'min_data_points': 52,
        'use_cases': ['swing', 'trend_following']
    },
    '1mo': {
        'name': '1 Month',
        'interval_seconds': 2592000,
        'candles_per_day': 0.033,
        'min_data_points': 24,
        'use_cases': ['long_term', 'value_investing']
    }
}
```

---

## Testing Strategy

### Unit Testing Structure

```python
# tests/unit/test_strategies.py

import pytest
import pandas as pd
from src.strategies.technical.sma_crossover import SMACrossover

@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    return pd.DataFrame({
        'open': [100, 102, 101, 105, 107],
        'high': [103, 104, 103, 107, 109],
        'low': [99, 101, 100, 104, 106],
        'close': [102, 103, 102, 106, 108],
        'volume': [1000, 1200, 900, 1500, 1300]
    })

def test_sma_crossover_initialization():
    """Test strategy initialization."""
    strategy = SMACrossover(fast_period=10, slow_period=20)
    assert strategy.params['fast_period'] == 10
    assert strategy.params['slow_period'] == 20

def test_sma_crossover_generates_signals(sample_data):
    """Test signal generation."""
    strategy = SMACrossover(fast_period=2, slow_period=3)
    signals = strategy.analyze(sample_data)

    assert isinstance(signals, list)
    # Add more specific assertions

def test_invalid_data_raises_error():
    """Test that invalid data raises error."""
    strategy = SMACrossover()
    invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})

    with pytest.raises(ValueError):
        strategy.analyze(invalid_data)
```

### Integration Testing

```python
# tests/integration/test_data_flow.py

import pytest
from src.data.adapters.adapter_factory import AdapterFactory
from src.strategies.registry import StrategyRegistry
from datetime import datetime, timedelta

def test_full_analysis_flow():
    """Test complete flow: data fetch → strategy → signals."""

    # Fetch data
    adapter = AdapterFactory.get_adapter(timeframe='1d')
    data = adapter.get_historical_data(
        symbol='RELIANCE',
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now(),
        timeframe='1d'
    )

    assert not data.empty
    assert 'close' in data.columns

    # Run strategy
    strategy = StrategyRegistry.get_strategy('sma_crossover')
    signals = strategy.analyze(data)

    # Verify signals format
    if signals:
        assert hasattr(signals[0], 'signal_type')
        assert hasattr(signals[0], 'price')
        assert hasattr(signals[0], 'confidence')
```

### Data Validation Testing

```python
# tests/unit/test_data_validation.py

import pytest
from src.data.adapters.yahoo_adapter import YahooFinanceAdapter

def test_yahoo_adapter_returns_standard_format():
    """Test that adapter returns data in standard format."""
    adapter = YahooFinanceAdapter()

    data = adapter.get_historical_data(
        symbol='RELIANCE',
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        timeframe='1d'
    )

    required_columns = ['open', 'high', 'low', 'close', 'volume', 'source', 'timeframe']

    for col in required_columns:
        assert col in data.columns

    assert data['source'].iloc[0] == 'yahoo_finance'
    assert data['timeframe'].iloc[0] == '1d'
```

### Testing Checklist

**Unit Tests:**
- [ ] All strategies have unit tests
- [ ] All adapters have unit tests
- [ ] All analysis modules have unit tests
- [ ] Edge cases covered
- [ ] Test coverage > 80%

**Integration Tests:**
- [ ] Data flow end-to-end tested
- [ ] Database operations tested
- [ ] API endpoints tested (if applicable)

**Performance Tests:**
- [ ] Load testing with 50+ stocks
- [ ] Response time < 3 seconds for analysis
- [ ] Database queries optimized

**Data Quality Tests:**
- [ ] Data validation rules defined
- [ ] Missing data handling tested
- [ ] Outlier detection tested

---

## Useful Additions

### 1. Environment Setup Guide

```bash
# Initial setup script
#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install TA-Lib (requires system package)
# macOS:
brew install ta-lib

# Ubuntu/Debian:
sudo apt-get install ta-lib

# Windows: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

# Setup PostgreSQL
createdb market_analysis

# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_nifty50.py

echo "Setup complete! Run: streamlit run src/presentation/streamlit_app/app.py"
```

### 2. Configuration Management

```python
# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Data Sources
    YAHOO_FINANCE_ENABLED = os.getenv('YAHOO_FINANCE_ENABLED', 'true').lower() == 'true'
    NSE_SCRAPING_ENABLED = os.getenv('NSE_SCRAPING_ENABLED', 'false').lower() == 'true'

    # API Keys
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    UPSTOX_API_KEY = os.getenv('UPSTOX_API_KEY')
    ZERODHA_API_KEY = os.getenv('ZERODHA_API_KEY')

    # Application Settings
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DATA_UPDATE_TIME = os.getenv('DATA_UPDATE_TIME', '17:00')

    # Rate Limiting
    RATE_LIMITS = {
        'yahoo': 2000,  # requests per hour
        'nse': 100,
        'screener': 50,
        'newsapi': 100  # per day on free tier
    }

    # Cache Settings
    CACHE_TTL = {
        '1m': 60,       # 1 minute
        '5m': 300,      # 5 minutes
        '1d': 86400,    # 1 day
        'fundamental': 604800  # 1 week
    }
```

### 3. Logging Configuration

```python
# src/utils/logger.py

import logging
from config import Config

def setup_logger(name: str) -> logging.Logger:
    """Setup application logger."""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)

    # File handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

### 4. Error Handling Patterns

```python
# src/utils/error_handlers.py

from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_data_fetch_errors(func):
    """Decorator for handling data fetching errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching data in {func.__name__}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise

    return wrapper

def handle_strategy_errors(func):
    """Decorator for handling strategy execution errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Invalid data in {func.__name__}: {e}")
            return []
        except Exception as e:
            logger.error(f"Strategy error in {func.__name__}: {e}")
            raise

    return wrapper
```

### 5. Rate Limiting

```python
# src/utils/rate_limiter.py

import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self):
        self.calls = defaultdict(list)
        self.lock = Lock()

    def check_rate_limit(self, source: str, max_calls: int, time_window: int) -> bool:
        """
        Check if rate limit is exceeded.

        Args:
            source: Data source name
            max_calls: Maximum calls allowed
            time_window: Time window in seconds

        Returns:
            True if call is allowed, False otherwise
        """

        with self.lock:
            current_time = time.time()

            # Remove old calls outside time window
            self.calls[source] = [
                call_time for call_time in self.calls[source]
                if current_time - call_time < time_window
            ]

            # Check if limit exceeded
            if len(self.calls[source]) >= max_calls:
                return False

            # Record this call
            self.calls[source].append(current_time)
            return True

    def wait_if_needed(self, source: str, max_calls: int, time_window: int):
        """Wait if rate limit is exceeded."""

        while not self.check_rate_limit(source, max_calls, time_window):
            time.sleep(1)
```

### 6. Data Quality Checks

```python
# src/utils/data_quality.py

import pandas as pd
from typing import Dict, List

class DataQualityChecker:
    """Validate data quality."""

    @staticmethod
    def check_ohlcv_data(df: pd.DataFrame) -> Dict[str, any]:
        """
        Check OHLCV data quality.

        Returns dict with:
        - is_valid: bool
        - issues: list of issues found
        """

        issues = []

        # Check required columns
        required = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in df.columns]
        if missing:
            issues.append(f"Missing columns: {missing}")

        # Check for null values
        null_counts = df[required].isnull().sum()
        if null_counts.any():
            issues.append(f"Null values found: {null_counts.to_dict()}")

        # Check OHLC relationships
        invalid_ohlc = df[
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        ]

        if not invalid_ohlc.empty:
            issues.append(f"Invalid OHLC relationships in {len(invalid_ohlc)} rows")

        # Check for negative values
        negative = df[(df[required] < 0).any(axis=1)]
        if not negative.empty:
            issues.append(f"Negative values found in {len(negative)} rows")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'total_rows': len(df),
            'date_range': (df.index.min(), df.index.max()) if not df.empty else None
        }
```

### 7. Performance Optimization Checklist

**Database:**
- [ ] Indexes on frequently queried columns
- [ ] Partitioning for large tables (TimescaleDB)
- [ ] Connection pooling configured
- [ ] Query optimization (EXPLAIN ANALYZE)

**Data Fetching:**
- [ ] Parallel fetching for multiple stocks
- [ ] Caching of frequently accessed data
- [ ] Rate limiting to avoid API bans
- [ ] Incremental updates instead of full refreshes

**Application:**
- [ ] Streamlit caching (@st.cache_data)
- [ ] Lazy loading of data
- [ ] Pagination for large result sets
- [ ] Background tasks for heavy computations

### 8. Security Considerations

```python
# Security best practices

# 1. API Key Management
# - Never commit .env file
# - Use environment variables
# - Rotate keys regularly

# 2. Database Security
# - Use parameterized queries (SQLAlchemy ORM)
# - Limit database user permissions
# - Enable SSL for connections

# 3. Input Validation
def validate_stock_symbol(symbol: str) -> bool:
    """Validate stock symbol format."""
    import re
    # Only allow alphanumeric and periods/hyphens
    pattern = r'^[A-Z0-9\.\-]{1,20}$'
    return bool(re.match(pattern, symbol.upper()))

# 4. Rate Limiting
# - Implement rate limiting for API calls
# - Prevent DDoS on scraped websites
# - Respect robots.txt

# 5. Data Privacy
# - Don't store sensitive user data unnecessarily
# - Encrypt sensitive data at rest
# - Comply with data retention policies
```

### 9. Troubleshooting Common Issues

**Issue 1: Yahoo Finance data not loading**
```python
# Solution: Add delay and retry logic

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_with_retry(symbol):
    return yf.download(symbol, period='1y')
```

**Issue 2: NSE scraping blocked**
```python
# Solution: Rotate user agents and add delays

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
    # ... more user agents
]

import random
headers = {'User-Agent': random.choice(USER_AGENTS)}
```

**Issue 3: Database performance slow**
```sql
-- Solution: Add missing indexes

CREATE INDEX CONCURRENTLY idx_stock_prices_symbol_date
ON stock_prices(stock_id, date DESC);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM stock_prices WHERE stock_id = 1 ORDER BY date DESC LIMIT 100;
```

**Issue 4: Streamlit app slow to load**
```python
# Solution: Use caching

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_stock_data(symbol):
    # Expensive operation
    return data

# Also: Lazy load data only when needed
if st.button("Analyze"):
    data = load_stock_data(symbol)
```

### 10. Migration Path: Free → Paid

**Step-by-Step Migration:**

1. **Add Paid API Credentials**
```bash
# .env
UPSTOX_API_KEY=your_key_here
UPSTOX_API_SECRET=your_secret_here
```

2. **Enable Paid Adapter**
```python
# config.py
PAID_DATA_ENABLED = True
```

3. **Test Intraday Data**
```python
# Test script
adapter = AdapterFactory.get_adapter(timeframe='5m')
data = adapter.get_historical_data('RELIANCE', ...)
print(data.head())
```

4. **Update UI**
```python
# Add timeframe selector
timeframe = st.selectbox(
    "Timeframe",
    ['1m', '5m', '15m', '1h', '1d', '1wk', '1mo']
)
```

5. **Monitor Costs**
```python
# Track API usage
class APIUsageTracker:
    def __init__(self):
        self.calls = defaultdict(int)

    def track_call(self, source: str):
        self.calls[source] += 1
        # Log to database for billing tracking
```

---

## Appendix

### A. NIFTY 50 Stock List (Seed Data)

```python
# scripts/seed_nifty50.py

NIFTY50_STOCKS = [
    {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.', 'sector': 'Energy'},
    {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd.', 'sector': 'IT'},
    {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd.', 'sector': 'Financials'},
    {'symbol': 'INFY', 'name': 'Infosys Ltd.', 'sector': 'IT'},
    {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd.', 'sector': 'Financials'},
    {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd.', 'sector': 'FMCG'},
    {'symbol': 'ITC', 'name': 'ITC Ltd.', 'sector': 'FMCG'},
    {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Financials'},
    {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd.', 'sector': 'Telecom'},
    {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Ltd.', 'sector': 'Financials'},
    # ... Add all 50 stocks
]

def seed_nifty50(db_session):
    """Seed NIFTY 50 stocks into database."""
    from src.data.models.stock import Stock

    for stock_data in NIFTY50_STOCKS:
        stock = Stock(**stock_data, exchange='NSE', is_active=True)
        db_session.add(stock)

    db_session.commit()
    print("NIFTY 50 stocks seeded successfully!")
```

### B. Additional Strategy Templates

**MACD Strategy:**

```python
# src/strategies/technical/macd_strategy.py

class MACDStrategy(BaseStrategy):
    """MACD (Moving Average Convergence Divergence) Strategy."""

    def get_default_params(self):
        return {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }

    def analyze(self, data: pd.DataFrame) -> list:
        """Generate signals based on MACD crossover."""

        # Calculate MACD
        exp1 = data['close'].ewm(span=self.params['fast_period']).mean()
        exp2 = data['close'].ewm(span=self.params['slow_period']).mean()
        data['macd'] = exp1 - exp2
        data['signal'] = data['macd'].ewm(span=self.params['signal_period']).mean()
        data['histogram'] = data['macd'] - data['signal']

        signals = []

        for i in range(1, len(data)):
            prev_macd = data['macd'].iloc[i-1]
            prev_signal = data['signal'].iloc[i-1]
            curr_macd = data['macd'].iloc[i]
            curr_signal = data['signal'].iloc[i]

            # Bullish crossover
            if prev_macd <= prev_signal and curr_macd > curr_signal:
                signals.append(Signal(
                    date=str(data.index[i].date()),
                    signal_type='BUY',
                    price=data['close'].iloc[i],
                    confidence=min(abs(data['histogram'].iloc[i]) * 50, 100),
                    metadata={'macd': curr_macd, 'signal': curr_signal}
                ))

            # Bearish crossover
            elif prev_macd >= prev_signal and curr_macd < curr_signal:
                signals.append(Signal(
                    date=str(data.index[i].date()),
                    signal_type='SELL',
                    price=data['close'].iloc[i],
                    confidence=min(abs(data['histogram'].iloc[i]) * 50, 100),
                    metadata={'macd': curr_macd, 'signal': curr_signal}
                ))

        self.signals = signals
        return signals
```

### C. Git Workflow

```.gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Environment
.env
.env.local

# Database
*.db
*.sqlite

# Logs
*.log
app.log

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Data
data/raw/
data/cache/
```

**Recommended Git Workflow:**

```bash
# Feature development
git checkout -b feature/add-bollinger-bands
# ... make changes ...
git add .
git commit -m "Add Bollinger Bands strategy"
git push origin feature/add-bollinger-bands

# Create PR, review, merge to main

# Release
git tag -a v1.0.0 -m "Phase 1 MVP Release"
git push origin v1.0.0
```

---

## Summary & Next Steps

### Quick Start (Day 1)

1. **Clone/Create project structure**
2. **Set up virtual environment**
3. **Install dependencies**
4. **Configure PostgreSQL**
5. **Run database migrations**
6. **Seed NIFTY 50 data**
7. **Test Yahoo Finance adapter**
8. **Run Streamlit app**

### Development Path

**Weeks 1-2:** Phase 1 MVP foundation
**Weeks 3-4:** Phase 1 completion + testing
**Weeks 5-6:** Phase 2 enhancement
**Weeks 7-8:** Phase 2 completion + testing
**Weeks 9-10:** Phase 3 scaling
**Weeks 11-12:** Phase 3 completion + deployment

### Success Criteria

**Phase 1:**
- ✅ Can analyze any NIFTY 50 stock
- ✅ 3 strategies working correctly
- ✅ Backtesting shows accurate results
- ✅ UI is responsive and intuitive

**Phase 2:**
- ✅ FII/DII data integrated
- ✅ 8-10 strategies available
- ✅ Screener finds valid opportunities
- ✅ Fundamental data displays correctly

**Phase 3:**
- ✅ Intraday data working
- ✅ Real-time alerts functioning
- ✅ Performance optimized
- ✅ Ready for production deployment

---

## Document Maintenance

**Version History:**
- v1.0 (2025-11-09): Initial roadmap created

**Update This Document:**
- When completing major milestones
- When architectural decisions change
- When new features are added
- Monthly review and refinement

**Questions/Issues:**
Track implementation questions and blockers here:

- [ ] TBD based on development progress

---

**Remember:** This is a living document. Update it as you progress, add learnings, and refine the approach. The goal is to have a single source of truth for the entire project.

**Good luck building your Indian Market Analysis application!** 🚀📈
