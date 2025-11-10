"""
Test 5paisa connection and data fetching.

This script verifies your 5paisa credentials and tests basic functionality.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_5paisa_connection():
    """Test 5paisa adapter connection and basic operations."""

    print("\n" + "=" * 60)
    print("🧪 Testing 5paisa Connection")
    print("=" * 60 + "\n")

    # Test 1: Load credentials
    print("📝 Test 1: Loading credentials...")
    try:
        from src.brokers.config import BrokerConfig

        config = BrokerConfig.from_env()
        print(f"✅ Credentials loaded")
        print(f"   App Name: {config.app_name}")
        print(f"   User ID: {config.user_id}")
        print(f"   Client Code: {config.client_code}")
        print(f"   Live Trading: {'ENABLED ⚠️' if config.enable_live_trading else 'DISABLED ✅'}")
        print(f"   Paper Trading: {'ENABLED ✅' if config.enable_paper_trading else 'DISABLED'}")
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        print("\n💡 Make sure you:")
        print("   1. Created .env file from .env.example")
        print("   2. Added your 5paisa credentials")
        print("   3. Saved the file")
        return False

    # Test 2: Connect to 5paisa
    print("\n📡 Test 2: Connecting to 5paisa...")
    try:
        from src.data.adapters import FivePaisaAdapter

        adapter = FivePaisaAdapter(config=config)

        if not adapter.client:
            print("❌ Failed to initialize client")
            return False

        print("✅ Connected to 5paisa successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Check:")
        print("   1. Internet connection")
        print("   2. 5paisa credentials are correct")
        print("   3. API access is enabled in your account")
        return False

    # Test 3: Get live price
    print("\n💰 Test 3: Fetching live price...")
    try:
        symbol = 'RELIANCE'
        price = adapter.get_current_price(symbol)

        if price:
            print(f"✅ Fetched live price for {symbol}: ₹{price:,.2f}")
        else:
            print(f"⚠️  Could not fetch price for {symbol}")
            print("   This might be normal if market is closed")
    except Exception as e:
        print(f"❌ Error fetching price: {e}")

    # Test 4: Get live quotes for multiple stocks
    print("\n📊 Test 4: Fetching live quotes...")
    try:
        symbols = ['RELIANCE', 'TCS', 'INFY']
        quotes = adapter.get_live_quotes(symbols)

        if quotes:
            print(f"✅ Fetched quotes for {len(quotes)} stocks:")
            for symbol, quote in quotes.items():
                ltp = quote.get('ltp', 'N/A')
                change_pct = quote.get('change_pct', 0)
                arrow = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
                print(f"   {arrow} {symbol}: ₹{ltp} ({change_pct:+.2f}%)")
        else:
            print("⚠️  No quotes returned (market might be closed)")
    except Exception as e:
        print(f"❌ Error fetching quotes: {e}")

    # Test 5: Get historical data
    print("\n📈 Test 5: Fetching historical data...")
    try:
        symbol = 'RELIANCE'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        data = adapter.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe='1d'
        )

        if not data.empty:
            print(f"✅ Fetched {len(data)} days of data for {symbol}")
            print(f"   Date range: {data.index[0]} to {data.index[-1]}")
            print(f"   Latest close: ₹{data['close'].iloc[-1]:,.2f}")
        else:
            print(f"⚠️  No historical data returned")
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        print(f"   Error details: {str(e)}")

    # Test 6: Test intraday data
    print("\n⏱️  Test 6: Fetching intraday data...")
    try:
        symbol = 'RELIANCE'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        data = adapter.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe='15min'
        )

        if not data.empty:
            print(f"✅ Fetched {len(data)} 15-minute bars for {symbol}")
        else:
            print(f"⚠️  No intraday data (market might be closed)")
    except Exception as e:
        print(f"⚠️  Intraday data test skipped: {str(e)}")

    # Final summary
    print("\n" + "=" * 60)
    print("✅ 5paisa Connection Test Complete!")
    print("=" * 60)

    print("\n📝 Next Steps:")
    print("   1. ✅ Connection working - you can now use 5paisa data")
    print("   2. Try the platform: streamlit run src/presentation/streamlit_app/app.py")
    print("   3. Go to Market Hub → Live Market Data to see real-time prices")
    print("   4. Use 5paisa data in backtesting and analysis")

    print("\n⚠️  Remember:")
    print("   - Keep ENABLE_LIVE_TRADING=false until ready")
    print("   - Test thoroughly in paper trading mode first")
    print("   - Review FIVEPAISA_SETUP.md for full documentation")

    return True


if __name__ == "__main__":
    try:
        success = test_5paisa_connection()

        if success:
            print("\n🎉 All systems ready!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check errors above.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
