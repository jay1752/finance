# Indian Market Analysis Application - Complete Guide

**Complete reference from setup to current state**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Initial Setup](#initial-setup)
3. [Phase 1 - MVP (Completed)](#phase-1---mvp-completed)
4. [Phase 2.1 - NSE Integration (Completed)](#phase-21---nse-integration-completed)
5. [Phase 2.2 - Additional Strategies (Completed)](#phase-22---additional-strategies-completed)
6. [Phase 2.3 - Optimization & Testing (Completed)](#phase-23---optimization--testing-completed)
7. [Phase 3 - Stock Screener (Completed)](#phase-3---stock-screener-completed)
8. [Phase 4 - Portfolio & Risk Management (Completed)](#phase-4---portfolio--risk-management-completed)
9. [Phase 6 - Sentiment Analysis (Completed)](#phase-6---sentiment-analysis-completed)
10. [How to Use](#how-to-use)
11. [Testing & Optimization Guide](#testing--optimization-guide)
12. [Stock Screener Guide](#stock-screener-guide)
13. [Portfolio & Risk Management Guide](#portfolio--risk-management-guide)
14. [Sentiment Analysis Guide](#sentiment-analysis-guide)
15. [Testing Procedures Guide](#testing-procedures-guide)
16. [Architecture Overview](#architecture-overview)
17. [Next Steps](#next-steps)

---

## Project Overview

**Goal**: Build a comprehensive Indian stock market analysis application with:
- Multiple data sources (free → paid progression)
- Technical analysis with multiple strategies
- Backtesting capabilities
- NSE-specific metrics (FII/DII, delivery %)
- Scalable architecture

**Tech Stack**:
- Python 3.13
- Streamlit (UI)
- Pandas/NumPy (data processing)
- Yahoo Finance (free OHLCV data)
- NSE scraping (Indian market metrics)
- PostgreSQL + TimescaleDB (optional database)
- SQLAlchemy (ORM)

---

## Initial Setup

### 1. Prerequisites

```bash
# System requirements
- Python 3.13+
- pip and venv
- PostgreSQL (optional, for database features)

# macOS
brew install python@3.13
# brew install postgresql  # Optional

# Ubuntu
sudo apt-get install python3.13 python3.13-venv
# sudo apt-get install postgresql  # Optional
```

### 2. Quick Start

```bash
# Clone/navigate to project
cd /path/to/finance

# Run setup script
./setup.sh

# This will:
# - Create virtual environment (venv/)
# - Install all dependencies
# - Copy .env.example to .env
# - Run setup tests
```

### 3. Manual Setup (if needed)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Test setup
python test_setup.py
```

### 4. Configuration

Edit `.env`:

```bash
# Database (optional for Phase 1)
DATABASE_URL=postgresql://user:password@localhost:5432/market_analysis

# Data Sources
YAHOO_FINANCE_ENABLED=true
NSE_SCRAPING_ENABLED=true

# App Settings
DEBUG=true
LOG_LEVEL=INFO
DATA_UPDATE_TIME=17:00
```

---

## Phase 1 - MVP (Completed ✅)

### What Was Built

**Core Architecture**:
```
src/
├── data/
│   ├── adapters/          # Data source abstraction layer
│   │   ├── base_adapter.py         # Abstract interface
│   │   ├── yahoo_adapter.py        # Yahoo Finance implementation
│   │   └── adapter_factory.py      # Auto-selects best adapter
│   └── models/            # SQLAlchemy models (optional DB)
│       ├── stock.py
│       ├── stock_price.py
│       ├── signal.py
│       └── backtest_result.py
│
├── strategies/            # Trading strategies
│   ├── base.py                     # Base strategy class
│   ├── registry.py                 # Strategy auto-registration
│   └── technical/
│       ├── sma_crossover.py        # SMA crossover strategy
│       ├── rsi_strategy.py         # RSI mean reversion
│       └── vwap_strategy.py        # VWAP strategy
│
├── backtesting/           # Backtesting engine
│   └── engine.py          # Simple backtesting with metrics
│
├── presentation/
│   └── streamlit_app/     # Web UI
│       ├── app.py                  # Landing page
│       └── pages/
│           ├── 01_dashboard.py     # Stock analysis
│           └── 03_backtesting.py   # Backtest strategies
│
└── utils/                 # Utilities
    ├── database.py        # DB connection management
    ├── logger.py          # Logging config
    ├── constants.py       # Constants
    └── validators.py      # Input validation
```

**Key Features**:
1. ✅ Yahoo Finance integration for daily OHLCV data
2. ✅ 3 technical strategies (SMA, RSI, VWAP)
3. ✅ Interactive dashboard with signal generation
4. ✅ Backtesting engine with performance metrics
5. ✅ Adapter pattern for flexible data sources
6. ✅ Strategy registry for dynamic loading

### How to Run Phase 1

```bash
# Activate environment
source venv/bin/activate

# Launch app
streamlit run src/presentation/streamlit_app/app.py

# Open browser to http://localhost:8501
```

**Usage**:
1. Go to "Dashboard" page
2. Enter stock symbol (e.g., RELIANCE, TCS)
3. Select date range
4. Choose strategy and adjust parameters
5. Click "Analyze" to see signals

---

## Phase 2.1 - NSE Integration (Completed ✅)

### What Was Built

**New Components**:

```
src/
├── data/
│   ├── adapters/
│   │   └── nse_adapter.py          # ✨ NEW: NSE data adapter
│   ├── models/
│   │   ├── fii_dii_data.py         # ✨ NEW: FII/DII model
│   │   └── delivery_data.py        # ✨ NEW: Delivery % model
│   └── providers/
│       └── free/
│           └── nse_scraper.py      # ✨ NEW: NSE web scraper
│
└── presentation/
    └── streamlit_app/
        └── pages/
            └── 01_dashboard.py     # ✨ UPDATED: NSE metrics panel

scripts/
├── nse_data_updater.py             # ✨ NEW: Daily NSE data updater
└── NSE_UPDATER_README.md           # ✨ NEW: Updater docs

database/
└── schema.sql                      # ✨ UPDATED: FII/DII & delivery tables
```

**NSE-Specific Features**:

1. **FII/DII Data** (Foreign/Domestic Institutional Investment)
   - Shows institutional money flow
   - Positive = Buying (bullish), Negative = Selling (bearish)
   - Market sentiment indicator
   - Unique to Indian markets

2. **Delivery Percentage**
   - Shows genuine buying vs speculation
   - >60% = Strong genuine buying
   - <40% = High speculation/intraday
   - Per-stock daily metric

3. **Market Status & Indices**
   - Live market open/closed status
   - NIFTY 50 index with changes
   - Timestamp of data

### Database Tables (Optional)

If using PostgreSQL:

```sql
-- FII/DII data (market-wide)
CREATE TABLE fii_dii_data (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    fii_net DECIMAL(12, 2),        -- Crores
    dii_net DECIMAL(12, 2),        -- Crores
    fii_gross_purchase DECIMAL(12, 2),
    fii_gross_sale DECIMAL(12, 2),
    dii_gross_purchase DECIMAL(12, 2),
    dii_gross_sale DECIMAL(12, 2)
);

-- Delivery data (per stock)
CREATE TABLE delivery_data (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    date DATE NOT NULL,
    delivery_quantity BIGINT,
    traded_quantity BIGINT,
    delivery_percentage DECIMAL(5, 2),
    UNIQUE(stock_id, date)
);
```

To set up database:

```bash
# Install PostgreSQL first
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Ubuntu

# Create database and tables
python scripts/setup_db.py
python scripts/seed_nifty50.py
```

### NSE Data Updater

**Purpose**: Automatically fetch and store NSE data daily.

```bash
# Run once manually
python scripts/nse_data_updater.py --once

# Run as scheduled service (daily at 5:30 PM)
python scripts/nse_data_updater.py

# Custom schedule
python scripts/nse_data_updater.py --hour 18 --minute 0
```

**Scheduling Options**:

1. **Built-in scheduler** (runs continuously):
   ```bash
   nohup python scripts/nse_data_updater.py > logs/nse_updater.log 2>&1 &
   ```

2. **Cron** (Linux/macOS):
   ```bash
   crontab -e
   # Add: 30 17 * * * cd /path/to/finance && source venv/bin/activate && python scripts/nse_data_updater.py --once
   ```

3. **systemd** (Linux) or **launchd** (macOS):
   See `scripts/NSE_UPDATER_README.md` for details

---

## Phase 4 - Portfolio & Risk Management (Completed)

**Goal**: Add professional portfolio tracking and risk management capabilities.

**Status**: ✅ Complete

### Overview

Phase 4 completes the trading workflow by adding:
- **Position Sizing**: Calculate optimal position sizes using 5 professional methods
- **Risk Management**: Stop-loss and take-profit automation
- **Portfolio Tracking**: Multi-position portfolio with real-time P&L
- **Risk Monitoring**: Auto-alerts for stop-loss/take-profit hits

This phase makes the application production-ready for real trading with proper risk controls.

### What Was Built

#### 1. Position Sizer (`src/portfolio/position_sizer.py`)

Professional position sizing methods:

**Kelly Criterion**:
```python
from src.portfolio import PositionSizer

sizer = PositionSizer(capital=100000)
result = sizer.kelly_criterion(
    win_rate=0.65,          # 65% win rate
    avg_win=8.5,            # Average win: 8.5%
    avg_loss=4.2,           # Average loss: 4.2%
    price=2847.50,
    kelly_fraction=0.25     # Quarter-Kelly for safety
)

print(f"Buy {result.shares} shares")
print(f"Allocation: ₹{result.capital_allocation:,.0f}")
print(f"Risk: ₹{result.risk_amount:,.0f}")
```

**Fixed Fractional**:
```python
# Risk 2% of capital per trade
result = sizer.fixed_fractional(
    price=2847.50,
    risk_percentage=0.02,   # Risk 2%
    stop_loss_pct=5.0       # 5% stop-loss
)
```

**Risk-Based (ATR)**:
```python
# Position size based on volatility
result = sizer.risk_based(
    price=2847.50,
    atr=50.0,               # Average True Range
    atr_multiplier=2.0,     # Stop = 2× ATR
    risk_percentage=0.02
)
```

**Equal Weight**:
```python
# Divide capital equally among N positions
result = sizer.equal_weight(
    price=2847.50,
    num_positions=5         # 5 total positions
)
```

**Fixed Amount**:
```python
# Invest fixed amount per position
result = sizer.fixed_amount(
    price=2847.50,
    amount=20000           # ₹20,000 per position
)
```

#### 2. Risk Manager (`src/portfolio/risk_manager.py`)

Comprehensive risk management tools:

**Stop-Loss Methods**:
```python
from src.portfolio import RiskManager

risk_mgr = RiskManager()

# Fixed % stop-loss
stop = risk_mgr.fixed_stop_loss(
    entry_price=2847.50,
    stop_pct=5.0            # 5% below entry
)
print(f"Stop-Loss: ₹{stop.price:.2f}")  # ₹2705.12

# ATR-based stop-loss
stop = risk_mgr.atr_stop_loss(
    entry_price=2847.50,
    atr=50.0,
    multiplier=2.0
)

# Support/Resistance stop
stop = risk_mgr.support_resistance_stop(
    entry_price=2847.50,
    support_level=2750.0,
    buffer_pct=0.5
)

# Trailing stop
stop = risk_mgr.trailing_stop_loss(
    entry_price=2847.50,
    current_price=2950.00,
    trail_pct=5.0
)
```

**Take-Profit Methods**:
```python
# Fixed % take-profit
target = risk_mgr.fixed_take_profit(
    entry_price=2847.50,
    profit_pct=10.0         # 10% above entry
)

# Risk-Reward ratio
target = risk_mgr.risk_reward_take_profit(
    entry_price=2847.50,
    stop_loss_price=2705.12,
    risk_reward_ratio=2.0   # 2:1 reward:risk
)
print(f"Take-Profit: ₹{target.price:.2f}")  # ₹3132.25

# Multiple targets
targets = risk_mgr.multiple_targets(
    entry_price=2847.50,
    targets=[5, 10, 15]     # 5%, 10%, 15% targets
)
```

**Risk Checks**:
```python
# Check if position risk is acceptable
is_ok, msg = risk_mgr.check_position_risk(
    capital=100000,
    position_value=28475,
    stop_loss_pct=5.0
)

# Check daily loss limit
can_trade, msg = risk_mgr.check_daily_loss_limit(
    capital=100000,
    daily_pnl=-3500         # Lost ₹3500 today
)

# Check portfolio risk
is_ok, msg = risk_mgr.check_portfolio_risk(
    capital=100000,
    total_risk_amount=8500  # Total risk across all positions
)
```

#### 3. Portfolio Tracker (`src/portfolio/portfolio.py`)

Complete portfolio management:

**Creating and Managing Portfolio**:
```python
from src.portfolio import Portfolio

# Create portfolio
portfolio = Portfolio(
    initial_capital=100000,
    name="My Trading Portfolio"
)

# Open position with risk management
position = portfolio.open_position(
    symbol='RELIANCE',
    shares=10,
    entry_price=2847.50,
    stop_loss=stop,         # From RiskManager
    take_profit=target,     # From RiskManager
    direction='LONG',
    notes='RSI oversold signal'
)

print(f"Position opened: {position}")
print(f"Cash remaining: ₹{portfolio.cash:,.0f}")

# Check portfolio value
summary = portfolio.get_summary()
print(f"Portfolio Value: ₹{summary['current_value']:,.0f}")
print(f"Total P&L: ₹{summary['total_pnl']:,.0f} ({summary['total_pnl_pct']:.2f}%)")
```

**Real-time Monitoring**:
```python
# Check if stops/targets hit
alerts = portfolio.check_stops_and_targets()

if alerts['stop_loss_hit']:
    print(f"STOP-LOSS HIT: {alerts['stop_loss_hit']}")
    # Auto-close or notify

if alerts['take_profit_hit']:
    print(f"TAKE-PROFIT HIT: {alerts['take_profit_hit']}")
    # Auto-close or scale out

# Get risk exposure
risk_data = portfolio.get_risk_exposure()
print(f"Total Risk: ₹{risk_data['total_risk']:,.0f} ({risk_data['total_risk_pct']:.2f}%)")
```

**Closing Positions**:
```python
# Close position
closed = portfolio.close_position(
    symbol='RELIANCE',
    exit_price=2950.00,
    notes='Take-profit hit'
)

pnl = closed.calculate_pnl(2950.00)
print(f"P&L: ₹{pnl['pnl']:,.2f} ({pnl['pnl_pct']:.2f}%)")
```

**Portfolio Reports**:
```python
# Get positions as DataFrame
df = portfolio.get_positions_dataframe(include_closed=True)
print(df)

# Export to CSV
df.to_csv('my_portfolio.csv', index=False)

# Full summary
summary = portfolio.get_summary()
print(f"Win Rate: {summary['win_rate']:.1f}%")
print(f"Total Trades: {summary['num_closed_positions']}")
```

#### 4. Portfolio Dashboard (`pages/06_portfolio.py`)

Complete Streamlit dashboard with 4 tabs:

**Tab 1: Portfolio Overview**
- Portfolio summary (value, cash, P&L)
- Risk metrics (positions, risk %, win rate)
- Open positions table (color-coded)
- Stop-loss/take-profit alerts
- Close position interface
- Closed positions history

**Tab 2: Add Position**
- Position entry form
- Risk management configuration
- Stop-loss calculator (Fixed % or ATR)
- Take-profit calculator (Fixed % or R:R ratio)
- Position summary preview
- One-click add to portfolio

**Tab 3: Position Sizer**
- Position size calculator
- All 5 sizing methods available
- Method-specific parameters
- Real-time calculation
- Risk % display
- Calculation details

**Tab 4: Performance**
- Performance metrics
- Cumulative P&L chart
- Trade history table
- Win/loss analysis
- Color-coded results

### Key Features

**Position Sizing:**
- 5 professional methods (Kelly, Fixed Fractional, Risk-Based, Equal Weight, Fixed Amount)
- Automatic risk calculation
- Capital allocation optimization
- Position size capping (max 20% per position)

**Risk Management:**
- 4 stop-loss types (Fixed %, ATR, S/R, Trailing)
- 3 take-profit methods (Fixed %, R:R Ratio, Multiple Targets)
- Portfolio-level risk limits
- Daily loss limits (default: 5%)
- Position risk limits (default: 2%)

**Portfolio Tracking:**
- Multi-position management
- Real-time P&L calculation
- Unrealized vs Realized P&L
- Automatic stop/target monitoring
- Position alerts
- Trade history

**Dashboard:**
- 4 comprehensive tabs
- Color-coded visualizations
- Real-time price fetching
- One-click operations
- Export to CSV

### Testing

Test all features:

```bash
# Test position sizing
python -c "
from src.portfolio import PositionSizer

sizer = PositionSizer(capital=100000)
result = sizer.kelly_criterion(0.65, 8.5, 4.2, 2847.50, 0.25)
print(f'Kelly: {result.shares} shares, ₹{result.capital_allocation:,.0f}')

result = sizer.fixed_fractional(2847.50, stop_loss_pct=5.0)
print(f'Fixed Fractional: {result.shares} shares, ₹{result.capital_allocation:,.0f}')
"

# Test risk management
python -c "
from src.portfolio import RiskManager

risk_mgr = RiskManager()
stop = risk_mgr.fixed_stop_loss(2847.50, 5.0)
target = risk_mgr.risk_reward_take_profit(2847.50, stop.price, 2.0)

print(f'Stop-Loss: ₹{stop.price:.2f}')
print(f'Take-Profit: ₹{target.price:.2f}')
"

# Test portfolio
python -c "
from src.portfolio import Portfolio, RiskManager

portfolio = Portfolio(100000, 'Test Portfolio')

risk_mgr = RiskManager()
stop = risk_mgr.fixed_stop_loss(2847.50, 5.0)
target = risk_mgr.risk_reward_take_profit(2847.50, stop.price, 2.0)

# Open position
pos = portfolio.open_position('RELIANCE', 10, 2847.50, stop, target)
print(f'Opened: {pos.shares} shares at ₹{pos.entry_price:.2f}')

# Close position
closed = portfolio.close_position('RELIANCE', 2950.00)
pnl = closed.calculate_pnl(2950.00)
print(f'P&L: ₹{pnl[\"pnl\"]:,.2f} ({pnl[\"pnl_pct\"]:.2f}%)')
"
```

### Files Created

```
src/portfolio/
├── __init__.py           # Module exports
├── position_sizer.py     # Position sizing (350 lines)
├── risk_manager.py       # Risk management (420 lines)
└── portfolio.py          # Portfolio tracker (500 lines)

src/presentation/streamlit_app/pages/
└── 06_portfolio.py       # Portfolio dashboard (650 lines)
```

### What's Next

With Phase 4 complete, you have a **full-featured trading system**:
- Strategy development ✅
- Backtesting ✅
- Optimization ✅
- Screening ✅
- Portfolio & Risk Management ✅

**Recommended Next Steps:**
1. **Phase 5 - Real-time & Alerts**: Live data and notifications
2. **Phase 6 - Sentiment Analysis**: News context for trading decisions ✅ **COMPLETED**
3. **Phase 8 - Trading Bot**: Full automation with broker integration

---

## Phase 6 - Sentiment Analysis (Completed)

**Goal**: Add news sentiment analysis to inform trading decisions with market context.

**Status**: ✅ Complete

### Overview

Phase 6 adds intelligent news analysis capabilities:
- **News Fetching**: Aggregate news from multiple free sources (Yahoo Finance, Google News)
- **Sentiment Analysis**: Analyze news sentiment using VADER and TextBlob
- **Trading Signals**: Generate BUY/SELL/HOLD signals based on news sentiment
- **Sentiment Dashboard**: Interactive UI for sentiment analysis and comparison

This phase complements technical analysis with fundamental market context from news sentiment.

### What Was Built

#### 1. News Fetcher (`src/sentiment/news_fetcher.py`)

Fetch news from multiple sources without API keys:

**Basic News Fetching**:
```python
from src.sentiment import NewsFetcher

fetcher = NewsFetcher()

# Fetch news for a stock
news = fetcher.fetch_news(
    symbol='RELIANCE',
    max_results=20,
    days_back=7
)

for article in news:
    print(f"{article.title} - {article.source}")
    print(f"Published: {article.published_date}")
    print(f"URL: {article.url}\n")
```

**News Sources**:
1. **Yahoo Finance** (via yfinance): Free, reliable financial news
2. **Google News** (web scraping): Broad coverage, latest headlines
3. **NewsAPI.org** (optional): Enhanced coverage with API key

**Advanced Features**:
```python
# Get trending stocks (most news coverage)
trending = fetcher.get_trending_stocks(limit=10)
for stock in trending:
    print(f"{stock['symbol']}: {stock['news_count']} articles")

# Filter by sources
news = fetcher.fetch_news(
    symbol='TCS',
    sources=['yahoo', 'google']  # Choose specific sources
)
```

#### 2. Sentiment Analyzer (`src/sentiment/sentiment_analyzer.py`)

Analyze text sentiment using multiple methods:

**VADER Analysis (Recommended for News)**:
```python
from src.sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer(method='vader')

# Analyze a headline
text = "Reliance Industries reports record quarterly profit, beats estimates"
sentiment = analyzer.analyze_text(text)

print(f"Sentiment: {sentiment.sentiment}")      # 'positive'
print(f"Score: {sentiment.score:.2f}")          # 0.73 (range: -1 to +1)
print(f"Confidence: {sentiment.confidence:.2f}") # 0.73
print(f"Method: {sentiment.method}")            # 'vader'

# Breakdown shows detailed scores
print(sentiment.breakdown)
# {'positive': 0.35, 'negative': 0.0, 'neutral': 0.65}
```

**Available Methods**:
```python
# TextBlob (general purpose)
analyzer = SentimentAnalyzer(method='textblob')
sentiment = analyzer.analyze_text(text)

# Combined (averages VADER + TextBlob)
analyzer = SentimentAnalyzer(method='combined')
sentiment = analyzer.analyze_text(text)

# Simple keywords (fallback, no libraries needed)
# Automatically used if VADER/TextBlob unavailable
```

**Sentiment Classification**:
- **Positive**: Score > 0.1
- **Negative**: Score < -0.1
- **Neutral**: Score between -0.1 and 0.1

**Financial Keywords Extraction**:
```python
keywords = analyzer.get_financial_keywords(
    "Company announces dividend increase and record revenue growth"
)
print(keywords['positive_keywords'])
# ['dividend increase', 'revenue growth']
print(keywords['negative_keywords'])
# []
```

#### 3. Sentiment Scorer (`src/sentiment/sentiment_scorer.py`)

High-level API combining news + sentiment:

**Single Stock Analysis**:
```python
from src.sentiment import SentimentScorer

scorer = SentimentScorer(sentiment_method='vader')

# Analyze sentiment for a stock
sentiment = scorer.analyze_stock(
    symbol='RELIANCE',
    max_news=20,
    days_back=7
)

print(f"Symbol: {sentiment.symbol}")
print(f"Overall Sentiment: {sentiment.overall_sentiment}")  # 'positive'
print(f"Overall Score: {sentiment.overall_score:.2f}")      # 0.42
print(f"Confidence: {sentiment.confidence:.2%}")            # 65%
print(f"News Analyzed: {sentiment.news_count}")             # 15

print(f"Positive News: {sentiment.positive_news}")          # 10
print(f"Negative News: {sentiment.negative_news}")          # 2
print(f"Neutral News: {sentiment.neutral_news}")            # 3

# Access individual articles
for article in sentiment.news_articles[:3]:
    print(f"{article['title']}: {article['sentiment']} ({article['score']:.2f})")
```

**Get Trading Signal**:
```python
summary = scorer.get_sentiment_summary(sentiment)

print(f"Signal: {summary['signal']}")                # 'BUY', 'SELL', or 'HOLD'
print(f"Strength: {summary['strength']}")            # 'Strong', 'Moderate', or 'Weak'
print(f"Recommendation: {summary['recommendation']}")
# "Consider BUYING - Positive news sentiment"

# Signal thresholds:
# BUY:  score > 0.3 and sentiment == 'positive'
# SELL: score < -0.3 and sentiment == 'negative'
# HOLD: Everything else
```

**Multi-Stock Comparison**:
```python
# Compare sentiment across stocks
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
results = scorer.compare_stocks(
    symbols=stocks,
    max_news=10,
    days_back=7
)

# Results sorted by sentiment score (most positive first)
for stock_sentiment in results:
    summary = scorer.get_sentiment_summary(stock_sentiment)
    print(f"{stock_sentiment.symbol}: {summary['signal']} "
          f"({stock_sentiment.overall_score:.2f})")

# RELIANCE: BUY (0.45)
# TCS: BUY (0.32)
# INFY: HOLD (0.08)
# HDFCBANK: SELL (-0.35)
```

**Filter Stocks by Sentiment**:
```python
# Find stocks with positive sentiment
stocks = ['RELIANCE', 'TCS', 'INFY', 'WIPRO', 'SBIN']
positive_stocks = scorer.filter_by_sentiment(
    symbols=stocks,
    target_sentiment='positive',
    min_confidence=0.3
)

for stock in positive_stocks:
    print(f"{stock.symbol}: {stock.overall_score:.2f} "
          f"(confidence: {stock.confidence:.2%})")
```

#### 4. Sentiment Dashboard (`pages/07_sentiment.py`)

Interactive 3-tab sentiment dashboard:

**Tab 1 - Single Stock Analysis**:
- Input any stock symbol
- Configurable parameters (max news, time period, sentiment method)
- Display key metrics: sentiment, score, confidence, news count
- BUY/SELL/HOLD signal with recommendation
- Sentiment distribution (pie chart + bar chart)
- News feed with individual article sentiment
- Export to CSV

**Tab 2 - Multi-Stock Comparison**:
- Compare sentiment across multiple stocks
- Select from popular stocks or enter custom list
- Color-coded comparison table (green=positive, red=negative)
- Sentiment score bar chart
- Show most positive and negative stocks
- Export comparison data

**Tab 3 - Trending Stocks**:
- Find stocks with most news coverage (24 hours)
- Quick sentiment analysis for each trending stock
- Latest news preview
- Discover newsworthy stocks

**Dashboard Features**:
- Sidebar settings: max news articles, time period, sentiment method
- Real-time analysis with progress indicators
- Interactive charts (Plotly)
- CSV export for all analyses
- Responsive layout

### How to Use

**Quick Test - Single Stock**:
```bash
source venv/bin/activate

python -c "
from src.sentiment import SentimentScorer

scorer = SentimentScorer(sentiment_method='vader')
sentiment = scorer.analyze_stock('RELIANCE', max_news=10)

summary = scorer.get_sentiment_summary(sentiment)
print(f'\nRELIANCE Sentiment Analysis:')
print(f'Signal: {summary[\"signal\"]}')
print(f'Sentiment: {sentiment.overall_sentiment.upper()}')
print(f'Score: {sentiment.overall_score:.2f}')
print(f'Confidence: {sentiment.confidence:.2%}')
print(f'News Count: {sentiment.news_count}')
print(f'Recommendation: {summary[\"recommendation\"]}')
"
```

**Compare Multiple Stocks**:
```bash
python -c "
from src.sentiment import SentimentScorer

scorer = SentimentScorer()
stocks = ['RELIANCE', 'TCS', 'INFY']
results = scorer.compare_stocks(stocks, max_news=10)

print('\nSentiment Comparison:')
print('-' * 50)
for sentiment in results:
    summary = scorer.get_sentiment_summary(sentiment)
    print(f'{sentiment.symbol:10} | {summary[\"signal\"]:4} | '
          f'Score: {sentiment.overall_score:5.2f} | '
          f'News: {sentiment.news_count:2}')
"
```

**Access the Dashboard**:
```bash
# Start Streamlit app
streamlit run src/presentation/streamlit_app/app.py

# Navigate to "📰 Sentiment Analysis" page
```

### Configuration

**Sentiment Method Selection**:
- **VADER** (Recommended): Optimized for news/social media, fast, accurate for financial news
- **TextBlob**: General purpose, good baseline
- **Combined**: Averages both methods, more conservative

**Time Period Guidelines**:
- **1 day**: Breaking news, immediate events
- **3-7 days**: Short-term trading signals
- **14-30 days**: Medium-term trend analysis

**News Count Guidelines**:
- **5-10 articles**: Quick check, trending stocks
- **20 articles**: Standard analysis (recommended)
- **50 articles**: Deep dive, comprehensive view

### Testing

**Run Basic Tests**:
```bash
source venv/bin/activate

# Test news fetching
python -c "
from src.sentiment import NewsFetcher
fetcher = NewsFetcher()
news = fetcher.fetch_news('RELIANCE', max_results=5)
print(f'Fetched {len(news)} articles')
for article in news:
    print(f'- {article.title[:60]}...')
"

# Test sentiment analysis
python -c "
from src.sentiment import SentimentAnalyzer
analyzer = SentimentAnalyzer(method='vader')
text = 'Company reports record profit and strong growth'
sentiment = analyzer.analyze_text(text)
print(f'Sentiment: {sentiment.sentiment} (score: {sentiment.score:.2f})')
"

# Test trending stocks
python -c "
from src.sentiment import NewsFetcher
fetcher = NewsFetcher()
trending = fetcher.get_trending_stocks(limit=5)
for stock in trending:
    print(f\"{stock['symbol']}: {stock['news_count']} articles\")
"
```

### Files Created

```
src/sentiment/
├── __init__.py              # Module exports
├── news_fetcher.py          # News fetching (270 lines)
├── sentiment_analyzer.py    # Sentiment analysis (330 lines)
└── sentiment_scorer.py      # High-level API (280 lines)

src/presentation/streamlit_app/pages/
└── 07_sentiment.py          # Sentiment dashboard (530 lines)
```

### Dependencies

Added to `requirements.txt`:
```
vaderSentiment==3.3.2    # VADER sentiment analysis
textblob==0.17.1         # TextBlob sentiment analysis
beautifulsoup4>=4.12.3   # Web scraping for Google News
```

### Best Practices

**Combining with Technical Analysis**:
```python
from src.sentiment import SentimentScorer
from src.strategy import StrategyRunner

# 1. Check technical signal
runner = StrategyRunner()
tech_signals = runner.run_strategy('RSI', 'RELIANCE')

# 2. Check sentiment
scorer = SentimentScorer()
sentiment = scorer.analyze_stock('RELIANCE')
summary = scorer.get_sentiment_summary(sentiment)

# 3. Combine signals
if tech_signals['rsi'] < 30 and summary['signal'] == 'BUY':
    print("STRONG BUY: Oversold + Positive sentiment")
elif tech_signals['rsi'] > 70 and summary['signal'] == 'SELL':
    print("STRONG SELL: Overbought + Negative sentiment")
```

**Risk Management with Sentiment**:
- Use sentiment as **confirmation**, not sole decision factor
- Higher confidence = stronger signal reliability
- Check news count: 5+ articles for reliable sentiment
- Verify major news events manually before trading
- Combine sentiment with technical signals for best results

**Sentiment Workflow**:
1. **Morning**: Check trending stocks (Tab 3)
2. **Research**: Analyze specific stocks (Tab 1)
3. **Compare**: Multi-stock comparison (Tab 2)
4. **Combine**: Verify with technical analysis
5. **Trade**: Execute with proper risk management

### What's Next

With Phase 6 complete, your trading system now has:
- Strategy development ✅
- Backtesting ✅
- Optimization ✅
- Screening ✅
- Portfolio & Risk Management ✅
- Sentiment Analysis ✅

**Recommended Next Steps:**
1. **Phase 5 - Real-time & Alerts**: Live data and notifications
2. **Phase 7 - Machine Learning**: Predictive models for price forecasting
3. **Phase 8 - Trading Bot**: Full automation with broker integration

---

## How to Use

### Complete Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. (Optional) Start NSE data updater in background
nohup python scripts/nse_data_updater.py > logs/nse_updater.log 2>&1 &

# 3. Launch Streamlit app
streamlit run src/presentation/streamlit_app/app.py

# 4. Open browser
# http://localhost:8501
```

### Analyzing Stocks

**Dashboard (Technical Analysis)**:
1. Navigate to "Dashboard" page
2. Enter stock symbol: `RELIANCE`, `TCS`, `INFY`, etc.
3. Select date range (e.g., last 1 year)
4. Choose strategy:
   - **SMA Crossover**: Fast/slow moving averages
   - **RSI**: Oversold/overbought conditions
   - **VWAP**: Volume-weighted average price
5. Adjust strategy parameters using sliders
6. Click "🔍 Analyze"

**What You'll See**:
- Basic price metrics (latest, high, low, volume)
- **🇮🇳 NSE Market Indicators** (new!):
  - Institutional Activity (FII/DII)
  - Delivery Analysis
  - Market Status & NIFTY 50
- Candlestick chart with buy/sell signals
- Recent signals table
- Signal statistics

**Backtesting**:
1. Navigate to "Backtesting" page
2. Select stock and strategy
3. Set date range and parameters
4. Click "Run Backtest"
5. View:
   - Total return & win rate
   - Equity curve chart
   - Trade history
   - Performance metrics

### Understanding NSE Metrics

**FII/DII Interpretation**:
```
FII Net: ₹1,200 Cr (Buying) 🟢     → Foreign money flowing in (bullish)
DII Net: ₹-400 Cr (Selling) 🔴     → Domestic selling (bearish)
Total Net: ₹800 Cr                 → Overall bullish
Market Sentiment: 📈 Bullish
```

**Delivery % Interpretation**:
```
Delivery %: 72% 🟢                 → Strong genuine buying
Strength: Strong                   → Low speculation
✅ Genuine buying interest
```

```
Delivery %: 28% 🔴                 → High speculation
Strength: Weak                     → Mostly intraday
⚠️ High speculation
```

---

## Architecture Overview

### Adapter Pattern (Core Design)

**Why**: Allows swapping data sources without changing strategy code.

```
Strategy Code (SMA, RSI, etc.)
        ↓
   Uses standard interface
        ↓
  BaseDataAdapter (abstract)
        ↓
   ┌────┴────┬────────┐
   ↓         ↓        ↓
Yahoo    NSE       Upstox
Adapter  Adapter   Adapter (future)
   ↓         ↓        ↓
Yahoo    NSE      Paid API
Finance  Website  (real-time)
```

**Code Example**:

```python
# Get adapter (automatically selects best for timeframe)
adapter = AdapterFactory.get_adapter(timeframe='1d')

# All adapters return same format
data = adapter.get_historical_data(
    symbol='RELIANCE',
    start_date=start,
    end_date=end,
    timeframe='1d'
)

# Strategy works with any adapter
strategy = StrategyRegistry.get_strategy('sma_crossover')
signals = strategy.analyze(data)  # Doesn't care about source!
```

### Strategy Registry Pattern

**Why**: Auto-register strategies without manual updates.

```python
# Define strategy with decorator
@register_strategy('my_strategy')
class MyStrategy(BaseStrategy):
    def analyze(self, data):
        # Your logic here
        return signals

# Automatically available!
strategies = StrategyRegistry.list_strategies()
# ['sma_crossover', 'rsi', 'vwap', 'my_strategy']
```

### Data Flow

```
1. User Request (Streamlit UI)
        ↓
2. Adapter Factory selects data source
        ↓
3. Yahoo/NSE Adapter fetches data
        ↓
4. Strategy analyzes → generates signals
        ↓
5. Backtesting Engine (optional)
        ↓
6. Results displayed in UI
```

---

## Project Structure

```
finance/
├── .env                    # Environment configuration
├── .gitignore
├── README.md
├── QUICKSTART.md
├── PROJECT_GUIDE.md        # This file
├── INDIAN_MARKET_ANALYSIS_ROADMAP.md  # Full 3-phase roadmap
│
├── requirements.txt        # Python dependencies
├── setup.sh               # Automated setup script
├── test_setup.py          # Setup validation
│
├── config.py              # Central configuration
│
├── database/
│   └── schema.sql         # PostgreSQL schema
│
├── scripts/
│   ├── setup_db.py                # Database initialization
│   ├── seed_nifty50.py            # Seed NIFTY 50 stocks
│   ├── nse_data_updater.py        # NSE daily updater
│   └── NSE_UPDATER_README.md
│
├── src/
│   ├── data/
│   │   ├── adapters/      # Data source abstraction
│   │   ├── models/        # Database models
│   │   └── providers/     # Data providers (NSE scraper)
│   │
│   ├── strategies/
│   │   ├── base.py
│   │   ├── registry.py
│   │   └── technical/     # Technical strategies
│   │
│   ├── backtesting/
│   │   └── engine.py
│   │
│   ├── presentation/
│   │   └── streamlit_app/
│   │       ├── app.py
│   │       └── pages/
│   │           ├── 01_dashboard.py
│   │           └── 03_backtesting.py
│   │
│   └── utils/
│       ├── database.py
│       ├── logger.py
│       ├── constants.py
│       └── validators.py
│
├── logs/                  # Application logs
└── venv/                  # Virtual environment
```

---

## Phase 2.2 - Additional Strategies (Completed)

Expanded the strategy library from 3 to **8 professional-grade technical indicators**.

### New Strategies Implemented

#### 1. MACD (Moving Average Convergence Divergence)
**File**: `src/strategies/technical/macd_strategy.py`

- **Type**: Trend-following momentum indicator
- **Parameters**:
  - `fast_period`: Fast EMA period (default: 12)
  - `slow_period`: Slow EMA period (default: 26)
  - `signal_period`: Signal line period (default: 9)
  - `min_histogram`: Minimum histogram for signal validation
- **Signals**:
  - **BUY**: MACD line crosses above signal line (bullish crossover)
  - **SELL**: MACD line crosses below signal line (bearish crossover)
- **Confidence Calculation**: Based on histogram strength, trend confirmation, and crossover gap

#### 2. Bollinger Bands
**File**: `src/strategies/technical/bollinger_bands_strategy.py`

- **Type**: Volatility-based mean reversion
- **Parameters**:
  - `period`: Moving average period (default: 20)
  - `std_dev`: Standard deviation multiplier (default: 2.0)
  - `oversold_threshold`: Distance from lower band for BUY (default: 0.02)
  - `overbought_threshold`: Distance from upper band for SELL (default: 0.02)
- **Signals**:
  - **BUY**: Price touches/crosses below lower band (oversold)
  - **SELL**: Price touches/crosses above upper band (overbought)
- **Advanced Features**: Calculates %B (position within bands) and bandwidth (volatility measure)

#### 3. Stochastic Oscillator
**File**: `src/strategies/technical/stochastic_strategy.py`

- **Type**: Momentum oscillator for overbought/oversold conditions
- **Parameters**:
  - `k_period`: %K period (default: 14)
  - `d_period`: %D signal line period (default: 3)
  - `oversold_level`: Oversold threshold (default: 20)
  - `overbought_level`: Overbought threshold (default: 80)
- **Signals**:
  - **BUY**: %K crosses above %D in oversold zone (< 20)
  - **SELL**: %K crosses below %D in overbought zone (> 80)
- **Formula**: %K = (Close - Lowest Low) / (Highest High - Lowest Low) × 100

#### 4. Supertrend
**File**: `src/strategies/technical/supertrend_strategy.py`

- **Type**: ATR-based trend following with dynamic support/resistance
- **Parameters**:
  - `period`: ATR period (default: 10)
  - `multiplier`: ATR multiplier for bands (default: 3.0)
- **Signals**:
  - **BUY**: Price crosses above Supertrend line (trend changes bullish)
  - **SELL**: Price crosses below Supertrend line (trend changes bearish)
- **Characteristics**: Generates fewer but higher-quality signals, follows strong trends

#### 5. ADX (Average Directional Index)
**File**: `src/strategies/technical/adx_strategy.py`

- **Type**: Trend strength indicator with directional components
- **Parameters**:
  - `period`: Period for DI and ADX calculation (default: 14)
  - `adx_threshold`: Minimum ADX for signal validation (default: 25)
- **Signals**:
  - **BUY**: +DI crosses above -DI with ADX > threshold (strong bullish trend)
  - **SELL**: -DI crosses above +DI with ADX > threshold (strong bearish trend)
- **Components**: +DI (bullish movement), -DI (bearish movement), ADX (trend strength)

### Strategy Integration

All strategies automatically integrate with:
- ✅ **Dashboard UI** - Accessible via dropdown with parameter controls
- ✅ **Backtesting Engine** - Full performance testing
- ✅ **Parameter Optimization** - Automatic parameter tuning
- ✅ **Strategy Comparison** - Side-by-side performance analysis
- ✅ **Registry System** - Auto-discovery via `@register_strategy` decorator

### Usage Example

```python
from src.strategies.technical import MACDStrategy, BollingerBandsStrategy
import yfinance as yf

# Fetch data
data = yf.Ticker("RELIANCE.NS").history(period="1y")
data.columns = data.columns.str.lower()

# Use MACD strategy
macd = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
signals = macd.analyze(data)

# Use Bollinger Bands
bb = BollingerBandsStrategy(period=20, std_dev=2.0)
signals = bb.analyze(data)
```

### Complete Strategy List

Now have **8 strategies** available:

1. **SMA Crossover** - Simple moving average crossover (Phase 1)
2. **RSI** - Relative Strength Index (Phase 1)
3. **VWAP** - Volume Weighted Average Price (Phase 1)
4. **MACD** - Moving Average Convergence Divergence (Phase 2.2) ⭐ NEW
5. **Bollinger Bands** - Volatility-based mean reversion (Phase 2.2) ⭐ NEW
6. **Stochastic Oscillator** - Momentum indicator (Phase 2.2) ⭐ NEW
7. **Supertrend** - ATR-based trend following (Phase 2.2) ⭐ NEW
8. **ADX** - Average Directional Index (Phase 2.2) ⭐ NEW

---

## Phase 2.3 - Optimization & Testing (Completed)

Added professional-grade optimization, comparison, and risk analysis tools.

### 1. Parameter Optimization Engine

**File**: `src/backtesting/optimizer.py`

#### Grid Search Optimization

Automatically finds the best parameter combinations for any strategy:

```python
from src.backtesting.optimizer import ParameterOptimizer
from src.strategies.technical import RSIStrategy

# Define parameter ranges to test
param_ranges = {
    'period': [10, 14, 20],
    'oversold': [25, 30, 35],
    'overbought': [65, 70, 75]
}

# Run optimization
optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=historical_data,
    initial_capital=100000,
    optimization_metric='total_return_pct'  # or 'sharpe_ratio', 'win_rate', etc.
)

results = optimizer.optimize(param_ranges, min_trades=5)

# Get best parameters
best_params = optimizer.get_best_params()[0]
print(f"Best parameters: {best_params}")

# Get all results as DataFrame
df = optimizer.get_results_dataframe()
```

**Features**:
- Tests all parameter combinations (grid search)
- Supports multiple optimization metrics:
  - `total_return_pct` - Maximize returns
  - `sharpe_ratio` - Best risk-adjusted returns
  - `sortino_ratio` - Downside risk-adjusted returns
  - `profit_factor` - Gross profit / gross loss
  - `win_rate` - Percentage of winning trades
- Filters results by minimum trade count
- Returns ranked results with full metrics
- Progress tracking for large parameter spaces

**Real Example**:
```
RSI Strategy on RELIANCE (2 years):
- Default parameters (14, 30, 70): 6.18% return
- Optimized parameters (10, 35, 75): 37.16% return
- Improvement: 6x better performance!
```

#### Walk-Forward Analysis

Validates strategy robustness using out-of-sample testing:

```python
from src.backtesting.optimizer import WalkForwardOptimizer

# Initialize walk-forward optimizer
wf_optimizer = WalkForwardOptimizer(
    strategy_class=RSIStrategy,
    data=historical_data,
    train_size=252,  # 1 year training window
    test_size=63     # 3 months test window
)

# Run walk-forward analysis
results = wf_optimizer.run_walk_forward(param_ranges)

# Get summary
summary = wf_optimizer.get_summary()
print(f"Average test return: {summary['avg_test_return']:.2f}%")
print(f"Consistency score: {summary['consistency_score']:.2f}")
```

**Features**:
- Rolling window optimization
- In-sample (training) and out-of-sample (testing) periods
- Prevents overfitting
- Measures consistency across periods
- Calculates correlation between train and test performance

### 2. Strategy Comparator

**File**: `src/backtesting/comparator.py`

Compare multiple strategies on the same dataset:

```python
from src.backtesting.comparator import StrategyComparator
from src.strategies.technical import RSIStrategy, MACDStrategy, BollingerBandsStrategy

# Create comparator
comparator = StrategyComparator(data=historical_data, initial_capital=100000)

# Add strategies
comparator.add_strategy(RSIStrategy())
comparator.add_strategy(MACDStrategy())
comparator.add_strategy(BollingerBandsStrategy())

# Get comparison table
table = comparator.get_comparison_table()
print(table)

# Get rankings
rankings = comparator.get_rankings('total_return_pct')

# Get best strategy
best = comparator.get_best_strategy('sharpe_ratio')

# Get combined equity curves
curves = comparator.get_combined_equity_curve()
```

**Features**:
- Side-by-side performance comparison
- Rank by any metric
- Combined equity curve visualization
- Detailed statistics for each strategy
- Winner summary with best/worst performers
- Export to CSV

**Example Output**:
```
Strategy Comparison on RELIANCE (2 years):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 Bollinger Bands: 23.30% return, 80% win rate
🥈 SMA Crossover: 7.85% return, 33% win rate
🥉 RSI: 6.18% return, 57% win rate
   MACD: 0.08% return, 23% win rate
```

### 3. Advanced Risk Metrics

**Enhanced File**: `src/backtesting/engine.py`

Added professional risk-adjusted performance metrics:

#### Sharpe Ratio
```
Sharpe Ratio = (Average Return / Standard Deviation) × √252
```
- Measures risk-adjusted returns
- Higher is better (> 1.0 is good, > 2.0 is excellent)
- Accounts for volatility of returns

#### Sortino Ratio
```
Sortino Ratio = (Average Return / Downside Deviation) × √252
```
- Like Sharpe but only penalizes downside volatility
- Better for strategies with asymmetric returns
- Higher values indicate better downside risk management

#### Maximum Drawdown
```
Max Drawdown = Max((Peak - Trough) / Peak) × 100
```
- Largest peak-to-trough decline in portfolio value
- Lower is better
- Key risk metric for portfolio management

#### Calmar Ratio
```
Calmar Ratio = Annualized Return / Max Drawdown
```
- Return per unit of maximum drawdown
- Higher is better (> 1.0 is good)
- Balances returns against worst-case losses

**All metrics automatically calculated** in every backtest and included in results.

### 4. New Dashboard Page: Optimization

**File**: `src/presentation/streamlit_app/pages/04_optimization.py`

Brand new Streamlit page with two powerful tabs:

#### Tab 1: Strategy Comparison 📊

**Features**:
- Select multiple strategies to compare
- Configure stock symbol and date range
- View comparison summary with key statistics
- Detailed performance metrics table with formatting
- Combined equity curves chart (Plotly visualization)
- Rankings by return, win rate, and profit factor
- Medal system (🥇🥈🥉) for top 3 performers

**How to Use**:
1. Navigate to "Optimization" page in Streamlit
2. Select 2+ strategies from multiselect
3. Choose stock and date range
4. Click "Compare Strategies"
5. View results: summary, table, equity curves, rankings

#### Tab 2: Parameter Optimization 🔧

**Features**:
- Select strategy to optimize
- Define parameter ranges with multiselect controls
- Choose optimization metric (return, Sharpe, win rate, etc.)
- Shows total combinations to be tested
- Displays best parameters prominently
- Top 10 results table
- Optimization summary statistics

**Supported Strategies**:
- RSI: period, oversold, overbought levels
- MACD: fast, slow, signal periods
- SMA Crossover: fast and slow periods
- Bollinger Bands: period and standard deviation
- Others use default parameters

**How to Use**:
1. Go to "Optimization" tab
2. Select strategy (e.g., RSI)
3. Choose parameter ranges (e.g., period: [10, 14, 20])
4. Select optimization metric
5. Click "Run Optimization"
6. View best parameters and top 10 results

### Key Benefits

✅ **No More Guessing** - Automatically find optimal parameters
✅ **Objective Comparison** - Compare strategies with same data
✅ **Risk Assessment** - Advanced metrics beyond just returns
✅ **Robustness Testing** - Walk-forward validation
✅ **Professional Grade** - Industry-standard metrics and methods
✅ **Beautiful UI** - Professional charts and tables in Streamlit

### Testing Example

```bash
# Test parameter optimization
python -c "
from src.backtesting.optimizer import ParameterOptimizer
from src.strategies.technical import RSIStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=data,
    optimization_metric='sharpe_ratio'
)

results = optimizer.optimize({
    'period': [10, 14, 20],
    'oversold': [25, 30, 35],
    'overbought': [65, 70, 75]
})

print(f'Best: {results[0].params}')
print(f'Sharpe: {results[0].metrics[\"sharpe_ratio\"]:.2f}')
"
```

---

## Testing & Optimization Guide

### Quick Start: Testing Strategies

#### 1. Basic Backtesting

Test a single strategy on historical data:

```python
from src.backtesting.engine import BacktestEngine
from src.strategies.technical import RSIStrategy
import yfinance as yf

# Fetch data
data = yf.Ticker("RELIANCE.NS").history(period="1y")
data.columns = data.columns.str.lower()

# Create strategy
strategy = RSIStrategy(period=14, oversold=30, overbought=70)

# Run backtest
engine = BacktestEngine(initial_capital=100000)
results = engine.run(data, strategy)

# View results
print(f"Total Return: {results['total_return_pct']}%")
print(f"Win Rate: {results['win_rate']}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']}")
print(f"Max Drawdown: {results['max_drawdown']}%")
```

#### 2. Parameter Optimization

Find the best parameters for a strategy:

```python
from src.backtesting.optimizer import ParameterOptimizer

# Define what to test
param_ranges = {
    'period': [10, 12, 14, 16, 20],
    'oversold': [20, 25, 30, 35],
    'overbought': [65, 70, 75, 80]
}

# Run optimization
optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=data,
    optimization_metric='sharpe_ratio'  # Optimize for risk-adjusted returns
)

results = optimizer.optimize(param_ranges, min_trades=10)

# Get best parameters
best = results[0]
print(f"Optimal parameters: {best.params}")
print(f"Expected Sharpe Ratio: {best.metrics['sharpe_ratio']:.2f}")
print(f"Expected Return: {best.metrics['total_return_pct']:.2f}%")
```

#### 3. Strategy Comparison

Compare multiple strategies to find the best:

```python
from src.backtesting.comparator import StrategyComparator

# Create comparator
comparator = StrategyComparator(data=data, initial_capital=100000)

# Add all your strategies
comparator.add_strategy(RSIStrategy())
comparator.add_strategy(MACDStrategy())
comparator.add_strategy(BollingerBandsStrategy())
comparator.add_strategy(SupertrendStrategy())

# View comparison
print(comparator.get_winner_summary())

# Get detailed table
table = comparator.get_comparison_table()
print(table)

# Get best for specific metric
best_sharpe = comparator.get_best_strategy('sharpe_ratio')
best_return = comparator.get_best_strategy('total_return_pct')
```

### Using the Streamlit UI

#### Strategy Comparison (Tab 1)

**Step-by-Step**:

1. **Open Application**
   ```bash
   streamlit run src/presentation/streamlit_app/app.py
   ```

2. **Navigate to Optimization Page**
   - Click "Optimization" in sidebar

3. **Configure Comparison**
   - In sidebar:
     - Enter stock symbol (e.g., "RELIANCE")
     - Select date range (recommended: 2 years)
     - Set initial capital (e.g., ₹1,00,000)
     - Select 2+ strategies to compare

4. **Run Comparison**
   - Click "🔍 Compare Strategies"
   - Wait for analysis to complete

5. **Analyze Results**
   - **Summary Metrics**: Best strategy, average return, total compared
   - **Performance Table**: Sortable table with all metrics
   - **Equity Curves**: Visual comparison of portfolio growth
   - **Rankings**: Top performers by different metrics

**Tips**:
- Compare similar strategy types (e.g., all trend-following)
- Use 2+ years of data for reliability
- Check multiple metrics, not just return
- Look for consistent performers across metrics

#### Parameter Optimization (Tab 2)

**Step-by-Step**:

1. **Select Strategy**
   - Choose strategy to optimize (e.g., RSI)

2. **Define Parameter Ranges**
   - Select values to test for each parameter
   - Example for RSI:
     - Period: [10, 14, 20]
     - Oversold: [25, 30, 35]
     - Overbought: [65, 70, 75]
   - Total combinations shown

3. **Choose Optimization Metric**
   - `total_return_pct`: Maximum returns
   - `sharpe_ratio`: Best risk-adjusted returns (recommended)
   - `sortino_ratio`: Best downside risk-adjusted
   - `win_rate`: Highest win percentage
   - `profit_factor`: Best profit/loss ratio

4. **Run Optimization**
   - Click "🚀 Run Optimization"
   - Progress shown during execution

5. **Review Results**
   - **Best Parameters**: Optimal settings highlighted
   - **Performance**: Key metrics for best combination
   - **Top 10 Table**: Best parameter combinations
   - **Summary Stats**: Average, best, worst scores

**Tips**:
- Start with smaller parameter ranges (faster)
- Use at least 2 years of data
- Optimize for Sharpe ratio (balances return and risk)
- Test top 3 results, not just #1 (avoid overfitting)
- Verify results with walk-forward analysis

### Interpreting Metrics

#### Return Metrics
- **Total Return %**: Overall profit/loss
  - Good: > 15% per year
  - Excellent: > 25% per year
- **Win Rate %**: Percentage of profitable trades
  - Good: > 50%
  - Excellent: > 60%

#### Risk Metrics
- **Sharpe Ratio**: Risk-adjusted returns
  - < 1.0: Poor
  - 1.0-2.0: Good
  - \> 2.0: Excellent
- **Sortino Ratio**: Downside risk-adjusted
  - Higher than Sharpe = good downside protection
  - Look for > 1.5
- **Max Drawdown %**: Largest loss from peak
  - Good: < 15%
  - Acceptable: 15-25%
  - Concerning: > 25%
- **Calmar Ratio**: Return / Max Drawdown
  - > 0.5: Good
  - \> 1.0: Excellent

#### Trade Metrics
- **Profit Factor**: Gross profit / Gross loss
  - < 1.0: Losing strategy
  - 1.0-1.5: Breakeven to marginal
  - 1.5-2.0: Good
  - \> 2.0: Excellent
- **Avg Profit/Loss**: Average win vs average loss
  - Avg Profit should be > Avg Loss
  - Ratio > 2:1 is good

### Best Practices

#### 1. Parameter Optimization
- ✅ Use 2+ years of historical data
- ✅ Test reasonable parameter ranges only
- ✅ Optimize for Sharpe ratio, not just return
- ✅ Require minimum trade count (5-10)
- ✅ Test top 3 results, not just #1
- ❌ Don't overfit (too many parameters)
- ❌ Don't use only recent data
- ❌ Don't ignore risk metrics

#### 2. Strategy Comparison
- ✅ Use same data period for all strategies
- ✅ Compare similar strategy types
- ✅ Look at multiple metrics
- ✅ Check equity curves for consistency
- ❌ Don't just pick highest return
- ❌ Don't ignore drawdowns
- ❌ Don't compare on different time periods

#### 3. Validation
- ✅ Use walk-forward analysis
- ✅ Test on out-of-sample data
- ✅ Verify across different stocks
- ✅ Check consistency across time periods
- ❌ Don't assume past = future
- ❌ Don't over-optimize (curve fitting)

### Common Workflows

#### Workflow 1: Find Best Strategy for a Stock

```python
# 1. Fetch data
data = yf.Ticker("RELIANCE.NS").history(period="2y")
data.columns = data.columns.str.lower()

# 2. Compare all strategies
comparator = StrategyComparator(data=data)
comparator.add_strategy(RSIStrategy())
comparator.add_strategy(MACDStrategy())
comparator.add_strategy(BollingerBandsStrategy())
comparator.add_strategy(SupertrendStrategy())
comparator.add_strategy(ADXStrategy())

# 3. Get best strategy
best = comparator.get_best_strategy('sharpe_ratio')
print(f"Winner: {best.strategy_name}")

# 4. Optimize best strategy's parameters
optimizer = ParameterOptimizer(
    strategy_class=type(best.strategy),
    data=data,
    optimization_metric='sharpe_ratio'
)
# ... define param_ranges and optimize
```

#### Workflow 2: Optimize and Validate

```python
# 1. Split data
train_data = data[:'2024']
test_data = data['2024':]

# 2. Optimize on training data
optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=train_data,
    optimization_metric='sharpe_ratio'
)
results = optimizer.optimize(param_ranges)
best_params = results[0].params

# 3. Test on out-of-sample data
strategy = RSIStrategy(**best_params)
engine = BacktestEngine()
test_results = engine.run(test_data, strategy)

# 4. Compare train vs test performance
print(f"Train Return: {results[0].metrics['total_return_pct']:.2f}%")
print(f"Test Return: {test_results['total_return_pct']:.2f}%")
# Test should be similar to train (within 50%)
```

#### Workflow 3: Portfolio of Strategies

```python
# Find best strategy for each stock type
stocks = {
    'trending': 'RELIANCE.NS',
    'volatile': 'TATASTEEL.NS',
    'stable': 'TCS.NS'
}

best_strategies = {}

for stock_type, symbol in stocks.items():
    data = yf.Ticker(symbol).history(period='2y')
    data.columns = data.columns.str.lower()

    comparator = StrategyComparator(data=data)
    # ... add strategies

    best = comparator.get_best_strategy('sharpe_ratio')
    best_strategies[stock_type] = best.strategy_name

print(best_strategies)
# Example: {'trending': 'Supertrend', 'volatile': 'BollingerBands', 'stable': 'SMAcrossover'}
```

### Troubleshooting

**Problem**: "No valid results" in optimization
**Solution**: Reduce `min_trades` parameter or expand date range

**Problem**: All strategies show similar performance
**Solution**: Use longer time period or more volatile stock

**Problem**: Optimized parameters fail on new data
**Solution**: You've overfit. Use walk-forward analysis or simpler parameter ranges

**Problem**: High return but terrible Sharpe ratio
**Solution**: Strategy is risky. Consider max drawdown and use risk-adjusted metrics

---

## Phase 3 - Stock Screener (Completed)

Multi-stock, multi-strategy screener to find trading opportunities across the entire market.

### Overview

The Stock Screener scans multiple stocks with multiple strategies simultaneously to identify trading opportunities. Instead of manually checking each stock individually, you can now scan all NIFTY 50 stocks (or any custom list) in seconds and get a prioritized list of signals.

**Key Concept**: Leverage your 8 strategies across 50 stocks = 400 potential signal combinations analyzed instantly!

### 1. Screener Engine

**File**: `src/screener/engine.py`

Core engine that handles multi-stock scanning with filtering and aggregation capabilities.

#### Features

- **Multi-Stock Scanning**: Scan any number of stocks simultaneously
- **Multi-Strategy Analysis**: Use all 8 strategies or select specific ones
- **Smart Filtering**: Filter by signal type, confidence level, strategy
- **Result Aggregation**: Combine and rank all signals
- **Export Functionality**: Save results to CSV
- **Grouping**: View signals by stock or by strategy
- **Summary Statistics**: Overall metrics and top signals

#### Basic Usage

```python
from src.screener import StockScreener
import src.strategies.technical

# Create screener
screener = StockScreener(
    lookback_days=365,      # Use 1 year of data
    min_confidence=50       # Only signals > 50% confidence
)

# Scan stocks
results = screener.scan(
    stock_symbols=['RELIANCE', 'TCS', 'INFY', 'HDFCBANK'],
    strategy_names=None,    # Use all strategies (or specify list)
    signal_types=['BUY', 'SELL']  # Both BUY and SELL signals
)

print(f"Found {len(results)} signals")

# Get top signals
top_10_buys = screener.get_top_signals(10, 'BUY')
top_10_sells = screener.get_top_signals(10, 'SELL')

# Export to CSV
screener.export_to_csv('screener_results.csv')
```

#### Advanced Features

**Filter Results**:
```python
# Filter by multiple criteria
high_confidence_buys = screener.filter_results(
    min_confidence=70,
    signal_types=['BUY'],
    strategy_names=['macd', 'supertrend']
)
```

**Group by Stock**:
```python
# See all signals for each stock
signals_by_stock = screener.get_signals_by_stock()

for symbol, signals in signals_by_stock.items():
    print(f"{symbol}: {len(signals)} signals")
    for sig in signals:
        print(f"  - {sig.strategy_name}: {sig.signal_type} ({sig.confidence:.1f}%)")
```

**Group by Strategy**:
```python
# See which strategies are most active
signals_by_strategy = screener.get_signals_by_strategy()

for strategy, signals in signals_by_strategy.items():
    buy_count = len([s for s in signals if s.signal_type == 'BUY'])
    sell_count = len([s for s in signals if s.signal_type == 'SELL'])
    print(f"{strategy}: {len(signals)} signals (BUY: {buy_count}, SELL: {sell_count})")
```

**Get Summary**:
```python
summary = screener.get_summary()

print(f"Total Signals: {summary['total_signals']}")
print(f"BUY: {summary['buy_signals']}, SELL: {summary['sell_signals']}")
print(f"Stocks Scanned: {summary['stocks_scanned']}")
print(f"Avg Confidence: {summary['avg_confidence']}%")
print(f"Top BUY: {summary['top_buy']}")
print(f"Top SELL: {summary['top_sell']}")
```

### 2. Screener Dashboard

**File**: `src/presentation/streamlit_app/pages/05_screener.py`

Beautiful Streamlit interface for the stock screener with filtering, visualization, and export.

#### Stock Selection Methods

**1. NIFTY 50** (Recommended):
- Scans all 50 NIFTY stocks
- Pre-loaded list, just click and scan
- Best for comprehensive market overview

**2. Popular Stocks**:
- Pre-selected top 10 most traded stocks
- Faster scans
- Good for quick daily checks

**3. Custom List**:
- Enter your own stock symbols
- One symbol per line
- Useful for specific watchlists

#### Dashboard Features

**Configuration Panel** (Sidebar):
- Stock selection (NIFTY 50, Popular, Custom)
- Strategy selection (all or specific)
- Signal type filter (BUY, SELL, or both)
- Minimum confidence slider (0-100%)
- Lookback period (6 months, 1 year, 2 years)

**Results Display**:
- **Summary Cards**: Total signals, BUY/SELL counts, average confidence
- **Results Table**: Color-coded table (green=BUY, red=SELL) with sorting
- **Top Signals**: Top 5 BUY and SELL signals with medal rankings 🥇🥈🥉
- **Charts**:
  - Signals by Strategy (bar chart)
  - Signal Distribution (pie chart)
  - Most Active Stocks (bar chart)

**Export**:
- Download results as CSV with timestamp
- Includes all signal details and metadata

#### How to Use

**Step-by-Step**:

1. **Open Streamlit App**:
   ```bash
   streamlit run src/presentation/streamlit_app/app.py
   ```

2. **Navigate to "Screener" Page** in sidebar

3. **Configure Settings**:
   - Choose stock selection method (NIFTY 50 recommended for first scan)
   - Select strategies to use (default: all 8 strategies)
   - Set minimum confidence (50-60% is good starting point)
   - Choose signal types (both BUY and SELL recommended)

4. **Click "Scan Stocks"** button

5. **Wait for Results** (usually 10-30 seconds for NIFTY 50)

6. **Analyze Results**:
   - Check summary metrics at top
   - Browse results table (click column headers to sort)
   - Review top signals on both sides
   - Examine charts for patterns
   - Download CSV for offline analysis

#### Interpreting Results

**Summary Metrics**:
- **Total Signals**: Number of opportunities found
- **BUY Signals**: Bullish opportunities
- **SELL Signals**: Bearish opportunities
- **Avg Confidence**: Overall signal quality

**Results Table**:
- **Green rows**: BUY signals (potential long opportunities)
- **Red rows**: SELL signals (potential short/exit opportunities)
- **Confidence**: Higher is better (>70% is strong, >80% is very strong)
- **Strategy**: Which indicator generated the signal
- **Date**: When signal was generated (most recent data)

**Top Signals**:
- **🥇🥈🥉 Rankings**: Best opportunities by confidence
- **Multiple Signals on Same Stock**: Higher conviction (multiple strategies agree)
- **High Confidence + Recent Date**: Most actionable signals

**Charts**:
- **Signals by Strategy**: See which indicators are most active currently
- **Signal Distribution**: Market sentiment (more BUY = bullish, more SELL = bearish)
- **Most Active Stocks**: Stocks with most technical activity

### Real-World Examples

#### Example 1: Daily Market Scan

```python
from src.screener import StockScreener
import src.strategies.technical

# Morning routine: Scan NIFTY 50 for BUY opportunities
screener = StockScreener(lookback_days=365, min_confidence=65)

nifty50 = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', ...]  # All 50

results = screener.scan(
    stock_symbols=nifty50,
    strategy_names=None,  # All strategies
    signal_types=['BUY']  # Only BUY signals today
)

# Get actionable list
top_opportunities = screener.get_top_signals(10, 'BUY')

print("Today's Top 10 Trading Opportunities:")
for i, signal in enumerate(top_opportunities, 1):
    print(f"{i}. {signal.stock_symbol} via {signal.strategy_name}")
    print(f"   Entry: ₹{signal.price:,.2f}")
    print(f"   Confidence: {signal.confidence:.1f}%")
    print()
```

#### Example 2: Strategy-Specific Screening

```python
# Find stocks where Supertrend is bullish
screener = StockScreener(min_confidence=60)

results = screener.scan(
    stock_symbols=nifty50,
    strategy_names=['supertrend'],  # Only Supertrend
    signal_types=['BUY']
)

print(f"Supertrend BUY signals: {len(results)}")

# Supertrend generates fewer but higher-quality signals
# Good for trend-following entries
```

#### Example 3: High-Conviction Multi-Strategy Signals

```python
# Find stocks with signals from multiple strategies
screener = StockScreener(min_confidence=60)

results = screener.scan(nifty50, strategy_names=None, signal_types=['BUY'])

# Group by stock
by_stock = screener.get_signals_by_stock()

# Find stocks with 3+ strategies agreeing
high_conviction = {
    symbol: signals
    for symbol, signals in by_stock.items()
    if len(signals) >= 3
}

print(f"High Conviction Stocks (3+ strategies agree):")
for symbol, signals in high_conviction.items():
    strategies = [s.strategy_name for s in signals]
    avg_conf = sum(s.confidence for s in signals) / len(signals)
    print(f"{symbol}: {strategies}")
    print(f"  Avg Confidence: {avg_conf:.1f}%")
```

### Performance & Scalability

**Scan Times** (approximate):
- 10 stocks × 8 strategies = 80 combinations → 10-15 seconds
- 50 stocks × 8 strategies = 400 combinations → 30-45 seconds
- Custom 5 stocks × 3 strategies = 15 combinations → 5-8 seconds

**Optimization Tips**:
- Use shorter lookback period (180 days) for faster scans
- Select specific strategies instead of all 8
- Scan during non-market hours for better data availability
- Start with Popular Stocks for quick tests

### Best Practices

**Daily Workflow**:
1. **Morning Scan** (before market open):
   - Scan NIFTY 50 with all strategies
   - Focus on BUY signals > 65% confidence
   - Create watchlist from top 10

2. **Mid-Day Check**:
   - Scan watchlist only
   - Check for new signals or changes
   - Look for SELL signals on existing positions

3. **Evening Review**:
   - Full NIFTY 50 scan
   - Export results for record-keeping
   - Note patterns in active strategies

**Signal Quality**:
- **>80% confidence**: Very strong, high priority
- **70-80%**: Strong, worth researching
- **60-70%**: Moderate, need confirmation
- **50-60%**: Weak, watch for other signals
- **<50%**: Filter out (too low quality)

**Multiple Signals**:
- **Same stock, multiple strategies**: Higher conviction
- **Same strategy, multiple stocks**: Strategy is active
- **BUY + SELL on same stock**: Market indecision, wait

**Strategy Insights**:
- **Bollinger Bands active**: Volatile market, mean reversion opportunities
- **Supertrend active**: Strong trending market
- **RSI/Stochastic active**: Ranging market, overbought/oversold
- **MACD active**: Trend changes occurring

### Exporting & Integration

**CSV Export**:
```python
# Save to timestamped file
from datetime import datetime

filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
screener.export_to_csv(filename)

# CSV includes: stock, strategy, signal, price, confidence, date, metadata
```

**Integration with Other Tools**:
```python
# Convert to DataFrame for analysis
df = screener.get_results_dataframe()

# Filter and manipulate
high_quality = df[df['confidence'] > 75]
by_stock = df.groupby('stock_symbol')['confidence'].mean()

# Merge with other data sources
# ... your custom analysis
```

---

## Stock Screener Guide

### Quick Start: Finding Opportunities

#### Step 1: Run Your First Scan

**Via Streamlit** (Easiest):
```bash
streamlit run src/presentation/streamlit_app/app.py
# Navigate to "Screener" page
# Select "Popular Stocks"
# Click "Scan Stocks"
```

**Via Python** (Programmatic):
```python
from src.screener import StockScreener
import src.strategies.technical

screener = StockScreener(min_confidence=60)
results = screener.scan(
    stock_symbols=['RELIANCE', 'TCS', 'INFY'],
    strategy_names=None,
    signal_types=['BUY']
)

for r in screener.get_top_signals(5, 'BUY'):
    print(f"{r.stock_symbol}: {r.confidence:.1f}%")
```

#### Step 2: Understanding Results

**Green (BUY) Signals**:
- Potential entry opportunities
- Strategy thinks stock will go up
- Check confidence level and strategy type

**Red (SELL) Signals**:
- Potential exit or short opportunities
- Strategy thinks stock will go down
- Good for existing position management

**Confidence Levels**:
- 80-100%: Very strong signal, high priority
- 70-80%: Strong signal, good opportunity
- 60-70%: Moderate signal, research needed
- 50-60%: Weak signal, need confirmation

#### Step 3: Taking Action

1. **Review Top Signals**: Start with top 5 by confidence
2. **Check Multiple Strategies**: Look for agreement
3. **Verify Fundamentals**: Do basic research on stock
4. **Set Alerts**: Monitor selected stocks
5. **Plan Entry**: Determine entry price and stop-loss

### Common Workflows

#### Workflow 1: Find Today's Best Opportunities

```python
# Scan NIFTY 50 for high-confidence BUY signals
screener = StockScreener(lookback_days=365, min_confidence=70)

results = screener.scan(
    stock_symbols=NIFTY_50_LIST,
    strategy_names=None,
    signal_types=['BUY']
)

# Get top 10
top10 = screener.get_top_signals(10, 'BUY')

# Look for multi-strategy confirmation
by_stock = screener.get_signals_by_stock()
for symbol, signals in by_stock.items():
    if len(signals) >= 2:  # 2+ strategies agree
        print(f"{symbol}: {len(signals)} strategies")
```

#### Workflow 2: Strategy-Specific Screening

```python
# Find stocks in strong trends (Supertrend)
trend_screener = StockScreener()
trend_results = trend_screener.scan(
    stock_symbols=NIFTY_50_LIST,
    strategy_names=['supertrend'],
    signal_types=['BUY']
)

# Find mean-reversion opportunities (Bollinger Bands)
mean_rev_screener = StockScreener()
mean_rev_results = mean_rev_screener.scan(
    stock_symbols=NIFTY_50_LIST,
    strategy_names=['bollinger_bands'],
    signal_types=['BUY']
)

# Compare strategies
print(f"Trend following: {len(trend_results)} signals")
print(f"Mean reversion: {len(mean_rev_results)} signals")
```

#### Workflow 3: Watchlist Monitoring

```python
# Monitor specific watchlist
watchlist = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']

screener = StockScreener(min_confidence=50)
results = screener.scan(
    stock_symbols=watchlist,
    strategy_names=None,
    signal_types=['BUY', 'SELL']
)

# Get all signals for watchlist
for stock in watchlist:
    stock_signals = [r for r in results if r.stock_symbol == stock]
    if stock_signals:
        print(f"\n{stock}:")
        for sig in stock_signals:
            print(f"  {sig.signal_type}: {sig.strategy_name} ({sig.confidence:.1f}%)")
    else:
        print(f"\n{stock}: No signals")
```

### Tips & Tricks

**Finding Best Stocks**:
- Look for 70%+ confidence
- Prefer stocks with multiple strategy signals
- Check signal date (recent is better)
- Review strategy type (trend vs mean-reversion)

**Filtering Noise**:
- Set min_confidence to 60-70%
- Focus on 3-5 specific strategies
- Filter by signal type (BUY or SELL only)
- Look at 1-year lookback minimum

**Market Sentiment**:
- More BUY signals overall = Bullish market
- More SELL signals overall = Bearish market
- 50/50 split = Neutral/ranging market
- Track daily to see sentiment shifts

**Strategy Patterns**:
- Bollinger Bands active = High volatility
- Supertrend active = Strong trends
- MACD active = Trend reversals
- RSI/Stochastic active = Overbought/oversold

**Export & Track**:
- Export daily scans to CSV
- Track which signals worked
- Build confidence in certain strategies
- Refine your filtering over time

### Troubleshooting

**Problem**: Scan takes too long
**Solution**: Reduce lookback_days to 180, or scan fewer stocks

**Problem**: No signals found
**Solution**: Lower min_confidence, use longer lookback period, or check data availability

**Problem**: Too many signals (overwhelming)
**Solution**: Increase min_confidence to 70%, filter to specific strategies, or focus on top 10

**Problem**: Signals don't make sense
**Solution**: Check signal date (should be recent), verify stock data is current, review strategy logic

---

## Portfolio & Risk Management Guide

Complete guide to using portfolio tracking and risk management features.

---

### Quick Start

#### Create Your First Portfolio

```python
from src.portfolio import Portfolio, PositionSizer, RiskManager

# Step 1: Create portfolio
portfolio = Portfolio(
    initial_capital=100000,
    name="My Trading Portfolio"
)

# Step 2: Calculate position size
sizer = PositionSizer(capital=100000)
position_size = sizer.fixed_fractional(
    price=2847.50,
    risk_percentage=0.02,  # Risk 2% per trade
    stop_loss_pct=5.0
)

print(f"Buy {position_size.shares} shares")

# Step 3: Set risk management
risk_mgr = RiskManager()
stop = risk_mgr.fixed_stop_loss(2847.50, stop_pct=5.0)
target = risk_mgr.risk_reward_take_profit(2847.50, stop.price, 2.0)

# Step 4: Open position
position = portfolio.open_position(
    symbol='RELIANCE',
    shares=position_size.shares,
    entry_price=2847.50,
    stop_loss=stop,
    take_profit=target
)

# Step 5: Check portfolio
summary = portfolio.get_summary()
print(f"Portfolio Value: ₹{summary['current_value']:,.0f}")
print(f"Risk: ₹{summary['total_risk']:,.0f}")
```

---

### Position Sizing Guide

#### Method Selection

**When to use each method:**

| Method | Best For | Risk Profile | Complexity |
|--------|----------|--------------|------------|
| **Kelly Criterion** | Proven strategy with known win rate | Aggressive | High |
| **Fixed Fractional** | General trading | Conservative | Low |
| **Risk-Based (ATR)** | Volatile markets | Adaptive | Medium |
| **Equal Weight** | Diversification | Moderate | Low |
| **Fixed Amount** | Simple management | Fixed | Low |

#### Kelly Criterion

**Best for**: Strategies with proven win rates (from backtesting)

```python
# Get win rate from backtest
from src.backtesting.engine import BacktestEngine
from src.strategies.technical import RSIStrategy

engine = BacktestEngine()
results = engine.run(data, RSIStrategy())

win_rate = results['win_rate'] / 100
avg_win = 8.5   # Average win in %
avg_loss = 4.2  # Average loss in %

# Calculate Kelly position size
sizer = PositionSizer(capital=100000)
kelly_size = sizer.kelly_criterion(
    win_rate=win_rate,
    avg_win=avg_win,
    avg_loss=avg_loss,
    price=2847.50,
    kelly_fraction=0.25  # Quarter-Kelly for safety
)

print(f"Kelly suggests {kelly_size.shares} shares")
print(f"That's {(kelly_size.capital_allocation / 100000) * 100:.1f}% of capital")
```

**Kelly Fraction Guidelines:**
- **Full Kelly (1.0)**: Maximum growth but very aggressive
- **Half Kelly (0.5)**: Good balance
- **Quarter Kelly (0.25)**: Conservative, recommended
- **Eighth Kelly (0.125)**: Very conservative

#### Fixed Fractional

**Best for**: Most traders, simple and effective

```python
# Risk 2% of capital per trade
sizer = PositionSizer(capital=100000)
size = sizer.fixed_fractional(
    price=2847.50,
    risk_percentage=0.02,  # 2% risk
    stop_loss_pct=5.0      # 5% stop-loss
)

# If capital = ₹100,000
# Risk = ₹2,000
# Stop-loss = 5%
# Position size = ₹2,000 / 0.05 = ₹40,000
# Shares = ₹40,000 / ₹2,847.50 = 14 shares
```

**Risk Percentage Guidelines:**
- **1%**: Very conservative
- **2%**: Recommended for most traders
- **3-5%**: Aggressive
- **>5%**: Very risky

#### Risk-Based (ATR)

**Best for**: Adapting to volatility

```python
import pandas_ta as ta

# Calculate ATR from data
data['atr'] = ta.atr(data['high'], data['low'], data['close'], length=14)
current_atr = data['atr'].iloc[-1]

# Position size based on ATR
sizer = PositionSizer(capital=100000)
size = sizer.risk_based(
    price=2847.50,
    atr=current_atr,
    atr_multiplier=2.0,    # Stop = 2× ATR
    risk_percentage=0.02
)

# In volatile markets: ATR is high → smaller position
# In calm markets: ATR is low → larger position
```

---

### Risk Management Guide

#### Setting Stop-Loss

**Fixed Percentage** (Simple):
```python
risk_mgr = RiskManager()
stop = risk_mgr.fixed_stop_loss(
    entry_price=2847.50,
    stop_pct=5.0  # 5% below entry
)
# Result: ₹2705.12
```

**ATR-Based** (Volatility-adjusted):
```python
stop = risk_mgr.atr_stop_loss(
    entry_price=2847.50,
    atr=50.0,
    multiplier=2.0  # 2× ATR
)
# In volatile markets, stop is wider
# In calm markets, stop is tighter
```

**Support/Resistance** (Technical):
```python
# Find support level from chart
support = 2750.0

stop = risk_mgr.support_resistance_stop(
    entry_price=2847.50,
    support_level=support,
    buffer_pct=0.5  # 0.5% below support
)
# Gives you room for noise
```

**Trailing Stop** (Lock in profits):
```python
# As price moves up, stop follows
stop = risk_mgr.trailing_stop_loss(
    entry_price=2847.50,
    current_price=2950.00,  # Price has moved up
    trail_pct=5.0
)
# Stop moves to ₹2802.50 (5% below ₹2950)
# Locks in profit of ₹102.50 per share
```

#### Setting Take-Profit

**Fixed Percentage**:
```python
target = risk_mgr.fixed_take_profit(
    entry_price=2847.50,
    profit_pct=10.0  # 10% profit target
)
# Result: ₹3132.25
```

**Risk-Reward Ratio** (Recommended):
```python
# Risk ₹142.38, target ₹284.76 (2:1 ratio)
target = risk_mgr.risk_reward_take_profit(
    entry_price=2847.50,
    stop_loss_price=2705.12,
    risk_reward_ratio=2.0  # Aim for 2× what you risk
)
```

**Multiple Targets** (Scale out):
```python
# Take partial profits at multiple levels
targets = risk_mgr.multiple_targets(
    entry_price=2847.50,
    targets=[5, 10, 15]  # 5%, 10%, 15%
)

# Exit strategy:
# - 33% at +5% (quick profit)
# - 33% at +10% (main target)
# - 33% at +15% (let winners run)
```

---

### Portfolio Management Guide

#### Daily Workflow

**Morning Routine**:
```python
# 1. Check portfolio status
summary = portfolio.get_summary()
print(f"Portfolio Value: ₹{summary['current_value']:,.0f}")
print(f"Today's P&L: Check manually or add tracking")

# 2. Check if stops/targets hit
alerts = portfolio.check_stops_and_targets()

if alerts['stop_loss_hit']:
    for symbol in alerts['stop_loss_hit']:
        print(f"STOP-LOSS: Close {symbol}")
        # portfolio.close_position(symbol, current_price)

if alerts['take_profit_hit']:
    for symbol in alerts['take_profit_hit']:
        print(f"TAKE-PROFIT: Close {symbol}")

# 3. Check risk exposure
risk = portfolio.get_risk_exposure()
if risk['total_risk_pct'] > 10:
    print("WARNING: Portfolio risk exceeds 10%!")
```

**Adding New Position**:
```python
# 1. Get signal from screener
from src.screener import StockScreener

screener = StockScreener(min_confidence=70)
results = screener.scan(['RELIANCE', 'TCS', 'INFY'], signal_types=['BUY'])

if results:
    # Pick top signal
    top_signal = screener.get_top_signals(1, 'BUY')[0]

    # 2. Calculate position size
    sizer = PositionSizer(capital=portfolio.cash)
    size = sizer.fixed_fractional(
        price=top_signal.price,
        risk_percentage=0.02,
        stop_loss_pct=5.0
    )

    # 3. Set risk management
    risk_mgr = RiskManager()
    stop, target = risk_mgr.calculate_stop_and_target(
        entry_price=top_signal.price,
        method='risk_reward',
        stop_pct=5.0,
        risk_reward_ratio=2.0
    )

    # 4. Add to portfolio
    portfolio.open_position(
        symbol=top_signal.stock_symbol,
        shares=size.shares,
        entry_price=top_signal.price,
        stop_loss=stop,
        take_profit=target,
        notes=f"Signal from {top_signal.strategy_name}"
    )
```

**Evening Review**:
```python
# Update all positions with latest prices
symbols = [pos.symbol for pos in portfolio.get_all_positions()]
current_prices = portfolio.get_current_prices(symbols)

# Check each position
for pos in portfolio.get_all_positions():
    current_price = current_prices[pos.symbol]
    pnl = pos.calculate_pnl(current_price)

    print(f"{pos.symbol}: {pnl['pnl_pct']:+.2f}%")

    # Consider trailing stop if up >10%
    if pnl['pnl_pct'] > 10 and not isinstance(pos.stop_loss.method, 'trailing'):
        # Update to trailing stop
        new_stop = risk_mgr.trailing_stop_loss(
            pos.entry_price,
            current_price,
            trail_pct=5.0
        )
        portfolio.update_stop_loss(pos.symbol, new_stop)
        print(f"  → Updated to trailing stop at ₹{new_stop.price:.2f}")

# Export today's snapshot
portfolio.get_positions_dataframe().to_csv(
    f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
    index=False
)
```

---

### Risk Control Best Practices

#### Position Limits

```python
# Never risk more than 2% per position
MAX_RISK_PER_POSITION = 0.02

# Never risk more than 10% total
MAX_PORTFOLIO_RISK = 0.10

# Max 20% of capital per position
MAX_POSITION_SIZE = 0.20

# Max 5 positions at once
MAX_POSITIONS = 5

# Check before adding position
def can_add_position(portfolio, position_value, risk_amount):
    # Check individual position risk
    risk_pct = risk_amount / portfolio.initial_capital
    if risk_pct > MAX_RISK_PER_POSITION:
        return False, "Position risk too high"

    # Check position size
    size_pct = position_value / portfolio.initial_capital
    if size_pct > MAX_POSITION_SIZE:
        return False, "Position size too large"

    # Check number of positions
    if len(portfolio.get_all_positions()) >= MAX_POSITIONS:
        return False, "Too many positions"

    # Check total portfolio risk
    current_risk = portfolio.get_risk_exposure()['total_risk']
    new_total_risk = current_risk + risk_amount
    if (new_total_risk / portfolio.initial_capital) > MAX_PORTFOLIO_RISK:
        return False, "Portfolio risk limit exceeded"

    return True, "OK"
```

#### Daily Loss Limits

```python
# Track daily P&L
def check_daily_loss_limit(portfolio, max_daily_loss_pct=0.05):
    """Stop trading if daily loss exceeds limit."""

    # Calculate today's P&L
    # (In production, track opening value)
    today_start_value = 100000  # Save this at market open
    current_value = portfolio.get_summary()['current_value']

    daily_pnl = current_value - today_start_value
    daily_pnl_pct = daily_pnl / today_start_value

    if daily_pnl_pct <= -max_daily_loss_pct:
        print(f"CIRCUIT BREAKER: Daily loss {daily_pnl_pct:.2%} exceeds limit!")
        print("No more trades today.")
        return False

    return True
```

#### Correlation Limits

```python
# Don't over-concentrate in one sector
def check_sector_exposure(portfolio, max_sector_pct=0.40):
    """Ensure no more than 40% in one sector."""

    # Define sectors (simplified)
    sectors = {
        'RELIANCE': 'Energy',
        'TCS': 'IT',
        'INFY': 'IT',
        'HDFCBANK': 'Finance',
        'ICICIBANK': 'Finance',
        # ... etc
    }

    sector_exposure = {}
    total_value = 0

    for pos in portfolio.get_all_positions():
        sector = sectors.get(pos.symbol, 'Other')
        value = pos.shares * pos.entry_price

        sector_exposure[sector] = sector_exposure.get(sector, 0) + value
        total_value += value

    # Check each sector
    for sector, value in sector_exposure.items():
        pct = value / portfolio.initial_capital
        if pct > max_sector_pct:
            print(f"WARNING: {sector} exposure {pct:.1%} exceeds {max_sector_pct:.1%}")
            return False

    return True
```

---

### Common Workflows

#### Workflow 1: Conservative Portfolio (2% Risk Per Trade)

```python
# Setup
portfolio = Portfolio(100000, "Conservative Portfolio")
risk_mgr = RiskManager(
    max_daily_loss_pct=0.05,        # 5% daily limit
    max_portfolio_risk_pct=0.10,    # 10% total risk
    max_position_risk_pct=0.02      # 2% per position
)

# For each new position
def add_conservative_position(symbol, entry_price):
    # 1. Fixed fractional sizing (2% risk)
    sizer = PositionSizer(portfolio.cash)
    size = sizer.fixed_fractional(
        price=entry_price,
        risk_percentage=0.02,
        stop_loss_pct=5.0
    )

    # 2. Risk-reward 2:1
    stop = risk_mgr.fixed_stop_loss(entry_price, 5.0)
    target = risk_mgr.risk_reward_take_profit(entry_price, stop.price, 2.0)

    # 3. Add position
    portfolio.open_position(
        symbol, size.shares, entry_price, stop, target
    )
```

#### Workflow 2: Aggressive Portfolio (Kelly Criterion)

```python
# For traders with proven strategies
portfolio = Portfolio(100000, "Aggressive Portfolio")

def add_kelly_position(symbol, entry_price, strategy_results):
    # Use Kelly based on backtest results
    sizer = PositionSizer(portfolio.cash)
    size = sizer.kelly_criterion(
        win_rate=strategy_results['win_rate'] / 100,
        avg_win=strategy_results['avg_win_pct'],
        avg_loss=strategy_results['avg_loss_pct'],
        price=entry_price,
        kelly_fraction=0.25  # Still use quarter-Kelly for safety
    )

    # ATR-based stops
    stop = risk_mgr.atr_stop_loss(entry_price, atr=50.0, multiplier=2.0)
    target = risk_mgr.risk_reward_take_profit(entry_price, stop.price, 3.0)

    portfolio.open_position(symbol, size.shares, entry_price, stop, target)
```

#### Workflow 3: Swing Trading (Wider Stops, Multiple Targets)

```python
def add_swing_position(symbol, entry_price, support_level):
    # Position sizing
    sizer = PositionSizer(portfolio.cash)
    size = sizer.fixed_fractional(entry_price, 0.02, stop_loss_pct=10.0)

    # Support-based stop (wider for swing trades)
    stop = risk_mgr.support_resistance_stop(
        entry_price, support_level, buffer_pct=1.0
    )

    # Multiple targets
    targets = risk_mgr.multiple_targets(entry_price, [10, 20, 30])

    # Scale out:
    # - Sell 1/3 at +10%
    # - Sell 1/3 at +20%
    # - Let 1/3 run to +30% or trailing stop

    portfolio.open_position(symbol, size.shares, entry_price, stop, targets[0])
```

---

### Dashboard Usage Guide

**Access**: Navigate to "💼 Portfolio Manager" in Streamlit

#### Tab 1: Portfolio Overview

**What you see:**
- Total portfolio value and P&L
- Cash available
- Risk metrics
- Open positions table (green = profit, red = loss)
- Automatic alerts for stop-loss/take-profit hits

**Actions:**
- Close positions with current price
- View position details
- Monitor risk exposure

#### Tab 2: Add Position

**Steps:**
1. Enter stock symbol, shares, entry price
2. Choose stop-loss method (Fixed % or ATR)
3. Choose take-profit method (Fixed % or Risk-Reward)
4. Review position summary (cost, risk, potential profit)
5. Click "Add Position"

**Tips:**
- Use the preview to verify risk before adding
- ATR-based stops adapt to volatility
- Risk-Reward ratio ensures good risk/reward

#### Tab 3: Position Sizer

**Use this to calculate optimal position size before adding:**

1. Select sizing method
2. Enter current price
3. Adjust method-specific parameters
4. See recommended shares and risk

**Copy the suggested shares to Tab 2 when adding position.**

#### Tab 4: Performance

**Track your trading performance:**
- View cumulative P&L chart
- See all closed trades
- Calculate win rate
- Identify what's working

---

### Troubleshooting

**Problem**: Position won't add - "Insufficient cash"
**Solution**: Either reduce shares or close another position

**Problem**: Risk percentage seems wrong
**Solution**: Check stop-loss %. Risk = Position Value × Stop %

**Problem**: Stop-loss keeps getting hit
**Solution**: Stops too tight. Use ATR-based or wider fixed %

**Problem**: Missing profits - price goes way past target
**Solution**: Use trailing stops or scale out with multiple targets

**Problem**: Portfolio value doesn't update
**Solution**: Dashboard fetches prices on load. Refresh page for latest prices

---

### Tips & Tricks

**1. Start Small**
- Begin with 1-2 positions
- Use 1% risk per trade initially
- Increase as you gain confidence

**2. Always Use Stops**
- NEVER enter without a stop-loss
- Set it immediately after entry
- Don't move it further away (only trail up)

**3. Scale In/Out**
- Enter partial position first
- Add on confirmation
- Exit in stages (1/3 at each target)

**4. Review Weekly**
- Export positions to CSV
- Analyze what worked/didn't
- Adjust strategy accordingly

**5. Risk Management > Everything**
- One big loss can wipe out months of gains
- Protect capital first, profits second
- When in doubt, reduce position size

---

## Sentiment Analysis Guide

Complete guide to using news sentiment analysis for trading decisions.

---

### Quick Start

**1. Test Sentiment Analysis**:
```bash
source venv/bin/activate

# Analyze a single stock
python -c "
from src.sentiment import SentimentScorer

scorer = SentimentScorer(sentiment_method='vader')
sentiment = scorer.analyze_stock('RELIANCE', max_news=10)

print(f'Sentiment: {sentiment.overall_sentiment.upper()}')
print(f'Score: {sentiment.overall_score:.2f}')
print(f'News Count: {sentiment.news_count}')

summary = scorer.get_sentiment_summary(sentiment)
print(f'Signal: {summary[\"signal\"]}')
print(f'Recommendation: {summary[\"recommendation\"]}')
"
```

**2. Access Dashboard**:
```bash
streamlit run src/presentation/streamlit_app/app.py
# Navigate to "📰 Sentiment Analysis"
```

---

### Understanding Sentiment Analysis

#### Sentiment Score Scale

```
+1.0  ← Very Positive
+0.5  ← Moderately Positive
+0.1  ← Slightly Positive
 0.0  ← Neutral
-0.1  ← Slightly Negative
-0.5  ← Moderately Negative
-1.0  ← Very Negative
```

**Classification**:
- **Positive**: Score > 0.1
- **Neutral**: Score between -0.1 and 0.1
- **Negative**: Score < -0.1

**Trading Signals**:
- **BUY**: Score > 0.3 and positive sentiment
- **SELL**: Score < -0.3 and negative sentiment
- **HOLD**: Everything else (neutral or weak sentiment)

**Confidence**:
- 0.0 - 0.3: Low confidence (be cautious)
- 0.3 - 0.6: Moderate confidence (decent signal)
- 0.6 - 1.0: High confidence (strong signal)

#### Sentiment Methods Comparison

| Method | Best For | Speed | Accuracy | Recommendation |
|--------|----------|-------|----------|----------------|
| **VADER** | Financial news, headlines | Fast | High | ⭐ **Recommended** |
| **TextBlob** | General text | Fast | Good | Alternative |
| **Combined** | Consensus analysis | Medium | Very Good | Conservative |
| **Simple** | Fallback only | Very Fast | Basic | Auto-fallback |

**When to use each**:
- **VADER**: Default choice for financial news (optimized for social media/news)
- **TextBlob**: When you want a second opinion
- **Combined**: When you want conservative, averaged results
- **Simple**: Automatically used if libraries unavailable (keyword-based)

---

### Workflow Examples

#### Workflow 1: Morning Market Check

Find trending stocks and check sentiment:

```bash
python -c "
from src.sentiment import NewsFetcher, SentimentScorer

# 1. Find trending stocks
fetcher = NewsFetcher()
trending = fetcher.get_trending_stocks(limit=10)

print('📰 TRENDING STOCKS (Most News Coverage)')
print('=' * 60)

# 2. Quick sentiment check
scorer = SentimentScorer()
for stock in trending[:5]:
    sentiment = scorer.analyze_stock(stock['symbol'], max_news=5, days_back=1)
    summary = scorer.get_sentiment_summary(sentiment)

    print(f\"{stock['symbol']:10} | {summary['signal']:4} | \"
          f\"Score: {sentiment.overall_score:5.2f} | \"
          f\"News: {sentiment.news_count:2}\")
"
```

**Output**:
```
📰 TRENDING STOCKS (Most News Coverage)
============================================================
RELIANCE   | BUY  | Score:  0.42 | News: 12
TCS        | BUY  | Score:  0.35 | News:  8
HDFCBANK   | HOLD | Score:  0.08 | News: 10
INFY       | SELL | Score: -0.28 | News:  6
SBIN       | HOLD | Score: -0.05 | News:  7
```

#### Workflow 2: Stock Research with Sentiment

Combine technical + sentiment analysis:

```bash
python -c "
from src.strategy import StrategyRunner
from src.sentiment import SentimentScorer

symbol = 'RELIANCE'

# 1. Technical analysis
runner = StrategyRunner()
tech_signals = runner.run_strategy('RSI', symbol)
rsi = tech_signals.get('rsi', 50)

# 2. Sentiment analysis
scorer = SentimentScorer()
sentiment = scorer.analyze_stock(symbol, max_news=20, days_back=7)
summary = scorer.get_sentiment_summary(sentiment)

# 3. Combined decision
print(f'\\n{symbol} Analysis:')
print('=' * 50)
print(f'RSI: {rsi:.1f}')
print(f'Sentiment: {sentiment.overall_sentiment.upper()} ({sentiment.overall_score:.2f})')
print(f'Signal: {summary[\"signal\"]}')
print(f'Confidence: {sentiment.confidence:.2%}')
print()

# Decision logic
if rsi < 30 and summary['signal'] == 'BUY':
    print('✅ STRONG BUY: Oversold + Positive sentiment')
elif rsi > 70 and summary['signal'] == 'SELL':
    print('⛔ STRONG SELL: Overbought + Negative sentiment')
elif 30 <= rsi <= 70 and summary['signal'] == 'BUY':
    print('🟢 BUY: Positive sentiment, normal RSI')
elif 30 <= rsi <= 70 and summary['signal'] == 'SELL':
    print('🔴 SELL: Negative sentiment, normal RSI')
else:
    print('⏸️  HOLD: Mixed signals or neutral')
"
```

#### Workflow 3: Sector Sentiment Comparison

Compare sentiment across sector stocks:

```bash
python -c "
from src.sentiment import SentimentScorer

# IT Sector stocks
it_stocks = ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM']

scorer = SentimentScorer()
print('🏢 IT SECTOR SENTIMENT ANALYSIS')
print('=' * 70)
print(f'{'Symbol':10} | {'Signal':4} | {'Sent':8} | {'Score':5} | {'Conf':5} | News')
print('-' * 70)

results = scorer.compare_stocks(it_stocks, max_news=10, days_back=7)

for sentiment in results:
    summary = scorer.get_sentiment_summary(sentiment)
    print(f\"{sentiment.symbol:10} | {summary['signal']:4} | \"
          f\"{sentiment.overall_sentiment:8} | {sentiment.overall_score:5.2f} | \"
          f\"{sentiment.confidence:5.2%} | {sentiment.news_count:2}\")
"
```

#### Workflow 4: Pre-Market Watchlist

Build watchlist based on positive sentiment:

```bash
python -c "
from src.sentiment import SentimentScorer

# Stocks to check
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
          'BHARTIARTL', 'ITC', 'SBIN', 'WIPRO', 'LT']

scorer = SentimentScorer()

# Filter for positive sentiment
positive_stocks = scorer.filter_by_sentiment(
    symbols=stocks,
    target_sentiment='positive',
    min_confidence=0.3
)

print('📈 POSITIVE SENTIMENT WATCHLIST')
print('=' * 60)

if positive_stocks:
    for sentiment in positive_stocks:
        summary = scorer.get_sentiment_summary(sentiment)
        print(f\"\\n{sentiment.symbol}\")
        print(f\"  Score: {sentiment.overall_score:.2f}\")
        print(f\"  Confidence: {sentiment.confidence:.2%}\")
        print(f\"  Signal: {summary['signal']}\")
        print(f\"  Recommendation: {summary['recommendation']}\")
        print(f\"  News: {sentiment.news_count} articles\")
else:
    print('No stocks with strong positive sentiment found.')
"
```

---

### Dashboard Usage Guide

#### Tab 1: Single Stock Analysis

**Purpose**: Deep dive into one stock's sentiment

**Steps**:
1. Enter stock symbol (e.g., `RELIANCE`, `TCS`)
2. Adjust settings in sidebar:
   - Max News Articles: 5-50 (default: 20)
   - Time Period: 1-30 days (default: 7)
   - Analysis Method: VADER/TextBlob/Combined (default: VADER)
3. Click "🔍 Analyze Sentiment"

**What you get**:
- Overall sentiment (POSITIVE/NEGATIVE/NEUTRAL)
- Sentiment score (-1.0 to +1.0)
- Confidence level (0-100%)
- News count
- BUY/SELL/HOLD signal
- Sentiment distribution charts (pie + bar)
- Individual news articles with sentiment
- CSV export

**Use cases**:
- Research a stock before buying
- Check news context for price movements
- Validate technical signals
- Monitor existing positions

#### Tab 2: Multi-Stock Comparison

**Purpose**: Compare sentiment across multiple stocks

**Steps**:
1. Choose input method:
   - **Popular Stocks**: Select from predefined list
   - **Custom List**: Enter your own symbols (one per line)
2. Select/enter stocks
3. Click "🔍 Compare Sentiment"

**What you get**:
- Color-coded comparison table (green=positive, red=negative)
- Sentiment score bar chart
- Most positive stocks (top 3)
- Most negative stocks (top 3)
- CSV export

**Use cases**:
- Compare stocks within a sector
- Build a watchlist
- Rank stocks by sentiment
- Sector rotation decisions

#### Tab 3: Trending Stocks

**Purpose**: Discover stocks with most news coverage

**Steps**:
1. Click "🔍 Find Trending Stocks"
2. Expand stocks to see quick sentiment

**What you get**:
- Top 10 stocks by news count (24 hours)
- Latest news headline for each
- Quick sentiment analysis (5 articles, 1 day)
- Sentiment metrics (sentiment, score, news count)

**Use cases**:
- Morning market scan
- Find newsworthy stocks
- Discover trading opportunities
- Stay informed on active stocks

---

### Configuration Guidelines

#### Time Period Selection

| Period | Use Case | Best For |
|--------|----------|----------|
| **1 day** | Breaking news, events | Day trading, event-driven |
| **3 days** | Recent developments | Short-term trading |
| **7 days** | Week's sentiment | Swing trading (recommended) |
| **14 days** | Medium-term trend | Position trading |
| **30 days** | Long-term context | Investment decisions |

#### News Count Selection

| Count | Analysis Depth | Speed | Reliability |
|-------|---------------|-------|-------------|
| **5-10** | Quick check | Fast | Low (use for screening) |
| **20** | Standard analysis | Medium | Good ⭐ **Recommended** |
| **30-50** | Deep dive | Slow | High (comprehensive) |

**Recommendation**: Start with 20 articles and 7 days for most cases.

---

### Best Practices

#### ✅ Do's

**1. Use Sentiment as Confirmation**
```python
# ✅ Good: Combine with technical analysis
if rsi < 30 and sentiment_signal == 'BUY':
    execute_trade()
```

**2. Check Minimum News Count**
```python
# ✅ Good: Verify sufficient data
if sentiment.news_count >= 5:
    trust_signal = True
else:
    print("Not enough news data")
```

**3. Verify High-Confidence Signals**
```python
# ✅ Good: Higher confidence = more reliable
if sentiment.confidence > 0.6 and summary['signal'] == 'BUY':
    # Strong signal
    position_size = 'normal'
elif sentiment.confidence > 0.3:
    # Moderate signal
    position_size = 'reduced'
else:
    # Low confidence
    position_size = 'skip'
```

**4. Read Key News Manually**
```python
# ✅ Good: Verify major events
for article in sentiment.news_articles[:3]:
    print(f"{article['title']}")
    # Read to understand context
```

**5. Monitor Sentiment Changes**
```python
# ✅ Good: Track sentiment over time
today_sentiment = scorer.analyze_stock('RELIANCE', days_back=1)
week_sentiment = scorer.analyze_stock('RELIANCE', days_back=7)

if today_sentiment.overall_score < week_sentiment.overall_score - 0.2:
    print("⚠️ Sentiment deteriorating")
```

#### ❌ Don'ts

**1. Don't Trade on Sentiment Alone**
```python
# ❌ Bad: Only using sentiment
if summary['signal'] == 'BUY':
    buy()  # Missing technical analysis, risk management
```

**2. Don't Ignore Low News Count**
```python
# ❌ Bad: Trusting signal with only 1-2 articles
if sentiment.news_count < 5:
    # Don't trust this signal
```

**3. Don't Overtrade on News**
```python
# ❌ Bad: Trading every sentiment change
# Sentiment can be noisy in short term
```

**4. Don't Ignore Confidence**
```python
# ❌ Bad: Treating all signals equally
if summary['signal'] == 'BUY':
    # Should check confidence first
```

**5. Don't Skip Risk Management**
```python
# ❌ Bad: Forgetting stop-loss because sentiment is positive
# Always use stop-loss regardless of sentiment
```

---

### Common Workflows

#### Conservative Trader

```bash
# Daily routine
python -c "
from src.sentiment import SentimentScorer

# Only trade stocks with:
# - Strong positive sentiment (score > 0.4)
# - High confidence (> 60%)
# - Sufficient news (10+ articles)

scorer = SentimentScorer()
watchlist = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']

for symbol in watchlist:
    sentiment = scorer.analyze_stock(symbol, max_news=20)
    summary = scorer.get_sentiment_summary(sentiment)

    # Conservative filters
    if (sentiment.overall_score > 0.4 and
        sentiment.confidence > 0.6 and
        sentiment.news_count >= 10):
        print(f'✅ {symbol}: Strong BUY signal')
        print(f'   Score: {sentiment.overall_score:.2f}')
        print(f'   Confidence: {sentiment.confidence:.2%}')
"
```

#### Aggressive Trader

```bash
# More signals, lower thresholds
python -c "
from src.sentiment import SentimentScorer

scorer = SentimentScorer()
watchlist = ['RELIANCE', 'TCS', 'INFY', 'WIPRO', 'SBIN',
             'BHARTIARTL', 'ITC', 'LT']

# Lower thresholds for more signals
for symbol in watchlist:
    sentiment = scorer.analyze_stock(symbol, max_news=10, days_back=3)
    summary = scorer.get_sentiment_summary(sentiment)

    # Aggressive: Take any BUY signal with moderate confidence
    if summary['signal'] == 'BUY' and sentiment.confidence > 0.3:
        print(f'📈 {symbol}: {summary[\"signal\"]} (score: {sentiment.overall_score:.2f})')
"
```

#### Swing Trader (7-14 Day Hold)

```bash
# Medium-term sentiment + technical confirmation
python -c "
from src.sentiment import SentimentScorer
from src.strategy import StrategyRunner

scorer = SentimentScorer()
runner = StrategyRunner()

symbol = 'RELIANCE'

# 7-day sentiment
sentiment = scorer.analyze_stock(symbol, max_news=20, days_back=7)
summary = scorer.get_sentiment_summary(sentiment)

# Technical signals
tech_signals = runner.run_strategy('RSI', symbol)
rsi = tech_signals.get('rsi', 50)

# Swing trade criteria
if (sentiment.overall_score > 0.2 and  # Positive sentiment
    sentiment.confidence > 0.4 and      # Good confidence
    30 <= rsi <= 60):                   # Not overbought
    print(f'🎯 {symbol}: Good swing trade setup')
    print(f'   Sentiment: {sentiment.overall_score:.2f}')
    print(f'   RSI: {rsi:.1f}')
    print(f'   Hold: 7-14 days')
"
```

---

### Troubleshooting

#### Issue: "No news found for symbol"

**Causes**:
- Invalid symbol
- Stock has very little news coverage
- Time period too narrow

**Solutions**:
```bash
# Try with .NS suffix for NSE stocks
sentiment = scorer.analyze_stock('RELIANCE.NS')

# Increase time period
sentiment = scorer.analyze_stock('RELIANCE', days_back=14)

# Check if symbol is correct
from src.sentiment import NewsFetcher
fetcher = NewsFetcher()
news = fetcher.fetch_news('RELIANCE')
print(f"Found {len(news)} articles")
```

#### Issue: "Low confidence scores"

**Causes**:
- Mixed/neutral news
- Low-quality news sources
- Insufficient news articles

**Solutions**:
```bash
# Increase news count
sentiment = scorer.analyze_stock('RELIANCE', max_news=30)

# Use combined method for consensus
scorer = SentimentScorer(sentiment_method='combined')

# Check individual articles
for article in sentiment.news_articles[:5]:
    print(f"{article['title']}: {article['score']:.2f}")
```

#### Issue: "Sentiment doesn't match price movement"

**Understanding**:
- Sentiment is **lagging indicator** (reflects past news)
- Price often moves **before** news
- News sentiment ≠ guarantee of price direction

**What to do**:
```bash
# Use sentiment for confirmation, not prediction
# Combine with technical analysis
# Don't expect perfect correlation
```

#### Issue: "Different methods give different results"

**This is normal**:
```bash
# VADER is optimized for social media/news
vader_score = 0.65

# TextBlob is more general purpose
textblob_score = 0.42

# Combined averages both
combined_score = 0.54

# Use VADER for financial news (recommended)
```

---

### Integration Examples

#### Integrate with Stock Screener

```python
from src.screener import StockScreener
from src.sentiment import SentimentScorer

# 1. Screen for technical setups
screener = StockScreener()
technical_candidates = screener.screen({
    'rsi_max': 40,  # Oversold
    'min_volume': 1000000
})

# 2. Filter by sentiment
scorer = SentimentScorer()
for stock in technical_candidates[:10]:
    sentiment = scorer.analyze_stock(stock['symbol'])
    summary = scorer.get_sentiment_summary(sentiment)

    if summary['signal'] == 'BUY':
        print(f"✅ {stock['symbol']}: Technical + Sentiment BUY")
```

#### Integrate with Portfolio

```python
from src.portfolio import Portfolio
from src.sentiment import SentimentScorer

portfolio = Portfolio(capital=100000)
scorer = SentimentScorer()

# Check sentiment for all positions
for position in portfolio.get_all_positions():
    sentiment = scorer.analyze_stock(position.symbol, days_back=1)
    summary = scorer.get_sentiment_summary(sentiment)

    # Alert on negative sentiment
    if summary['signal'] == 'SELL':
        print(f"⚠️ {position.symbol}: Negative sentiment - consider exit")
        print(f"   Current P&L: {position.calculate_pnl(position.current_price)['pnl_pct']:.2f}%")
```

---

### Tips & Tricks

**1. Morning Routine**
```bash
# Quick scan of trending stocks
python -c "from src.sentiment import NewsFetcher;
trending = NewsFetcher().get_trending_stocks(5);
print('\\n'.join([f\"{s['symbol']}: {s['news_count']} articles\" for s in trending]))"
```

**2. Compare Sentiment Methods**
```python
from src.sentiment import SentimentAnalyzer

text = "Company reports strong quarterly results"

for method in ['vader', 'textblob', 'combined']:
    analyzer = SentimentAnalyzer(method=method)
    sentiment = analyzer.analyze_text(text)
    print(f"{method:10}: {sentiment.score:.2f}")
```

**3. Export for Further Analysis**
```python
import pandas as pd
from src.sentiment import SentimentScorer

scorer = SentimentScorer()
sentiment = scorer.analyze_stock('RELIANCE', max_news=50)

# Export to CSV
df = pd.DataFrame(sentiment.news_articles)
df.to_csv('reliance_sentiment.csv', index=False)
```

**4. Batch Analysis Script**
```bash
# Save as analyze_watchlist.py
python -c "
from src.sentiment import SentimentScorer
import sys

stocks = sys.argv[1:]  # Pass stocks as arguments
scorer = SentimentScorer()

for symbol in stocks:
    sentiment = scorer.analyze_stock(symbol, max_news=10)
    summary = scorer.get_sentiment_summary(sentiment)
    print(f'{symbol:10} | {summary[\"signal\"]:4} | {sentiment.overall_score:5.2f}')
" RELIANCE TCS INFY HDFCBANK
```

**5. Sentiment Alerts**
```python
# Monitor for sentiment changes
from src.sentiment import SentimentScorer
import time

scorer = SentimentScorer()
previous_scores = {}

while True:
    for symbol in ['RELIANCE', 'TCS']:
        sentiment = scorer.analyze_stock(symbol, max_news=5, days_back=1)

        # Alert on significant change
        if symbol in previous_scores:
            change = sentiment.overall_score - previous_scores[symbol]
            if abs(change) > 0.3:
                print(f"🚨 {symbol}: Sentiment changed by {change:+.2f}")

        previous_scores[symbol] = sentiment.overall_score

    time.sleep(3600)  # Check every hour
```

---

## Testing Procedures Guide

Complete step-by-step testing procedures for all features.

---

### 1. Testing Individual Strategies

#### Method 1: Quick CLI Test (Fastest)

Test any strategy with a single stock using Python one-liner:

```bash
# Activate environment
source venv/bin/activate

# Test RSI Strategy
python -c "
from src.strategies.technical import RSIStrategy
import yfinance as yf

# Fetch data
data = yf.Ticker('RELIANCE.NS').history(period='1y')
data.columns = data.columns.str.lower()

# Run strategy
strategy = RSIStrategy()
signals = strategy.analyze(data)

# Show results
print(f'Strategy: {strategy.name}')
print(f'Total Signals: {len(signals)}')
if signals:
    latest = signals[-1]
    print(f'Latest Signal: {latest.signal_type} at ₹{latest.price:.2f}')
    print(f'Confidence: {latest.confidence:.1f}%')
    print(f'Date: {latest.date}')
"
```

**Expected Output**:
```
Strategy: RSI Strategy
Total Signals: 15
Latest Signal: BUY at ₹2,847.50
Confidence: 75.0%
Date: 2025-11-08
```

#### Method 2: Test Script

Create a test script for more detailed testing:

```bash
# Create test file
cat > test_strategy.py << 'EOF'
"""Test a specific strategy"""
import yfinance as yf
from src.strategies.technical import (
    RSIStrategy, MACDStrategy, BollingerBandsStrategy,
    SupertrendStrategy, ADXStrategy, StochasticStrategy
)

def test_strategy(strategy_class, symbol='RELIANCE.NS', period='1y'):
    """Test a strategy on a stock"""
    print(f"\n{'='*60}")

    # Fetch data
    print(f"Fetching data for {symbol}...")
    data = yf.Ticker(symbol).history(period=period)
    data.columns = data.columns.str.lower()

    if data.empty:
        print("❌ No data fetched!")
        return

    print(f"✅ Fetched {len(data)} days of data")

    # Create strategy
    strategy = strategy_class()
    print(f"\nTesting: {strategy.name}")
    print(f"Description: {strategy.description}")

    # Generate signals
    signals = strategy.analyze(data)

    print(f"\n📊 Results:")
    print(f"   Total Signals: {len(signals)}")

    if signals:
        # Show all signals
        buy_signals = [s for s in signals if s.signal_type == 'BUY']
        sell_signals = [s for s in signals if s.signal_type == 'SELL']

        print(f"   BUY Signals: {len(buy_signals)}")
        print(f"   SELL Signals: {len(sell_signals)}")

        # Latest signal
        latest = signals[-1]
        print(f"\n   Latest Signal:")
        print(f"      Type: {latest.signal_type}")
        print(f"      Price: ₹{latest.price:,.2f}")
        print(f"      Confidence: {latest.confidence:.1f}%")
        print(f"      Date: {latest.date}")
        print(f"      Metadata: {latest.metadata}")
    else:
        print("   ⚠️  No signals generated")

    print(f"{'='*60}\n")
    return signals

# Test all strategies
if __name__ == '__main__':
    strategies = [
        RSIStrategy,
        MACDStrategy,
        BollingerBandsStrategy,
        SupertrendStrategy,
        ADXStrategy,
        StochasticStrategy
    ]

    for strategy_cls in strategies:
        test_strategy(strategy_cls)
EOF

# Run test
python test_strategy.py
```

**Expected Output**: Detailed results for each strategy with signal counts and latest signal.

#### Method 3: Test via Streamlit UI

1. **Start Application**:
```bash
source venv/bin/activate
streamlit run src/presentation/streamlit_app/app.py
```

2. **Navigate to Dashboard**:
   - Open browser to `http://localhost:8501`
   - Go to "📊 Dashboard" page

3. **Test Strategy**:
   - Select stock: `RELIANCE`
   - Select strategy: `RSI Strategy`
   - Click "Analyze"
   - Verify:
     - ✅ Chart loads with signals
     - ✅ Signal summary shows BUY/SELL counts
     - ✅ Latest signal displays correctly
     - ✅ Parameters are adjustable

4. **Test All Strategies**:
   - Repeat for each strategy in dropdown
   - Verify each generates signals
   - Check charts render correctly

---

### 2. Testing Backtesting Engine

#### Method 1: CLI Quick Test

```bash
python -c "
from src.backtesting.engine import BacktestEngine
from src.strategies.technical import RSIStrategy
import yfinance as yf

# Fetch 2 years of data
data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

# Run backtest
engine = BacktestEngine(initial_capital=100000)
strategy = RSIStrategy()
results = engine.run(data, strategy)

# Show results
print('='*60)
print('BACKTEST RESULTS')
print('='*60)
for key, value in results.items():
    if isinstance(value, float):
        print(f'{key}: {value:.2f}')
    else:
        print(f'{key}: {value}')
print('='*60)
"
```

**Expected Output**:
```
============================================================
BACKTEST RESULTS
============================================================
total_return_pct: 37.16
win_rate: 66.67
profit_factor: 2.89
total_trades: 12
winning_trades: 8
losing_trades: 4
sharpe_ratio: 1.45
sortino_ratio: 2.12
max_drawdown: -8.34
calmar_ratio: 4.45
============================================================
```

**Validation Checklist**:
- ✅ `total_return_pct` > 0 (profitable)
- ✅ `win_rate` between 0-100
- ✅ `sharpe_ratio` > 1.0 (good risk-adjusted return)
- ✅ `max_drawdown` < -20% (acceptable risk)
- ✅ `total_trades` > 5 (sufficient sample)

#### Method 2: Via Streamlit UI

1. **Navigate to Backtesting Page**:
   - Go to "🔄 Backtesting" page

2. **Configure Backtest**:
   - Stock: `TCS`
   - Strategy: `MACD Strategy`
   - Initial Capital: `₹100,000`
   - Date Range: Last 2 years

3. **Run and Verify**:
   - Click "Run Backtest"
   - Verify:
     - ✅ Performance metrics display
     - ✅ Equity curve chart renders
     - ✅ Trade list shows entries
     - ✅ Download CSV works

4. **Test Edge Cases**:
   - Very short period (30 days) → Should warn if too few trades
   - Very long period (5 years) → Should complete successfully
   - Different strategies → Each should work

---

### 3. Testing Parameter Optimization

#### Method 1: CLI Test

```bash
python -c "
from src.backtesting.optimizer import ParameterOptimizer
from src.strategies.technical import RSIStrategy
import yfinance as yf

# Fetch data
data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

# Define parameter ranges to test
param_ranges = {
    'period': [10, 14, 20],
    'oversold': [25, 30, 35],
    'overbought': [65, 70, 75]
}

print('Starting optimization...')
print(f'Testing {3*3*3} = 27 combinations')

# Optimize
optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=data,
    optimization_metric='sharpe_ratio'
)

results = optimizer.optimize(param_ranges, min_trades=5)

print(f'\n✅ Found {len(results)} valid combinations\n')

# Show top 3
print('='*60)
print('TOP 3 PARAMETER COMBINATIONS')
print('='*60)

for i, result in enumerate(results[:3], 1):
    print(f'\n#{i}')
    print(f'   Parameters: {result.params}')
    print(f'   Sharpe Ratio: {result.metrics[\"sharpe_ratio\"]:.2f}')
    print(f'   Return: {result.metrics[\"total_return_pct\"]:.2f}%')
    print(f'   Win Rate: {result.metrics[\"win_rate\"]:.1f}%')
    print(f'   Trades: {result.metrics[\"total_trades\"]}')

print('='*60)
"
```

**Expected Output**:
```
Starting optimization...
Testing 3*3*3 = 27 combinations

✅ Found 24 valid combinations

============================================================
TOP 3 PARAMETER COMBINATIONS
============================================================

#1
   Parameters: {'period': 14, 'oversold': 30, 'overbought': 70}
   Sharpe Ratio: 1.87
   Return: 42.35%
   Win Rate: 71.4%
   Trades: 14

#2
   Parameters: {'period': 10, 'oversold': 25, 'overbought': 70}
   Sharpe Ratio: 1.65
   Return: 38.90%
   Win Rate: 66.7%
   Trades: 12

#3
   Parameters: {'period': 20, 'oversold': 30, 'overbought': 75}
   Sharpe Ratio: 1.52
   Return: 35.20%
   Win Rate: 64.3%
   Trades: 14

============================================================
```

**Validation Checklist**:
- ✅ Returns multiple valid results
- ✅ Results are sorted by metric (best first)
- ✅ All results meet `min_trades` threshold
- ✅ Top result has better metrics than default parameters

#### Method 2: Via Streamlit UI

1. **Navigate to Optimization Page**:
   - Go to "⚡ Optimization" page
   - Click "Parameter Optimization" tab

2. **Configure Optimization**:
   - Strategy: `RSI Strategy`
   - Stock: `RELIANCE`
   - Date Range: Last 2 years
   - Metric: `sharpe_ratio`

3. **Set Parameter Ranges**:
   - `period`: 10, 14, 20
   - `oversold`: 25, 30, 35
   - `overbought`: 65, 70, 75

4. **Run and Verify**:
   - Click "Run Optimization"
   - Verify:
     - ✅ Shows "Testing X combinations"
     - ✅ Best parameters highlighted
     - ✅ Top 10 results table displays
     - ✅ Each result shows params + metrics
     - ✅ Can download results

---

### 4. Testing Strategy Comparison

#### Method 1: CLI Test

```bash
python -c "
from src.backtesting.comparator import StrategyComparator
from src.strategies.technical import RSIStrategy, MACDStrategy, BollingerBandsStrategy
import yfinance as yf

# Fetch data
data = yf.Ticker('TCS.NS').history(period='2y')
data.columns = data.columns.str.lower()

# Create comparator
comparator = StrategyComparator(data=data, initial_capital=100000)

# Add strategies
comparator.add_strategy(RSIStrategy())
comparator.add_strategy(MACDStrategy())
comparator.add_strategy(BollingerBandsStrategy())

print('='*60)
print('STRATEGY COMPARISON')
print('='*60)

# Get best by different metrics
best_sharpe = comparator.get_best_strategy('sharpe_ratio')
best_return = comparator.get_best_strategy('total_return_pct')

print(f'\nBest by Sharpe Ratio: {best_sharpe.strategy_name}')
print(f'   Sharpe: {best_sharpe.metrics[\"sharpe_ratio\"]:.2f}')
print(f'   Return: {best_sharpe.metrics[\"total_return_pct\"]:.2f}%')

print(f'\nBest by Total Return: {best_return.strategy_name}')
print(f'   Return: {best_return.metrics[\"total_return_pct\"]:.2f}%')
print(f'   Sharpe: {best_return.metrics[\"sharpe_ratio\"]:.2f}')

# Show all results
print(f'\n{\"=\"*60}')
print('ALL STRATEGIES')
print('='*60)

for result in comparator.results:
    print(f'\n{result.strategy_name}:')
    print(f'   Return: {result.metrics[\"total_return_pct\"]:.2f}%')
    print(f'   Sharpe: {result.metrics[\"sharpe_ratio\"]:.2f}')
    print(f'   Win Rate: {result.metrics[\"win_rate\"]:.1f}%')
    print(f'   Trades: {result.metrics[\"total_trades\"]}')

print('='*60)
"
```

**Expected Output**: Comparison showing which strategy performed best by different metrics.

**Validation Checklist**:
- ✅ All strategies complete successfully
- ✅ Each strategy has metrics calculated
- ✅ Can identify best by different metrics
- ✅ Results are comparable (same data/capital)

#### Method 2: Via Streamlit UI

1. **Navigate to Optimization Page**:
   - Go to "⚡ Optimization" page
   - Click "Strategy Comparison" tab

2. **Select Strategies to Compare**:
   - Check: RSI, MACD, Bollinger Bands, Supertrend
   - Stock: `INFY`
   - Date Range: Last 2 years

3. **Run Comparison**:
   - Click "Compare Strategies"
   - Verify:
     - ✅ Winner summary displays
     - ✅ Comparison table shows all strategies
     - ✅ Equity curves chart displays all strategies
     - ✅ Rankings show for each metric
     - ✅ Can export to CSV

---

### 5. Testing Stock Screener

#### Method 1: CLI Test

```bash
python -c "
from src.screener import StockScreener

# Create screener
screener = StockScreener(
    lookback_days=365,
    min_confidence=50
)

# Define stocks to scan
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']

print('='*60)
print(f'SCANNING {len(stocks)} STOCKS')
print('='*60)

# Run scan
results = screener.scan(
    stock_symbols=stocks,
    signal_types=['BUY', 'SELL']
)

print(f'\n✅ Found {len(results)} signals\n')

# Show summary
summary = screener.get_summary()
print('SUMMARY:')
print(f'   Total Signals: {summary[\"total_signals\"]}')
print(f'   BUY Signals: {summary[\"buy_signals\"]}')
print(f'   SELL Signals: {summary[\"sell_signals\"]}')
print(f'   Avg Confidence: {summary[\"avg_confidence\"]:.1f}%')

# Show top 5 BUY signals
print(f'\n{\"=\"*60}')
print('TOP 5 BUY SIGNALS')
print('='*60)

top_buys = screener.get_top_signals(5, 'BUY')
for i, signal in enumerate(top_buys, 1):
    print(f'\n#{i} {signal.stock_symbol}')
    print(f'   Strategy: {signal.strategy_name}')
    print(f'   Price: ₹{signal.price:,.2f}')
    print(f'   Confidence: {signal.confidence:.1f}%')
    print(f'   Date: {signal.signal_date}')

print('='*60)
"
```

**Expected Output**:
```
============================================================
SCANNING 5 STOCKS
============================================================

✅ Found 18 signals

SUMMARY:
   Total Signals: 18
   BUY Signals: 10
   SELL Signals: 8
   Avg Confidence: 68.3%

============================================================
TOP 5 BUY SIGNALS
============================================================

#1 TCS
   Strategy: RSI Strategy
   Price: ₹3,445.80
   Confidence: 85.2%
   Date: 2025-11-08

#2 RELIANCE
   Strategy: Bollinger Bands Strategy
   Price: ₹2,847.50
   Confidence: 78.5%
   Date: 2025-11-08

...
============================================================
```

**Validation Checklist**:
- ✅ Scans all stocks successfully
- ✅ Finds signals for multiple stocks
- ✅ Summary statistics are accurate
- ✅ Top signals sorted by confidence
- ✅ No errors for missing/invalid stocks

#### Method 2: Via Streamlit UI

1. **Navigate to Screener Page**:
   - Go to "🔍 Stock Screener" page

2. **Configure Scan**:
   - Stock Selection: "Popular Stocks"
   - Select: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK
   - Strategies: Select all (or specific ones)
   - Signal Type: Both BUY and SELL
   - Min Confidence: 50%
   - Lookback: 365 days

3. **Run Scan**:
   - Click "🔍 Scan Stocks"
   - Wait for "Scanning..." spinner

4. **Verify Results**:
   - ✅ Summary cards show counts
   - ✅ Results table displays with color coding
   - ✅ Top signals sections show top 5 BUY/SELL
   - ✅ Charts render (signals by strategy, distribution)
   - ✅ Download CSV works

5. **Test NIFTY 50 Scan** (Longer Test):
   - Stock Selection: "NIFTY 50"
   - Strategies: Select 2-3 strategies (faster)
   - Click "Scan Stocks"
   - Should complete in 30-90 seconds
   - Verify results for 50 stocks

---

### 6. Integration Testing

Test complete workflows end-to-end:

#### Workflow 1: Find Best Strategy for a Stock

```bash
# Step 1: Compare strategies
python -c "
from src.backtesting.comparator import StrategyComparator
from src.strategies.technical import RSIStrategy, MACDStrategy, BollingerBandsStrategy, SupertrendStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

comp = StrategyComparator(data=data)
comp.add_strategy(RSIStrategy())
comp.add_strategy(MACDStrategy())
comp.add_strategy(BollingerBandsStrategy())
comp.add_strategy(SupertrendStrategy())

best = comp.get_best_strategy('sharpe_ratio')
print(f'Best Strategy: {best.strategy_name}')
print(f'Sharpe: {best.metrics[\"sharpe_ratio\"]:.2f}')
"

# Step 2: Optimize best strategy (if it's RSI)
python -c "
from src.backtesting.optimizer import ParameterOptimizer
from src.strategies.technical import RSIStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=data,
    optimization_metric='sharpe_ratio'
)

results = optimizer.optimize({
    'period': [10, 14, 20],
    'oversold': [25, 30],
    'overbought': [70, 75]
})

best = results[0]
print(f'Best Parameters: {best.params}')
print(f'Sharpe: {best.metrics[\"sharpe_ratio\"]:.2f}')
print(f'Return: {best.metrics[\"total_return_pct\"]:.2f}%')
"

# Step 3: Backtest with optimized parameters
python -c "
from src.backtesting.engine import BacktestEngine
from src.strategies.technical import RSIStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

# Use optimized params from step 2
strategy = RSIStrategy(period=14, oversold=30, overbought=70)
engine = BacktestEngine(initial_capital=100000)
results = engine.run(data, strategy)

print('Final Backtest Results:')
print(f\"Return: {results['total_return_pct']:.2f}%\")
print(f\"Sharpe: {results['sharpe_ratio']:.2f}\")
print(f\"Max DD: {results['max_drawdown']:.2f}%\")
"
```

**Expected**: Each step completes successfully and shows progression to optimized strategy.

#### Workflow 2: Daily Screening Routine

```bash
# Scan NIFTY 50 for opportunities
python -c "
from src.screener import StockScreener

nifty50 = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK'
]

screener = StockScreener(lookback_days=365, min_confidence=60)
results = screener.scan(stock_symbols=nifty50, signal_types=['BUY'])

print(f'Found {len(results)} high-confidence BUY signals')

top_5 = screener.get_top_signals(5, 'BUY')
for i, sig in enumerate(top_5, 1):
    print(f'{i}. {sig.stock_symbol} via {sig.strategy_name} ({sig.confidence:.0f}%)')

# Export for tracking
screener.export_to_csv('daily_scan.csv')
print('Exported to daily_scan.csv')
"
```

**Expected**: Finds opportunities, shows top signals, exports CSV.

---

### 7. Verification Checklist

Use this checklist to verify complete functionality:

#### Strategies (8 total)
- [ ] SMA Crossover generates signals
- [ ] RSI generates signals
- [ ] VWAP generates signals
- [ ] MACD generates signals
- [ ] Bollinger Bands generates signals
- [ ] Stochastic generates signals
- [ ] Supertrend generates signals
- [ ] ADX generates signals

#### Backtesting
- [ ] Engine runs without errors
- [ ] Calculates all metrics correctly
- [ ] Handles edge cases (few trades, no signals)
- [ ] Equity curve generates

#### Optimization
- [ ] Parameter optimization finds best params
- [ ] Strategy comparison ranks correctly
- [ ] Results are reproducible
- [ ] Export to CSV works

#### Screening
- [ ] Scans multiple stocks
- [ ] Filters by confidence/signal type
- [ ] Groups results correctly
- [ ] Export works

#### UI (Streamlit)
- [ ] All pages load
- [ ] Dashboard shows signals
- [ ] Backtesting runs successfully
- [ ] Optimization tabs work
- [ ] Screener finds signals
- [ ] Charts render correctly
- [ ] CSV downloads work

---

### 8. Performance Benchmarks

Expected performance for reference:

| Task | Time | Notes |
|------|------|-------|
| Single strategy analysis | < 1s | 1 year data, 1 stock |
| Backtest (2 years) | < 2s | 1 strategy, 1 stock |
| Parameter optimization | 5-30s | Depends on combinations |
| Strategy comparison (4 strategies) | 5-10s | 2 years data |
| Screener (10 stocks, all strategies) | 15-30s | 1 year lookback |
| Screener (NIFTY 50, all strategies) | 60-120s | 1 year lookback |

**Note**: Times may vary based on network speed (data fetching) and system performance.

---

### 9. Troubleshooting Tests

#### Test Fails with "No data fetched"

**Cause**: Network issue or invalid symbol

**Solution**:
```bash
# Test data fetching directly
python -c "
import yfinance as yf
data = yf.Ticker('RELIANCE.NS').history(period='1y')
print(f'Fetched {len(data)} rows')
print(data.head())
"
```

#### Test Shows No Signals

**Cause**: Strategy parameters too strict or insufficient data

**Solution**:
- Use 2+ years of data
- Adjust strategy parameters
- Try different stock (some are more volatile)

#### Optimization Returns Empty Results

**Cause**: `min_trades` threshold too high

**Solution**:
- Reduce `min_trades` to 3-5
- Use longer time period
- Widen parameter ranges

#### Screener is Slow

**Cause**: Scanning too many stocks/strategies

**Solution**:
- Reduce lookback_days to 180
- Scan fewer stocks initially
- Select specific strategies instead of all

---

### 10. Automated Test Suite

Create a comprehensive test file:

```bash
cat > run_all_tests.py << 'EOF'
"""
Comprehensive test suite for all features
Run with: python run_all_tests.py
"""
import yfinance as yf
from src.strategies.technical import RSIStrategy, MACDStrategy
from src.backtesting.engine import BacktestEngine
from src.backtesting.optimizer import ParameterOptimizer
from src.backtesting.comparator import StrategyComparator
from src.screener import StockScreener

def test_strategy():
    """Test 1: Strategy generates signals"""
    print("\n" + "="*60)
    print("TEST 1: Strategy Signal Generation")
    print("="*60)

    data = yf.Ticker('RELIANCE.NS').history(period='1y')
    data.columns = data.columns.str.lower()

    strategy = RSIStrategy()
    signals = strategy.analyze(data)

    assert len(signals) > 0, "No signals generated!"
    assert signals[-1].signal_type in ['BUY', 'SELL', 'HOLD'], "Invalid signal type!"

    print(f"✅ PASSED: Generated {len(signals)} signals")
    return True

def test_backtest():
    """Test 2: Backtesting engine"""
    print("\n" + "="*60)
    print("TEST 2: Backtesting Engine")
    print("="*60)

    data = yf.Ticker('TCS.NS').history(period='2y')
    data.columns = data.columns.str.lower()

    engine = BacktestEngine(initial_capital=100000)
    results = engine.run(data, RSIStrategy())

    assert 'total_return_pct' in results, "Missing return metric!"
    assert 'sharpe_ratio' in results, "Missing sharpe ratio!"
    assert results['total_trades'] >= 0, "Invalid trade count!"

    print(f"✅ PASSED: Backtest completed with {results['total_trades']} trades")
    return True

def test_optimization():
    """Test 3: Parameter optimization"""
    print("\n" + "="*60)
    print("TEST 3: Parameter Optimization")
    print("="*60)

    data = yf.Ticker('INFY.NS').history(period='2y')
    data.columns = data.columns.str.lower()

    optimizer = ParameterOptimizer(
        strategy_class=RSIStrategy,
        data=data,
        optimization_metric='sharpe_ratio'
    )

    results = optimizer.optimize(
        {'period': [14, 20], 'oversold': [30], 'overbought': [70]},
        min_trades=3
    )

    assert len(results) > 0, "No optimization results!"
    assert results[0].params is not None, "Missing parameters!"

    print(f"✅ PASSED: Found {len(results)} valid parameter combinations")
    return True

def test_comparison():
    """Test 4: Strategy comparison"""
    print("\n" + "="*60)
    print("TEST 4: Strategy Comparison")
    print("="*60)

    data = yf.Ticker('HDFCBANK.NS').history(period='2y')
    data.columns = data.columns.str.lower()

    comp = StrategyComparator(data=data)
    comp.add_strategy(RSIStrategy())
    comp.add_strategy(MACDStrategy())

    assert len(comp.results) == 2, "Wrong number of results!"

    best = comp.get_best_strategy('sharpe_ratio')
    assert best is not None, "No best strategy found!"

    print(f"✅ PASSED: Compared 2 strategies, winner: {best.strategy_name}")
    return True

def test_screener():
    """Test 5: Stock screener"""
    print("\n" + "="*60)
    print("TEST 5: Stock Screener")
    print("="*60)

    screener = StockScreener(lookback_days=365, min_confidence=0)

    results = screener.scan(
        stock_symbols=['RELIANCE', 'TCS', 'INFY'],
        strategy_names=['rsi_strategy']
    )

    assert isinstance(results, list), "Results not a list!"

    summary = screener.get_summary()
    assert summary['total_signals'] >= 0, "Invalid signal count!"

    print(f"✅ PASSED: Screener found {len(results)} signals")
    return True

# Run all tests
if __name__ == '__main__':
    print("\n" + "="*60)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("="*60)

    tests = [
        test_strategy,
        test_backtest,
        test_optimization,
        test_comparison,
        test_screener
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
EOF

# Run the test suite
python run_all_tests.py
```

**Expected Output**: All 5 tests should pass.

---

## Next Steps

### Recommended Next Phase

**Phase 4 - Portfolio & Risk Management** (Highly Recommended):
- Position sizing (Kelly Criterion, fixed fractional, risk-based)
- Stop-loss and take-profit rules
- Multi-stock portfolio tracking
- Drawdown protection and circuit breakers
- Portfolio-level metrics and dashboard
- **Why**: Complete the trading workflow with proper risk management

### Alternative Phases

**Phase 5 - Real-time & Alerts**:
- Live data integration during market hours
- Email/Telegram/WhatsApp alerts for new signals
- Watchlist monitoring with auto-refresh
- Desktop notifications
- **Why**: Makes application production-ready for live trading

**Phase 6 - Sentiment Analysis**:
- Position sizing (Kelly Criterion, fixed fractional)
- Stop-loss and take-profit rules
- Multi-stock portfolio management
- Drawdown protection
- Portfolio dashboard

**Phase 5 - Sentiment Analysis**:
- News API integration
- Basic sentiment scoring
- News feed per stock

**Phase 2.5 - Fundamental Analysis**:
- P/E, P/B ratios
- Financial statements
- Earnings data
- Fundamental screener

### Phase 3 - Advanced Features

- Real-time data (Upstox/Zerodha APIs)
- Intraday strategies (1m, 5m, 15m)
- Advanced backtesting with fees/slippage
- Paper trading
- Alert system
- Multi-timeframe analysis
- Portfolio tracking

---

## Quick Reference Commands

```bash
# Setup
./setup.sh                 # Initial setup
python test_setup.py       # Verify setup

# Run Application
source venv/bin/activate   # Activate environment
streamlit run src/presentation/streamlit_app/app.py

# NSE Data Updates
python scripts/nse_data_updater.py --once       # Run once
python scripts/nse_data_updater.py              # Scheduled service

# Database (optional)
python scripts/setup_db.py       # Create database
python scripts/seed_nifty50.py   # Seed stocks

# Development
pip install -r requirements.txt  # Install dependencies
python -m pytest                 # Run tests (when available)

# Logs
tail -f logs/nse_updater.log    # Monitor NSE updater
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `config.py` | Central configuration |
| `.env` | Environment variables |
| `requirements.txt` | Python dependencies |
| `src/data/adapters/adapter_factory.py` | Data source selection |
| `src/strategies/registry.py` | Strategy management |
| `src/presentation/streamlit_app/pages/01_dashboard.py` | Main UI |
| `scripts/nse_data_updater.py` | NSE data automation |
| `database/schema.sql` | Database schema |
| `INDIAN_MARKET_ANALYSIS_ROADMAP.md` | Complete 3-phase plan |

---

## Troubleshooting

### App Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.13+

# Reinstall dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify setup
python test_setup.py
```

### NSE Data Not Available

- NSE has anti-bot measures (403 errors are common)
- Try running during off-market hours (after 6 PM IST)
- Check NSE website is accessible
- Review logs: `tail -f logs/nse_updater.log`

### Database Connection Errors

```bash
# Check PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Verify DATABASE_URL in .env
# Format: postgresql://user:password@localhost:5432/dbname
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify you're in project root
pwd  # Should be /path/to/finance
```

---

## Getting Help

1. Check this guide first
2. Review `INDIAN_MARKET_ANALYSIS_ROADMAP.md` for detailed specs
3. Check `QUICKSTART.md` for setup issues
4. Review logs in `logs/` directory
5. Run `python test_setup.py` to diagnose issues

---

## Development Notes

**Adding New Strategies**:

```python
# 1. Create file: src/strategies/technical/my_strategy.py
from ..base import BaseStrategy, Signal
from ..registry import register_strategy

@register_strategy('my_strategy')
class MyStrategy(BaseStrategy):
    def analyze(self, data):
        # Your logic
        return [Signal(...)]

    def get_default_params(self):
        return {'param1': 10}

# 2. Import in src/strategies/technical/__init__.py
from .my_strategy import MyStrategy

# 3. Strategy auto-registered and available in UI!
```

**Adding New Data Sources**:

```python
# 1. Create: src/data/adapters/new_adapter.py
from .base_adapter import BaseDataAdapter

class NewAdapter(BaseDataAdapter):
    def get_historical_data(self, symbol, start, end, timeframe):
        # Fetch from API
        # Return standardized DataFrame
        pass

    def get_supported_timeframes(self):
        return ['1m', '5m', '1h', '1d']

    # Implement other abstract methods...

# 2. Register in adapter_factory.py
_adapters = {
    'yahoo': YahooFinanceAdapter,
    'nse': NSEAdapter,
    'new': NewAdapter,  # Add here
}

# 3. Update timeframe priorities
_timeframe_priority = {
    '1m': ['new', 'upstox'],  # New adapter preferred
    '1d': ['yahoo', 'nse'],
}
```

---

## Summary

✅ **Phase 1 Complete**: MVP with Yahoo Finance, 3 strategies, backtesting
✅ **Phase 2.1 Complete**: NSE integration with FII/DII and delivery data
🚀 **Next**: Phase 2.2 - Add 5-7 more technical strategies

**Access**: http://localhost:8501

**For detailed Phase 2 implementation plan**, see `INDIAN_MARKET_ANALYSIS_ROADMAP.md`
