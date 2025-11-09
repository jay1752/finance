# Quick Start Guide - Phase 1 MVP

## ✅ What's Been Built

Your **Indian Stock Market Analysis Application** is ready! Here's what you have:

### 🎯 Core Features
- ✅ **3 Trading Strategies**: SMA Crossover, RSI, VWAP
- ✅ **Data Layer**: Yahoo Finance integration with adapter pattern
- ✅ **Backtesting Engine**: Test strategies on historical data
- ✅ **Streamlit UI**: Interactive dashboard and analysis tools
- ✅ **Database**: PostgreSQL with TimescaleDB ready
- ✅ **Complete Architecture**: Modular, scalable, and extensible

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **PostgreSQL 14+**
3. **TA-Lib** (system package)

### Step 1: Install TA-Lib

**macOS:**
```bash
brew install ta-lib
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ta-lib
```

**Windows:**
Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

### Step 2: Set Up Virtual Environment

```bash
cd /Users/jd/personal/finance

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

Update this line in `.env`:
```bash
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/market_analysis
```

### Step 5: Set Up Database

```bash
# Create PostgreSQL database
createdb market_analysis

# Run database setup (creates tables)
python scripts/setup_db.py

# Seed NIFTY 50 stocks
python scripts/seed_nifty50.py
```

### Step 6: Run the Application

```bash
streamlit run src/presentation/streamlit_app/app.py
```

The app will open in your browser at http://localhost:8501

---

## 📊 Using the Application

### Analyze a Stock

1. Navigate to **Dashboard** page
2. Enter a stock symbol (e.g., `RELIANCE`, `TCS`, `INFY`)
3. Select date range (default: 1 year)
4. Choose a strategy (SMA Crossover, RSI, or VWAP)
5. Adjust strategy parameters in the sidebar
6. Click **🔍 Analyze**

You'll see:
- Interactive candlestick chart with buy/sell signals
- Signal summary and confidence scores
- Latest signal with details
- Downloadable signal history

### Run a Backtest

1. Navigate to **Backtesting** page
2. Enter stock symbol
3. Select date range (recommended: 1-2 years)
4. Set initial capital (default: ₹1,00,000)
5. Choose a strategy
6. Click **🚀 Run Backtest**

You'll see:
- Total return and win rate
- Detailed performance metrics
- Equity curve chart
- Trade-by-trade history
- Downloadable results

---

## 🎯 Supported Stock Symbols

Use NSE symbols **without** the `.NS` suffix:

**Blue Chips:** RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK
**Banking:** SBIN, KOTAKBANK, AXISBANK, INDUSINDBK
**IT:** INFY, TCS, WIPRO, TECHM, HCLTECH
**FMCG:** HINDUNILVR, ITC, NESTLEIND, BRITANNIA
**Auto:** MARUTI, TATAMOTORS, M&M, BAJAJ-AUTO

And 40+ more NIFTY 50 stocks!

---

## 📁 Project Structure

```
finance/
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
├── ROADMAP.md                   # Complete roadmap
├── README.md                    # Documentation
│
├── src/
│   ├── data/
│   │   ├── adapters/           # Data source adapters (KEY!)
│   │   ├── models/             # Database models
│   │   └── providers/          # Data providers
│   ├── strategies/
│   │   ├── base.py            # Base strategy class
│   │   ├── registry.py        # Strategy registry
│   │   └── technical/         # 3 strategies
│   ├── backtesting/           # Backtesting engine
│   ├── presentation/
│   │   └── streamlit_app/     # Streamlit UI
│   └── utils/                 # Utilities
│
├── database/
│   └── schema.sql             # Database schema
│
└── scripts/
    ├── setup_db.py            # Database setup
    └── seed_nifty50.py        # Seed data
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'talib'"

TA-Lib must be installed as a system package first (see Step 1).

### Issue: "Connection to database failed"

Check your `DATABASE_URL` in `.env` file. Make sure PostgreSQL is running:
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql
```

### Issue: "No data found for symbol"

- Make sure you're using NSE symbols (e.g., `RELIANCE`, not `RELIANCE.NS`)
- Check your internet connection (Yahoo Finance requires internet)
- Try a different stock symbol

### Issue: TimescaleDB extension error

If you see TimescaleDB errors, you can skip it for Phase 1:
1. Comment out the TimescaleDB lines in `database/schema.sql`
2. Re-run `python scripts/setup_db.py`

---

## 🎓 Learning Resources

### Understanding the Code

**Key Architectural Patterns:**

1. **Adapter Pattern** (`src/data/adapters/`)
   - Abstracts data sources
   - Makes it easy to swap Yahoo Finance → Upstox later
   - All strategies work with any data source

2. **Strategy Pattern** (`src/strategies/`)
   - Each strategy is a self-contained class
   - Easy to add new strategies
   - Strategies auto-register via decorator

3. **Repository Pattern** (`src/data/models/`)
   - Database access abstraction
   - SQLAlchemy ORM for type safety

### Example: Adding a New Strategy

See `INDIAN_MARKET_ANALYSIS_ROADMAP.md` for detailed guide.

---

## 📈 Next Steps - Phase 2

Once you're comfortable with Phase 1, refer to the roadmap for:

- NSE India integration (FII/DII data)
- 5+ additional strategies
- Fundamental analysis
- Stock screener
- Basic sentiment analysis

See `INDIAN_MARKET_ANALYSIS_ROADMAP.md` Section "Phase 2"

---

## 💡 Tips for Best Results

1. **Use sufficient data**: At least 100-200 days for daily analysis
2. **Test multiple strategies**: Different strategies work in different market conditions
3. **Adjust parameters**: Fine-tune for each stock
4. **Check confidence scores**: Higher confidence = more reliable signals
5. **Consider volume**: High volume signals are stronger

---

## 🐛 Found a Bug?

Check these first:
1. Latest code from repository
2. All dependencies installed correctly
3. Database is set up and running
4. Environment variables configured

Still having issues? Check the troubleshooting section in `ROADMAP.md`

---

## 📚 Documentation

- **Complete Roadmap**: `INDIAN_MARKET_ANALYSIS_ROADMAP.md`
- **Project README**: `README.md`
- **Code Comments**: All modules have detailed docstrings

---

## ⚖️ Disclaimer

This application is for **educational and research purposes only**.

**NOT financial advice. Trade at your own risk.**

Always do your own research and consult with a qualified financial advisor before making investment decisions.

---

## 🎉 You're Ready!

Run this command to start:

```bash
streamlit run src/presentation/streamlit_app/app.py
```

Happy analyzing! 📈
