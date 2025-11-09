"""
Main Streamlit application for Indian Stock Market Analysis.

Run with: streamlit run src/presentation/streamlit_app/app.py
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import to auto-register strategies
import src.strategies.technical

st.set_page_config(
    page_title="Indian Market Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Indian Stock Market Analysis Application - Phase 1 MVP"
    }
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Main page header
st.markdown('<h1 class="main-header">📈 Indian Stock Market Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyze stocks, backtest strategies, and make data-driven decisions</p>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/india.png", width=80)
    st.title("Navigation")

    st.markdown("""
    ### 📊 **Pages**
    - **Dashboard** - Analyze individual stocks
    - **Backtesting** - Test strategy performance
    - **Settings** - Configure application

    ### ℹ️ **Info**
    **Phase:** MVP (Phase 1)
    **Data Source:** Yahoo Finance (Free)
    **Strategies:** 3 (SMA, RSI, VWAP)
    **Timeframe:** Daily

    ---

    ### 🚀 **Quick Tips**
    1. Start with **Dashboard** to analyze a stock
    2. Use **Backtesting** to validate strategies
    3. Try different parameters for each strategy
    """)

    st.markdown("---")
    st.caption("💡 Built with Python & Streamlit")

# Main content - Home page
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📊 Strategies Available",
        value="3",
        delta="SMA, RSI, VWAP"
    )

with col2:
    st.metric(
        label="🏢 Stocks Supported",
        value="50+",
        delta="NIFTY 50 + More"
    )

with col3:
    st.metric(
        label="💰 Data Source",
        value="Free",
        delta="Yahoo Finance"
    )

st.markdown("---")

# Features section
st.subheader("✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📈 **Technical Analysis**
    - **SMA Crossover** - Classic trend-following strategy
    - **RSI** - Momentum-based mean reversion
    - **VWAP** - Volume-weighted price analysis

    ### 📊 **Visualization**
    - Interactive candlestick charts
    - Buy/sell signal overlays
    - Multiple timeframes (daily, weekly, monthly)
    """)

with col2:
    st.markdown("""
    ### 🔍 **Backtesting**
    - Historical strategy validation
    - Performance metrics (ROI, win rate, P&L)
    - Trade-by-trade analysis
    - Equity curve visualization

    ### 🎯 **Stock Analysis**
    - Real-time price data
    - Technical indicators
    - Signal confidence scores
    - Historical performance
    """)

st.markdown("---")

# Quick start guide
with st.expander("🚀 Quick Start Guide", expanded=False):
    st.markdown("""
    ### Getting Started

    #### 1. **Analyze a Stock**
    - Go to **Dashboard** (01_dashboard.py)
    - Enter a stock symbol (e.g., RELIANCE, TCS, INFY)
    - Select a date range
    - Choose a strategy and adjust parameters
    - Click **Analyze** to see signals

    #### 2. **Backtest a Strategy**
    - Go to **Backtesting** (03_backtesting.py)
    - Enter stock symbol
    - Select date range (recommended: 1-2 years)
    - Set initial capital
    - Click **Run Backtest** to see results

    #### 3. **Interpret Results**
    - **Green triangles** = Buy signals
    - **Red triangles** = Sell signals
    - **Confidence score** = Signal strength (0-100%)
    - **Win rate** = Percentage of profitable trades

    ### Supported Stock Symbols

    Use NSE symbols without .NS suffix:
    - **RELIANCE** - Reliance Industries
    - **TCS** - Tata Consultancy Services
    - **INFY** - Infosys
    - **HDFCBANK** - HDFC Bank
    - **ICICIBANK** - ICICI Bank
    - **SBIN** - State Bank of India
    - And more...

    ### Tips for Better Results

    1. **Use sufficient data** - At least 100-200 days for daily analysis
    2. **Test multiple strategies** - Different strategies work in different market conditions
    3. **Adjust parameters** - Fine-tune strategy parameters for each stock
    4. **Check confidence** - Higher confidence signals are more reliable
    5. **Consider volume** - High volume signals are stronger
    """)

# Roadmap section
with st.expander("🗺️ Roadmap", expanded=False):
    st.markdown("""
    ### Phase 1 (Current) - MVP ✅
    - [x] 3 core trading strategies
    - [x] Yahoo Finance integration
    - [x] Interactive dashboard
    - [x] Backtesting engine
    - [x] Daily timeframe analysis

    ### Phase 2 (Coming Soon) 🔄
    - [ ] NSE India integration (FII/DII data)
    - [ ] 5+ additional strategies
    - [ ] Fundamental analysis
    - [ ] Stock screener
    - [ ] Basic sentiment analysis

    ### Phase 3 (Planned) 🔮
    - [ ] Real-time intraday data
    - [ ] Multiple timeframes (1m, 5m, 15m, 1h)
    - [ ] Advanced metrics (Sharpe, Sortino)
    - [ ] Real-time alerts
    - [ ] Portfolio tracking
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Disclaimer:</strong> This application is for educational and research purposes only.
    Not financial advice. Trade at your own risk.</p>
    <p>📖 Refer to <code>INDIAN_MARKET_ANALYSIS_ROADMAP.md</code> for complete documentation</p>
</div>
""", unsafe_allow_html=True)
