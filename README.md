# Indian Stock Market Analysis Application

A comprehensive stock market analysis platform for Indian markets (NSE/BSE) with multiple trading strategies, backtesting, and visualization capabilities.

## Features

### Phase 1 (MVP - Current)
- ✅ 3 Core Trading Strategies (SMA Crossover, RSI, VWAP)
- ✅ Yahoo Finance Data Integration
- ✅ Daily Timeframe Analysis
- ✅ Interactive Streamlit Dashboard
- ✅ Backtesting Engine
- ✅ NIFTY 50 Stock Support

### Phase 2 (Planned)
- 🔄 NSE India Integration (FII/DII, Delivery %)
- 🔄 5+ Additional Strategies
- 🔄 Fundamental Analysis
- 🔄 Stock Screener
- 🔄 Basic Sentiment Analysis

### Phase 3 (Planned)
- 🔄 Real-time Intraday Data
- 🔄 Multiple Timeframes (1m, 5m, 15m, 1h)
- 🔄 Advanced Backtesting Metrics
- 🔄 Real-time Alerts

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- TA-Lib (system package)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd finance
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install TA-Lib (system dependency)**

**macOS:**
```bash
brew install ta-lib
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ta-lib
```

**Windows:**
Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

4. **Install Python dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. **Set up PostgreSQL database**
```bash
# Create database
createdb market_analysis

# Run schema
psql -d market_analysis -f database/schema.sql
```

7. **Seed NIFTY 50 stocks**
```bash
python scripts/seed_nifty50.py
```

8. **Run the application**
```bash
streamlit run src/presentation/streamlit_app/app.py
```

The application will open in your browser at http://localhost:8501

## Project Structure

```
indian-market-analysis/
├── src/
│   ├── presentation/        # Streamlit UI
│   ├── services/           # Business logic
│   ├── strategies/         # Trading strategies
│   ├── analysis/           # Analysis modules
│   ├── backtesting/        # Backtesting engine
│   ├── data/               # Data layer
│   │   ├── adapters/       # Data source adapters
│   │   ├── models/         # Database models
│   │   └── providers/      # Data providers
│   ├── utils/              # Utilities
│   └── visualization/      # Charts
├── database/               # Database schema & migrations
├── scripts/                # Setup & utility scripts
├── tests/                  # Tests
├── docs/                   # Documentation
├── config.py               # Configuration
└── requirements.txt        # Dependencies
```

## Usage

### Analyze a Stock

1. Navigate to the **Dashboard** page
2. Enter a stock symbol (e.g., RELIANCE, TCS, INFY)
3. Select a date range
4. Choose a trading strategy
5. Adjust strategy parameters
6. Click **Analyze**

### Run Backtesting

1. Navigate to the **Backtesting** page
2. Enter stock symbol
3. Select date range
4. Choose strategy
5. Set initial capital
6. Click **Run Backtest**

View detailed performance metrics, trade history, and P&L analysis.

## Configuration

Edit `config.py` or `.env` file to configure:

- Database connection
- Data source preferences
- API keys (for Phase 2+)
- Application settings

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### Adding a New Strategy

1. Create a new file in `src/strategies/technical/`
2. Extend `BaseStrategy` class
3. Implement `analyze()` method
4. Register in `StrategyRegistry`

See `INDIAN_MARKET_ANALYSIS_ROADMAP.md` for detailed guide.

## Architecture

The application uses a **Data Adapter Pattern** to abstract data sources, making it easy to swap between free (Yahoo Finance) and paid (Upstox/Zerodha) data providers without changing strategy code.

```
Strategies → Data Adapter Layer → Data Providers
                    ↕
              Database (PostgreSQL)
```

## Roadmap

See [INDIAN_MARKET_ANALYSIS_ROADMAP.md](INDIAN_MARKET_ANALYSIS_ROADMAP.md) for complete development roadmap.

## Tech Stack

- **Backend:** Python 3.10+, FastAPI
- **Frontend:** Streamlit
- **Database:** PostgreSQL + TimescaleDB
- **Data:** Yahoo Finance, NSE India
- **Analysis:** TA-Lib, pandas-ta
- **Visualization:** Plotly, mplfinance
- **Backtesting:** Backtrader

## Contributing

Contributions are welcome! Please read the roadmap document first.

## License

MIT License

## Disclaimer

This application is for educational and research purposes only. Not financial advice. Use at your own risk.

## Support

For issues and questions, refer to the troubleshooting section in `INDIAN_MARKET_ANALYSIS_ROADMAP.md`.
