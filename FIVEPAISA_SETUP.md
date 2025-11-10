# 5paisa Integration Setup Guide

Complete guide to set up 5paisa broker integration for live data and trading.

---

## 📋 **Prerequisites**

1. ✅ **5paisa Demat Account**
   - Active trading account
   - Login credentials (User ID, Password, Client Code)

2. ✅ **5paisa API Access**
   - Developer API enabled
   - API credentials obtained

---

## 🔑 **Step 1: Get API Credentials**

### **Option A: Via 5paisa Website** (Recommended)

1. **Login** to 5paisa: https://login.5paisa.com/
2. **Navigate** to: My Account → Settings → Developer API
3. **Request** API access (if not already enabled)
4. **Copy** the following credentials:
   - **App Name**
   - **App Source**
   - **User Key**
   - **Encryption Key**
5. **Note** your:
   - **User ID** (your login ID)
   - **Password** (your login password)
   - **Client Code** (your trading code)

### **Option B: Contact Support**

If API is not enabled:
- Email: websupport@5paisa.com
- Phone: 022-40058296
- Request: "Please enable Developer API for my account"

---

## ⚙️ **Step 2: Configure Credentials**

### **2.1 Copy Environment File**

```bash
cd /Users/jd/personal/finance
cp .env.example .env
```

### **2.2 Edit .env File**

Open `.env` and add your credentials:

```env
# 5paisa API Credentials
FIVEPAISA_APP_NAME=your_actual_app_name
FIVEPAISA_APP_SOURCE=your_actual_app_source
FIVEPAISA_USER_ID=your_user_id
FIVEPAISA_PASSWORD=your_password
FIVEPAISA_USER_KEY=your_user_key
FIVEPAISA_ENCRYPTION_KEY=your_encryption_key
FIVEPAISA_CLIENT_CODE=your_client_code

# Safety Settings (IMPORTANT!)
ENABLE_LIVE_TRADING=false  # Keep false for testing!
ENABLE_PAPER_TRADING=true  # Safe for testing
```

**⚠️ IMPORTANT:**
- **NEVER** commit `.env` to git
- Keep `ENABLE_LIVE_TRADING=false` until fully tested
- `.env` is already in `.gitignore`

---

## ✅ **Step 3: Test Connection**

### **3.1 Run Connection Test**

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python scripts/test_5paisa_connection.py
```

**Expected Output:**
```
✅ 5paisa credentials loaded
✅ Connected to 5paisa successfully
✅ Fetched live price for RELIANCE: ₹2,847.50
✅ Historical data test passed
✅ All tests passed!
```

### **3.2 If Connection Fails**

**Error: "Invalid credentials"**
- Double-check all credentials in `.env`
- Ensure no extra spaces
- Verify API is enabled in 5paisa account

**Error: "Module not found"**
- Install dependencies: `pip install -r requirements.txt`

**Error: "Login failed"**
- Verify User ID and Password are correct
- Check if account is active
- Try logging in to 5paisa web/app first

---

## 📊 **Step 4: Use 5paisa in Your Platform**

### **4.1 Fetch Live Data**

```python
from src.data.adapters import FivePaisaAdapter

# Initialize adapter (loads credentials from .env)
adapter = FivePaisaAdapter()

# Get live price
price = adapter.get_current_price('RELIANCE')
print(f"RELIANCE: ₹{price}")

# Get historical data
from datetime import datetime, timedelta

data = adapter.get_historical_data(
    symbol='RELIANCE',
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    timeframe='1d'
)

print(data.tail())
```

### **4.2 Get Live Quotes for Multiple Stocks**

```python
# Get quotes for watchlist
quotes = adapter.get_live_quotes(['RELIANCE', 'TCS', 'INFY'])

for symbol, quote in quotes.items():
    print(f"{symbol}: ₹{quote['ltp']} ({quote['change_pct']}%)")
```

### **4.3 Use in Backtesting/Analysis**

The adapter automatically integrates with existing system:

```python
from src.data.adapters.adapter_factory import AdapterFactory

# Will automatically use 5paisa if available
adapter = AdapterFactory.get_adapter(timeframe='1d')

# Works exactly like before!
data = adapter.get_historical_data('RELIANCE', start, end, '1d')
```

---

## 🎨 **Step 5: Access Live Dashboard**

Once credentials are set up:

1. **Start Streamlit:**
   ```bash
   streamlit run src/presentation/streamlit_app/app.py
   ```

2. **Navigate to:**
   - **Market Hub** (Page 02) → Live Market Data tab
   - See real-time prices from 5paisa
   - View FII/DII flows
   - Monitor indices

---

## 🔒 **Security Best Practices**

### **DO ✅**
- Keep `.env` file secure and private
- Use strong, unique password
- Enable 2FA on 5paisa account
- Start with `ENABLE_LIVE_TRADING=false`
- Test thoroughly in paper trading mode
- Review all code before enabling live trading

### **DON'T ❌**
- Share your credentials with anyone
- Commit `.env` to git
- Enable live trading without testing
- Use same credentials on multiple systems
- Store credentials in code files

---

## 📈 **Supported Features**

### **✅ Phase 1 - Live Data (CURRENT)**
- Real-time price quotes
- Historical OHLCV data
- Intraday data (1min, 5min, 15min, 30min, 1h)
- Market depth
- Multi-stock quotes
- Better data quality than Yahoo for Indian stocks

### **🚧 Phase 2 - Paper Trading (NEXT)**
- Simulated order placement
- Virtual portfolio tracking
- Risk-free strategy testing
- Performance analysis

### **⏳ Phase 3 - Live Trading (FUTURE)**
- Real order placement
- Position management
- Auto-trading based on signals
- Risk management controls

---

## 🐛 **Troubleshooting**

### **"Scrip code not found for SYMBOL"**

**Solution:** Add the symbol to scrip_map in `fivepaisa_adapter.py`:

```python
scrip_map = {
    'YOUR_SYMBOL': scrip_code_number,  # Add here
    'RELIANCE': 2885,
    # ... existing mappings
}
```

Or use 5paisa scrip master:
```python
adapter = FivePaisaAdapter()
scrips = adapter.get_scrip_master()
print(scrips[scrips['Name'].str.contains('COMPANY_NAME')])
```

### **Data Quality Issues**

If Yahoo data is better for certain timeframes:
```python
# Force Yahoo instead of 5paisa
from src.data.adapters import YahooFinanceAdapter

adapter = YahooFinanceAdapter()
```

### **API Rate Limits**

5paisa has rate limits. If exceeded:
- Add delays between requests
- Cache data locally
- Contact 5paisa support for higher limits

---

## 📊 **Data Comparison: 5paisa vs Yahoo**

| Feature | 5paisa | Yahoo Finance |
|---------|--------|---------------|
| **Real-time quotes** | ✅ Yes | ❌ 15min delayed |
| **Intraday (1min-30min)** | ✅ Yes | ❌ No |
| **Historical daily** | ✅ Accurate | ✅ Good |
| **Corporate actions** | ✅ Accurate | ⚠️ Sometimes lagged |
| **NSE/BSE** | ✅ Both | ✅ Both |
| **Cost** | ✅ Free (with account) | ✅ Free |
| **Reliability** | ✅ High | ✅ High |
| **Best for** | Live trading, intraday | Backtesting, research |

**Recommendation:**
- Use **5paisa** for live data and trading
- Keep **Yahoo** as fallback for research/backtesting

---

## 🎯 **Next Steps**

1. ✅ **Test Connection** - Verify credentials work
2. ✅ **Try Live Quotes** - Get real-time prices
3. ✅ **Compare Data** - Test data quality vs Yahoo
4. ⏳ **Paper Trading** - Practice with virtual money (Phase 2)
5. ⏳ **Live Trading** - Real trading (Phase 3, after thorough testing)

---

## 📞 **Support**

**5paisa Support:**
- Website: https://www.5paisa.com/support
- Email: websupport@5paisa.com
- Phone: 022-40058296
- Timings: Mon-Sat, 9 AM - 6 PM

**Platform Issues:**
- Check: [PROJECT_GUIDE.md](PROJECT_GUIDE.md)
- GitHub: Create an issue with error details

---

## ⚠️ **Disclaimer**

- Trading involves risk. Use at your own discretion.
- Test thoroughly before live trading.
- This platform is for educational/personal use.
- Not financial advice.
- Verify all trades before execution.

---

**Ready to start? Run the test script:**
```bash
python scripts/test_5paisa_connection.py
```
