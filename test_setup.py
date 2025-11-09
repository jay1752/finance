"""
Test script to verify the setup.

Run with: python test_setup.py
"""
import sys
from pathlib import Path

print("=" * 60)
print("TESTING SETUP")
print("=" * 60)

# Test 1: Python version
print("\n1. Python Version:")
print(f"   ✓ Python {sys.version.split()[0]}")

# Test 2: Import config
try:
    from config import config
    print("\n2. Configuration:")
    print(f"   ✓ Config loaded successfully")
    print(f"   ✓ Database URL: {config.DATABASE_URL}")
    print(f"   ✓ Debug mode: {config.DEBUG}")
except Exception as e:
    print(f"\n2. Configuration:")
    print(f"   ✗ Error: {e}")

# Test 3: Database connection
try:
    from src.utils.database import engine
    print("\n3. Database Connection:")
    print(f"   ✓ Engine created")
    print(f"   ✓ URL: {engine.url}")

    # Try to connect
    with engine.connect() as conn:
        print(f"   ✓ Connection successful!")
except Exception as e:
    print(f"\n3. Database Connection:")
    print(f"   ✗ Error: {e}")
    print(f"   → Make sure PostgreSQL is running")
    print(f"   → Check DATABASE_URL in .env file")

# Test 4: Data adapters
try:
    from src.data.adapters import AdapterFactory
    adapters = AdapterFactory.list_adapters()
    print("\n4. Data Adapters:")
    print(f"   ✓ Adapter factory loaded")
    for name, info in adapters.items():
        print(f"   ✓ {name}: {info['supported_timeframes']}")
except Exception as e:
    print(f"\n4. Data Adapters:")
    print(f"   ✗ Error: {e}")

# Test 5: Strategies
try:
    from src.strategies.registry import StrategyRegistry
    import src.strategies.technical  # Auto-register strategies
    strategies = StrategyRegistry.list_strategies()
    print("\n5. Trading Strategies:")
    print(f"   ✓ Strategy registry loaded")
    for strategy in strategies:
        print(f"   ✓ {strategy}")
except Exception as e:
    print(f"\n5. Trading Strategies:")
    print(f"   ✗ Error: {e}")

# Test 6: TA-Lib
try:
    import talib
    print("\n6. TA-Lib:")
    print(f"   ✓ TA-Lib installed successfully")
    print(f"   ✓ Version: {talib.__version__}")
except ImportError as e:
    print(f"\n6. TA-Lib:")
    print(f"   ✗ TA-Lib not installed")
    print(f"   → Install with: brew install ta-lib (macOS)")
    print(f"   → Then: pip install TA-Lib")

# Test 7: Streamlit
try:
    import streamlit
    print("\n7. Streamlit:")
    print(f"   ✓ Streamlit installed")
    print(f"   ✓ Version: {streamlit.__version__}")
except ImportError:
    print(f"\n7. Streamlit:")
    print(f"   ✗ Streamlit not installed")
    print(f"   → Run: pip install streamlit")

# Test 8: Yahoo Finance
try:
    import yfinance as yf
    print("\n8. Yahoo Finance:")
    print(f"   ✓ yfinance installed")

    # Quick test fetch
    print("   ℹ Testing data fetch for RELIANCE...")
    ticker = yf.Ticker("RELIANCE.NS")
    data = ticker.history(period="5d")
    if not data.empty:
        print(f"   ✓ Data fetch successful! (got {len(data)} days)")
    else:
        print(f"   ⚠ Data fetch returned empty (might be weekend/market closed)")
except Exception as e:
    print(f"\n8. Yahoo Finance:")
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("SETUP TEST COMPLETE")
print("=" * 60)

print("\n📝 Next Steps:")
print("   1. Fix any errors shown above")
print("   2. Run: python scripts/setup_db.py (if DB test failed)")
print("   3. Run: python scripts/seed_nifty50.py")
print("   4. Run: streamlit run src/presentation/streamlit_app/app.py")

print("\n✅ If all tests passed, you're ready to go!")
