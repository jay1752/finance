# Quick Reference - Strategy Testing & Optimization

**Last Updated**: Phase 6 Complete (Sentiment Analysis)

---

## 🚀 Quick Commands

### Start Application
```bash
# Activate environment
source venv/bin/activate

# Run Streamlit
streamlit run src/presentation/streamlit_app/app.py
```

### Run Tests
```bash
# Quick test - Single strategy
python -c "
from src.strategies.technical import RSIStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='1y')
data.columns = data.columns.str.lower()

strategy = RSIStrategy()
signals = strategy.analyze(data)
print(f'Signals: {len(signals)}')
if signals:
    latest = signals[-1]
    print(f'Latest: {latest.signal_type} at ₹{latest.price:.2f} ({latest.confidence:.1f}%)')
"

# Quick test - Backtest
python -c "
from src.backtesting.engine import BacktestEngine
from src.strategies.technical import RSIStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

engine = BacktestEngine(initial_capital=100000)
results = engine.run(data, RSIStrategy())
print(f'Return: {results[\"total_return_pct\"]:.2f}%')
print(f'Sharpe: {results[\"sharpe_ratio\"]:.2f}')
print(f'Win Rate: {results[\"win_rate\"]:.1f}%')
print(f'Trades: {results[\"total_trades\"]}')
"

# Quick test - Optimize
python -c "
from src.backtesting.optimizer import ParameterOptimizer
from src.strategies.technical import RSIStrategy
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='2y')
data.columns = data.columns.str.lower()

optimizer = ParameterOptimizer(RSIStrategy, data, 'sharpe_ratio')
results = optimizer.optimize({'period': [14, 20], 'oversold': [30], 'overbought': [70]})
print(f'Best: {results[0].params}')
print(f'Sharpe: {results[0].metrics[\"sharpe_ratio\"]:.2f}')
"

# Quick test - Screener
python -c "
from src.screener import StockScreener

screener = StockScreener(lookback_days=365, min_confidence=50)
results = screener.scan(['RELIANCE', 'TCS', 'INFY'])
print(f'Found {len(results)} signals')
if results:
    top = screener.get_top_signals(3, 'BUY')
    for i, s in enumerate(top, 1):
        print(f'{i}. {s.stock_symbol} via {s.strategy_name} ({s.confidence:.0f}%)')
"

# Comprehensive test suite
python run_all_tests.py  # Run automated tests (see PROJECT_GUIDE.md for script)
```

---

## 💼 Portfolio & Risk Management

### Quick Portfolio Setup
```bash
# Test portfolio features
python -c "
from src.portfolio import Portfolio, PositionSizer, RiskManager

# Create portfolio
portfolio = Portfolio(100000, 'Test Portfolio')

# Calculate position size
sizer = PositionSizer(100000)
size = sizer.fixed_fractional(2847.50, stop_loss_pct=5.0)
print(f'Position Size: {size.shares} shares (₹{size.capital_allocation:,.0f})')

# Set risk management
risk_mgr = RiskManager()
stop = risk_mgr.fixed_stop_loss(2847.50, 5.0)
target = risk_mgr.risk_reward_take_profit(2847.50, stop.price, 2.0)
print(f'Stop: ₹{stop.price:.2f}, Target: ₹{target.price:.2f}')

# Add position
pos = portfolio.open_position('RELIANCE', size.shares, 2847.50, stop, target)
print(f'Position added: {pos.shares} shares')

# Check portfolio
summary = portfolio.get_summary()
print(f'Portfolio Value: ₹{summary[\"current_value\"]:,.0f}')
print(f'Risk: ₹{summary[\"total_risk\"]:,.0f}')
"
```

### Position Sizing Methods
```bash
# Kelly Criterion (for proven strategies)
python -c "from src.portfolio import PositionSizer; s = PositionSizer(100000); r = s.kelly_criterion(0.65, 8.5, 4.2, 2847.50, 0.25); print(f'{r.shares} shares, ₹{r.capital_allocation:,.0f}')"

# Fixed Fractional (recommended)
python -c "from src.portfolio import PositionSizer; s = PositionSizer(100000); r = s.fixed_fractional(2847.50, stop_loss_pct=5.0); print(f'{r.shares} shares, ₹{r.capital_allocation:,.0f}')"

# Risk-Based ATR
python -c "from src.portfolio import PositionSizer; s = PositionSizer(100000); r = s.risk_based(2847.50, atr=50.0, atr_multiplier=2.0); print(f'{r.shares} shares, ₹{r.capital_allocation:,.0f}')"
```

---

## 📰 Sentiment Analysis

### Quick Sentiment Tests
```bash
# Test single stock sentiment
python -c "
from src.sentiment import SentimentScorer

scorer = SentimentScorer(sentiment_method='vader')
sentiment = scorer.analyze_stock('RELIANCE', max_news=10)

print(f'Sentiment: {sentiment.overall_sentiment.upper()}')
print(f'Score: {sentiment.overall_score:.2f}')
print(f'Confidence: {sentiment.confidence:.2%}')
print(f'News Count: {sentiment.news_count}')

summary = scorer.get_sentiment_summary(sentiment)
print(f'Signal: {summary[\"signal\"]}')
print(f'Recommendation: {summary[\"recommendation\"]}')
"

# Compare multiple stocks
python -c "
from src.sentiment import SentimentScorer

scorer = SentimentScorer()
stocks = ['RELIANCE', 'TCS', 'INFY']
results = scorer.compare_stocks(stocks, max_news=10)

print('Sentiment Comparison:')
for sentiment in results:
    summary = scorer.get_sentiment_summary(sentiment)
    print(f'{sentiment.symbol:10} | {summary[\"signal\"]:4} | Score: {sentiment.overall_score:5.2f}')
"

# Find trending stocks
python -c "
from src.sentiment import NewsFetcher

fetcher = NewsFetcher()
trending = fetcher.get_trending_stocks(limit=5)

print('Trending Stocks (Most News):')
for stock in trending:
    print(f\"{stock['symbol']}: {stock['news_count']} articles\")
"
```

### Sentiment Analysis Methods

| Method | Best For | Accuracy | Speed |
|--------|----------|----------|-------|
| **VADER** ⭐ | Financial news | High | Fast |
| **TextBlob** | General text | Good | Fast |
| **Combined** | Conservative | Very Good | Medium |

### Sentiment Score Guide

- **BUY Signal**: Score > 0.3 (positive sentiment)
- **SELL Signal**: Score < -0.3 (negative sentiment)
- **HOLD Signal**: Everything else

**Confidence Levels**:
- High (0.6-1.0): Strong signal
- Moderate (0.3-0.6): Decent signal
- Low (0.0-0.3): Be cautious

### Combine Sentiment + Technical

```bash
# Example: RSI + Sentiment confirmation
python -c "
from src.strategy import StrategyRunner
from src.sentiment import SentimentScorer

symbol = 'RELIANCE'

# Technical analysis
runner = StrategyRunner()
tech_signals = runner.run_strategy('RSI', symbol)
rsi = tech_signals.get('rsi', 50)

# Sentiment analysis
scorer = SentimentScorer()
sentiment = scorer.analyze_stock(symbol, max_news=20, days_back=7)
summary = scorer.get_sentiment_summary(sentiment)

# Combined decision
print(f'{symbol} Analysis:')
print(f'RSI: {rsi:.1f}')
print(f'Sentiment: {sentiment.overall_sentiment.upper()} ({sentiment.overall_score:.2f})')
print(f'Signal: {summary[\"signal\"]}')

if rsi < 30 and summary['signal'] == 'BUY':
    print('✅ STRONG BUY: Oversold + Positive sentiment')
elif rsi > 70 and summary['signal'] == 'SELL':
    print('⛔ STRONG SELL: Overbought + Negative sentiment')
elif 30 <= rsi <= 70 and summary['signal'] == 'BUY':
    print('🟢 BUY: Positive sentiment, normal RSI')
else:
    print('⏸️ HOLD: Mixed signals or neutral')
"
```

---

## 📊 Available Strategies (8 Total)

| Strategy | Type | Best For | Key Parameters |
|----------|------|----------|----------------|
| **SMA Crossover** | Trend Following | Trending markets | fast_period, slow_period |
| **RSI** | Momentum | Overbought/Oversold | period, oversold, overbought |
| **VWAP** | Volume-based | Intraday/Volume analysis | period, threshold |
| **MACD** | Trend/Momentum | Trend changes | fast, slow, signal periods |
| **Bollinger Bands** | Volatility | Mean reversion | period, std_dev |
| **Stochastic** | Momentum | Range-bound markets | k_period, d_period, levels |
| **Supertrend** | Trend Following | Strong trends | period, multiplier |
| **ADX** | Trend Strength | Confirming trends | period, adx_threshold |

---

## 🎯 Optimization Cheat Sheet

### Parameter Optimization
```python
from src.backtesting.optimizer import ParameterOptimizer
from src.strategies.technical import RSIStrategy

param_ranges = {
    'period': [10, 14, 20],
    'oversold': [25, 30, 35],
    'overbought': [65, 70, 75]
}

optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=data,
    optimization_metric='sharpe_ratio'  # RECOMMENDED
)

results = optimizer.optimize(param_ranges, min_trades=5)
best = results[0]
```

### Strategy Comparison
```python
from src.backtesting.comparator import StrategyComparator

comparator = StrategyComparator(data=data)
comparator.add_strategy(RSIStrategy())
comparator.add_strategy(MACDStrategy())
comparator.add_strategy(BollingerBandsStrategy())

# Get winner
best = comparator.get_best_strategy('sharpe_ratio')
print(comparator.get_winner_summary())
```

---

## 📈 Metrics Guide

### Choose Your Optimization Metric

| Metric | Use When | Good Value |
|--------|----------|------------|
| **total_return_pct** | Maximum profit | > 20%/year |
| **sharpe_ratio** ⭐ | Balance risk/return | > 1.5 |
| **sortino_ratio** | Minimize downside | > 2.0 |
| **win_rate** | Consistency matters | > 55% |
| **profit_factor** | Risk management | > 1.5 |

**Recommendation**: Use `sharpe_ratio` for most cases

### Interpreting Results

**Excellent Strategy**:
- Return: > 25%/year
- Sharpe: > 2.0
- Win Rate: > 60%
- Max Drawdown: < 15%

**Good Strategy**:
- Return: 15-25%/year
- Sharpe: 1.0-2.0
- Win Rate: 50-60%
- Max Drawdown: 15-20%

**Marginal Strategy**:
- Return: 5-15%/year
- Sharpe: 0.5-1.0
- Win Rate: 40-50%
- Max Drawdown: 20-30%

---

## 🎨 Streamlit UI Guide

### Pages Overview

1. **Dashboard** (01_dashboard.py)
   - Analyze single stock with any strategy
   - Adjust parameters via sliders
   - View signals and charts

2. **Backtesting** (03_backtesting.py)
   - Test strategy on historical data
   - View performance metrics
   - Analyze trades

3. **Optimization** (04_optimization.py) ⭐ NEW
   - **Tab 1**: Compare multiple strategies
   - **Tab 2**: Optimize parameters

### Optimization Page Workflows

#### Compare Strategies
1. Select 2+ strategies
2. Choose stock and 2-year date range
3. Click "Compare Strategies"
4. View: Summary → Table → Charts → Rankings

#### Optimize Parameters
1. Select strategy (e.g., RSI)
2. Define parameter ranges
3. Choose metric (sharpe_ratio recommended)
4. Click "Run Optimization"
5. View best parameters and top 10 results

---

## 💡 Best Practices

### DO ✅
- Use 2+ years of data
- Optimize for Sharpe ratio
- Test top 3 parameter sets
- Verify with walk-forward analysis
- Check multiple metrics
- Compare similar strategy types

### DON'T ❌
- Optimize on < 1 year data
- Only look at returns
- Use first result blindly
- Over-optimize (too many parameters)
- Ignore max drawdown
- Skip out-of-sample testing

---

## 🔧 Common Parameter Ranges

### RSI
```python
{
    'period': [10, 12, 14, 16, 20],
    'oversold': [20, 25, 30, 35],
    'overbought': [65, 70, 75, 80]
}
```

### MACD
```python
{
    'fast_period': [8, 10, 12, 15],
    'slow_period': [20, 24, 26, 30],
    'signal_period': [7, 9, 11]
}
```

### SMA Crossover
```python
{
    'fast_period': [10, 15, 20, 25],
    'slow_period': [40, 50, 60, 70]
}
```

### Bollinger Bands
```python
{
    'period': [15, 20, 25],
    'std_dev': [1.5, 2.0, 2.5, 3.0]
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No valid results" | Reduce min_trades or use more data |
| Strategies perform similarly | Use longer period or different stock |
| Optimized params fail on new data | Overfit - use simpler ranges |
| High return, bad Sharpe | Too risky - check max drawdown |
| Streamlit shows old strategies | Restart Streamlit |

---

## 📝 Example Workflows

### Find Best Strategy for RELIANCE
```python
import yfinance as yf
from src.backtesting.comparator import StrategyComparator
from src.strategies.technical import *

# 1. Get data
data = yf.Ticker("RELIANCE.NS").history(period="2y")
data.columns = data.columns.str.lower()

# 2. Compare all
comp = StrategyComparator(data=data)
comp.add_strategy(RSIStrategy())
comp.add_strategy(MACDStrategy())
comp.add_strategy(BollingerBandsStrategy())
comp.add_strategy(SupertrendStrategy())

# 3. Get winner
best = comp.get_best_strategy('sharpe_ratio')
print(f"Winner: {best.strategy_name}")
print(comp.get_winner_summary())
```

### Optimize RSI for Maximum Sharpe
```python
from src.backtesting.optimizer import ParameterOptimizer

optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=data,
    optimization_metric='sharpe_ratio'
)

results = optimizer.optimize({
    'period': [10, 12, 14, 16, 20],
    'oversold': [25, 30, 35],
    'overbought': [65, 70, 75]
}, min_trades=10)

print(f"Best: {results[0].params}")
print(f"Sharpe: {results[0].metrics['sharpe_ratio']:.2f}")
print(f"Return: {results[0].metrics['total_return_pct']:.2f}%")
```

### Validate with Out-of-Sample Testing
```python
# Split data: 80% train, 20% test
split_point = int(len(data) * 0.8)
train_data = data.iloc[:split_point]
test_data = data.iloc[split_point:]

# 1. Optimize on training data
optimizer = ParameterOptimizer(
    strategy_class=RSIStrategy,
    data=train_data,
    optimization_metric='sharpe_ratio'
)
results = optimizer.optimize(param_ranges)
best_params = results[0].params

# 2. Test on unseen data
from src.backtesting.engine import BacktestEngine

strategy = RSIStrategy(**best_params)
engine = BacktestEngine()
test_results = engine.run(test_data, strategy)

# 3. Compare
train_return = results[0].metrics['total_return_pct']
test_return = test_results['total_return_pct']

print(f"Train: {train_return:.2f}%")
print(f"Test: {test_return:.2f}%")
print(f"Difference: {abs(train_return - test_return):.2f}%")

# Good if difference < 50% of train return
```

---

## ✅ Testing Guide

### Quick Verification Tests

**Test 1: Strategy Works**
```bash
python -c "from src.strategies.technical import RSIStrategy; import yfinance as yf; data = yf.Ticker('RELIANCE.NS').history(period='1y'); data.columns = data.columns.str.lower(); print(f'Signals: {len(RSIStrategy().analyze(data))}')"
```
Expected: `Signals: 10-20` (non-zero)

**Test 2: Backtesting Works**
```bash
python -c "from src.backtesting.engine import BacktestEngine; from src.strategies.technical import RSIStrategy; import yfinance as yf; data = yf.Ticker('TCS.NS').history(period='2y'); data.columns = data.columns.str.lower(); r = BacktestEngine().run(data, RSIStrategy()); print(f'Return: {r[\"total_return_pct\"]:.1f}%, Sharpe: {r[\"sharpe_ratio\"]:.2f}')"
```
Expected: Shows return % and Sharpe ratio

**Test 3: Optimization Works**
```bash
python -c "from src.backtesting.optimizer import ParameterOptimizer; from src.strategies.technical import RSIStrategy; import yfinance as yf; data = yf.Ticker('INFY.NS').history(period='2y'); data.columns = data.columns.str.lower(); results = ParameterOptimizer(RSIStrategy, data, 'sharpe_ratio').optimize({'period': [14, 20]}); print(f'Found {len(results)} results')"
```
Expected: `Found 2 results`

**Test 4: Screener Works**
```bash
python -c "from src.screener import StockScreener; results = StockScreener(365, 0).scan(['RELIANCE', 'TCS']); print(f'Signals: {len(results)}')"
```
Expected: `Signals: 5-15` (non-zero)

**Test 5: UI Works**
```bash
# Start app
streamlit run src/presentation/streamlit_app/app.py

# Then open http://localhost:8501
# Navigate to each page: Dashboard, Backtesting, Optimization, Screener
# Verify all pages load without errors
```

### Common Test Scenarios

**Scenario 1: Test New Strategy**
```bash
# 1. Quick signal test
python -c "from src.strategies.technical import MACDStrategy; import yfinance as yf; data = yf.Ticker('RELIANCE.NS').history(period='1y'); data.columns = data.columns.str.lower(); signals = MACDStrategy().analyze(data); print(f'{len(signals)} signals'); print(signals[-1] if signals else 'No signals')"

# 2. Backtest it
python -c "from src.backtesting.engine import BacktestEngine; from src.strategies.technical import MACDStrategy; import yfinance as yf; data = yf.Ticker('RELIANCE.NS').history(period='2y'); data.columns = data.columns.str.lower(); r = BacktestEngine().run(data, MACDStrategy()); print(f\"Return: {r['total_return_pct']:.2f}%, Sharpe: {r['sharpe_ratio']:.2f}, Trades: {r['total_trades']}\")"
```

**Scenario 2: Compare Multiple Strategies**
```bash
python -c "
from src.backtesting.comparator import StrategyComparator
from src.strategies.technical import RSIStrategy, MACDStrategy, BollingerBandsStrategy
import yfinance as yf

data = yf.Ticker('TCS.NS').history(period='2y')
data.columns = data.columns.str.lower()

comp = StrategyComparator(data=data)
comp.add_strategy(RSIStrategy())
comp.add_strategy(MACDStrategy())
comp.add_strategy(BollingerBandsStrategy())

best = comp.get_best_strategy('sharpe_ratio')
print(f'Winner: {best.strategy_name}')
print(f'Sharpe: {best.metrics[\"sharpe_ratio\"]:.2f}')
print(f'Return: {best.metrics[\"total_return_pct\"]:.2f}%')
"
```

**Scenario 3: Daily Screening Workflow**
```bash
python -c "
from src.screener import StockScreener

# Scan top stocks
screener = StockScreener(lookback_days=365, min_confidence=60)
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
results = screener.scan(stock_symbols=stocks, signal_types=['BUY'])

print(f'Found {len(results)} high-confidence BUY signals\n')

# Show top 3
for i, sig in enumerate(screener.get_top_signals(3, 'BUY'), 1):
    print(f'{i}. {sig.stock_symbol} - {sig.strategy_name} ({sig.confidence:.0f}%)')
"
```

### Validation Checklist

Run through this checklist to verify everything works:

**Strategies** (8 total):
```bash
# Test all strategies at once
python -c "
from src.strategies.technical import *
import yfinance as yf

data = yf.Ticker('RELIANCE.NS').history(period='1y')
data.columns = data.columns.str.lower()

strategies = [
    SMACrossoverStrategy(), RSIStrategy(), VWAPStrategy(), MACDStrategy(),
    BollingerBandsStrategy(), StochasticStrategy(), SupertrendStrategy(), ADXStrategy()
]

for s in strategies:
    signals = s.analyze(data)
    status = '✅' if len(signals) > 0 else '❌'
    print(f'{status} {s.name}: {len(signals)} signals')
"
```

**Full System Test**:
```bash
# Create comprehensive test file
cat > quick_test.py << 'EOF'
import yfinance as yf
from src.strategies.technical import RSIStrategy
from src.backtesting.engine import BacktestEngine
from src.backtesting.optimizer import ParameterOptimizer
from src.screener import StockScreener

print("Testing all features...")

# 1. Strategy
data = yf.Ticker('RELIANCE.NS').history(period='1y')
data.columns = data.columns.str.lower()
signals = RSIStrategy().analyze(data)
print(f"✅ Strategy: {len(signals)} signals")

# 2. Backtest
data2y = yf.Ticker('TCS.NS').history(period='2y')
data2y.columns = data2y.columns.str.lower()
results = BacktestEngine().run(data2y, RSIStrategy())
print(f"✅ Backtest: {results['total_return_pct']:.1f}% return")

# 3. Optimization
opt = ParameterOptimizer(RSIStrategy, data2y, 'sharpe_ratio')
opt_results = opt.optimize({'period': [14]})
print(f"✅ Optimization: {len(opt_results)} results")

# 4. Screener
screener = StockScreener(365, 0)
scan_results = screener.scan(['RELIANCE', 'TCS'])
print(f"✅ Screener: {len(scan_results)} signals")

print("\n🎉 All features working!")
EOF

python quick_test.py
```

### Troubleshooting

**Issue**: Tests fail with "No module named 'src'"
**Fix**:
```bash
# Make sure you're in project root
cd /Users/jd/personal/finance
# Activate venv
source venv/bin/activate
```

**Issue**: "No data fetched"
**Fix**:
```bash
# Test internet connection and yfinance
python -c "import yfinance as yf; print(yf.Ticker('RELIANCE.NS').history(period='1mo').head())"
```

**Issue**: Streamlit doesn't start
**Fix**:
```bash
# Reinstall streamlit
pip install --upgrade streamlit
# Check if port is available
lsof -ti:8501 | xargs kill -9  # Kill process on port 8501
streamlit run src/presentation/streamlit_app/app.py
```

---

## 📚 Further Reading

- **PROJECT_GUIDE.md** - Complete documentation
- **Phase 2.2** - Strategy details
- **Phase 2.3** - Advanced optimization
- **Testing & Optimization Guide** - In-depth workflows

---

## 🎯 Quick Tips

1. **Always optimize for Sharpe, not just return**
2. **Use at least 2 years of data**
3. **Test top 3 parameter combinations**
4. **Verify with walk-forward or out-of-sample**
5. **Check max drawdown before going live**
6. **Compare multiple strategies, not just one**
7. **Start simple, add complexity gradually**

---

**Need Help?** Check PROJECT_GUIDE.md → Testing & Optimization Guide section
