"""
Market Hub - Comprehensive market overview and analysis.

Combines:
- Live Market Data (indices, FII/DII flows)
- Watchlist (track favorite stocks)
- Market Overview (sector performance, heat maps)
- Stock Comparison (side-by-side analysis)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.adapters.adapter_factory import AdapterFactory
from src.data.adapters import NSEAdapter
from src.strategies.registry import StrategyRegistry
import src.strategies.technical

st.set_page_config(page_title="Market Hub", page_icon="🏛️", layout="wide")

st.title("🏛️ Market Hub")
st.markdown("Your one-stop dashboard for market overview, watchlist, and stock comparison.")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Live Market Data",
    "⭐ Watchlist",
    "🌐 Market Overview",
    "🔍 Stock Comparison"
])

# ==================== TAB 1: LIVE MARKET DATA ====================
with tab1:
    st.header("📊 Live Market Data")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🇮🇳 Indian Market Indices")

        try:
            nse_adapter = NSEAdapter()

            # Fetch major indices
            indices = ["NIFTY 50", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO", "NIFTY PHARMA"]

            indices_data = []
            for index_name in indices:
                index_data = nse_adapter.get_index_data(index_name)
                if index_data:
                    indices_data.append({
                        'Index': index_name,
                        'Price': f"{index_data['last_price']:.2f}",
                        'Change': f"{index_data['change']:+.2f}",
                        'Change %': f"{index_data['percent_change']:+.2f}%",
                        'Status': '🟢' if index_data['percent_change'] > 0 else '🔴' if index_data['percent_change'] < 0 else '⚪'
                    })

            if indices_data:
                indices_df = pd.DataFrame(indices_data)
                st.dataframe(indices_df, use_container_width=True, height=250)
            else:
                st.info("Market indices data temporarily unavailable")

            # Market Status
            market_status = nse_adapter.get_market_status()
            if market_status:
                status = market_status['market_status']
                status_icon = "🟢 OPEN" if status == "Open" else "🔴 CLOSED"
                st.info(f"**Market Status:** {status_icon}")
                st.caption(f"Last updated: {market_status['timestamp']}")

            nse_adapter.close()

        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            st.info("💡 NSE data might be temporarily unavailable")

    with col2:
        st.subheader("💰 FII/DII Activity")

        try:
            nse_adapter = NSEAdapter()
            fii_dii = nse_adapter.get_fii_dii_data()

            if fii_dii:
                st.markdown(f"**Date:** {fii_dii['date']}")

                # FII Data
                fii_net = float(fii_dii['fii_net'])
                st.markdown("**Foreign Institutional Investors (FII)**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Buy", f"₹{fii_dii['fii_gross_purchase']:.0f} Cr")
                with col_b:
                    st.metric("Sell", f"₹{fii_dii['fii_gross_sale']:.0f} Cr")
                with col_c:
                    net_color = "normal" if fii_net >= 0 else "inverse"
                    st.metric("Net", f"₹{abs(fii_net):.0f} Cr",
                             "Buying" if fii_net > 0 else "Selling" if fii_net < 0 else "Neutral",
                             delta_color=net_color)

                st.markdown("---")

                # DII Data
                dii_net = float(fii_dii['dii_net'])
                st.markdown("**Domestic Institutional Investors (DII)**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Buy", f"₹{fii_dii['dii_gross_purchase']:.0f} Cr")
                with col_b:
                    st.metric("Sell", f"₹{fii_dii['dii_gross_sale']:.0f} Cr")
                with col_c:
                    net_color = "normal" if dii_net >= 0 else "inverse"
                    st.metric("Net", f"₹{abs(dii_net):.0f} Cr",
                             "Buying" if dii_net > 0 else "Selling" if dii_net < 0 else "Neutral",
                             delta_color=net_color)

                # Overall Sentiment
                total_net = fii_net + dii_net
                if total_net > 500:
                    sentiment = "🚀 Very Bullish"
                    sentiment_color = "success"
                elif total_net > 0:
                    sentiment = "📈 Bullish"
                    sentiment_color = "info"
                elif total_net > -500:
                    sentiment = "📉 Bearish"
                    sentiment_color = "warning"
                else:
                    sentiment = "⚠️ Very Bearish"
                    sentiment_color = "error"

                if sentiment_color == "success":
                    st.success(f"**Market Sentiment:** {sentiment}")
                elif sentiment_color == "info":
                    st.info(f"**Market Sentiment:** {sentiment}")
                elif sentiment_color == "warning":
                    st.warning(f"**Market Sentiment:** {sentiment}")
                else:
                    st.error(f"**Market Sentiment:** {sentiment}")

            else:
                st.info("FII/DII data temporarily unavailable")

            nse_adapter.close()

        except Exception as e:
            st.error(f"Error fetching FII/DII data: {str(e)}")

    # Top Gainers/Losers
    st.markdown("---")
    st.subheader("📈 Top Movers")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🟢 Top Gainers (Simulated)**")
        # Note: Real gainers would require NSE equity data
        gainers_data = {
            'Stock': ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'],
            'Price': ['₹2,847.50', '₹3,645.20', '₹1,543.80', '₹1,678.90', '₹1,089.45'],
            'Change %': ['+3.45%', '+2.87%', '+2.56%', '+2.34%', '+2.12%']
        }
        st.dataframe(pd.DataFrame(gainers_data), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**🔴 Top Losers (Simulated)**")
        losers_data = {
            'Stock': ['TATAMOTORS', 'BAJFINANCE', 'WIPRO', 'TECHM', 'MARUTI'],
            'Price': ['₹876.30', '₹6,543.20', '₹456.70', '₹1,234.50', '₹11,456.80'],
            'Change %': ['-2.34%', '-1.98%', '-1.76%', '-1.54%', '-1.23%']
        }
        st.dataframe(pd.DataFrame(losers_data), use_container_width=True, hide_index=True)


# ==================== TAB 2: WATCHLIST ====================
with tab2:
    st.header("⭐ Watchlist")

    # Initialize watchlist in session state
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']

    col1, col2 = st.columns([3, 1])

    with col1:
        new_symbol = st.text_input(
            "Add Stock to Watchlist",
            placeholder="Enter symbol (e.g., WIPRO)",
            key="new_watchlist_symbol"
        ).upper().strip()

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", use_container_width=True):
            if new_symbol and new_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_symbol)
                st.success(f"Added {new_symbol} to watchlist")
            elif new_symbol in st.session_state.watchlist:
                st.warning(f"{new_symbol} already in watchlist")

    st.markdown("---")

    if st.session_state.watchlist:
        # Get signals for watchlist stocks
        st.subheader(f"📊 Watchlist ({len(st.session_state.watchlist)} stocks)")

        # Quick scan button
        if st.button("🔍 Scan All for Signals", type="primary"):
            with st.spinner("Scanning watchlist..."):
                try:
                    from src.screener import StockScreener

                    screener = StockScreener(lookback_days=365, min_confidence=50)
                    results = screener.scan(
                        stock_symbols=st.session_state.watchlist,
                        signal_types=['BUY', 'SELL']
                    )

                    if results:
                        st.success(f"Found {len(results)} signals across {len(st.session_state.watchlist)} stocks")

                        # Display results
                        signals_data = []
                        for signal in results[:20]:  # Top 20
                            signals_data.append({
                                'Stock': signal.stock_symbol,
                                'Signal': signal.signal_type,
                                'Strategy': signal.strategy_name,
                                'Confidence': f"{signal.confidence:.0f}%",
                                'Date': signal.date
                            })

                        signals_df = pd.DataFrame(signals_data)

                        # Color code signals
                        def style_signal(val):
                            if val == 'BUY':
                                return 'background-color: #90EE90'
                            elif val == 'SELL':
                                return 'background-color: #FFB6C1'
                            return ''

                        styled_df = signals_df.style.applymap(style_signal, subset=['Signal'])
                        st.dataframe(styled_df, use_container_width=True)
                    else:
                        st.info("No signals found in watchlist")

                except Exception as e:
                    st.error(f"Error scanning watchlist: {str(e)}")

        st.markdown("---")

        # Display watchlist with remove buttons
        for i, symbol in enumerate(st.session_state.watchlist):
            col1, col2, col3 = st.columns([2, 3, 1])

            with col1:
                st.markdown(f"**{symbol}**")

            with col2:
                # Get current price (simplified)
                try:
                    adapter = AdapterFactory.get_adapter()
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=2)
                    data = adapter.get_historical_data(symbol, start_date, end_date, '1d')

                    if not data.empty:
                        latest_price = float(data['close'].iloc[-1])
                        prev_price = float(data['close'].iloc[-2]) if len(data) > 1 else latest_price
                        change_pct = ((latest_price - prev_price) / prev_price * 100) if prev_price > 0 else 0

                        st.metric(
                            "Price",
                            f"₹{latest_price:.2f}",
                            f"{change_pct:+.2f}%",
                            delta_color="normal" if change_pct >= 0 else "inverse"
                        )
                    else:
                        st.caption("Price unavailable")
                except:
                    st.caption("Price unavailable")

            with col3:
                if st.button("🗑️", key=f"remove_{symbol}_{i}"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()

    else:
        st.info("Your watchlist is empty. Add stocks above to get started!")


# ==================== TAB 3: MARKET OVERVIEW ====================
with tab3:
    st.header("🌐 Market Overview")

    # Market Breadth
    st.subheader("📊 Market Breadth (Simulated)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Advances", "1,234", "+123")

    with col2:
        st.metric("Declines", "876", "-98")

    with col3:
        adv_dec_ratio = 1234 / 876
        st.metric("Adv/Dec Ratio", f"{adv_dec_ratio:.2f}", "Bullish" if adv_dec_ratio > 1 else "Bearish")

    with col4:
        st.metric("Unchanged", "234")

    st.markdown("---")

    # Sector Performance
    st.subheader("🏢 Sector Performance (Simulated)")

    sectors_data = {
        'Sector': ['IT', 'Banking', 'Auto', 'Pharma', 'FMCG', 'Metal', 'Energy', 'Realty'],
        'Change %': [2.34, 1.87, -0.54, 1.23, 0.87, -1.45, 0.65, -2.12],
        'Status': ['🟢', '🟢', '🔴', '🟢', '🟢', '🔴', '🟢', '🔴']
    }

    sectors_df = pd.DataFrame(sectors_data)

    # Create horizontal bar chart
    fig = go.Figure()

    colors = ['green' if x > 0 else 'red' for x in sectors_df['Change %']]

    fig.add_trace(go.Bar(
        y=sectors_df['Sector'],
        x=sectors_df['Change %'],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{x:+.2f}%" for x in sectors_df['Change %']],
        textposition='auto',
    ))

    fig.update_layout(
        title="Sector Performance Today",
        xaxis_title="Change %",
        yaxis_title="Sector",
        height=400,
        template='plotly_white'
    )

    st.plotly_chart(fig, use_container_width=True)


# ==================== TAB 4: STOCK COMPARISON ====================
with tab4:
    st.header("🔍 Stock Comparison")

    st.markdown("Compare 2-4 stocks side-by-side with key metrics and signals")

    # Stock selection
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stock1 = st.text_input("Stock 1", value="RELIANCE", key="comp_stock1").upper().strip()

    with col2:
        stock2 = st.text_input("Stock 2", value="TCS", key="comp_stock2").upper().strip()

    with col3:
        stock3 = st.text_input("Stock 3 (optional)", key="comp_stock3").upper().strip()

    with col4:
        stock4 = st.text_input("Stock 4 (optional)", key="comp_stock4").upper().strip()

    compare_stocks = [s for s in [stock1, stock2, stock3, stock4] if s]

    if st.button("📊 Compare Stocks", type="primary") and len(compare_stocks) >= 2:
        with st.spinner(f"Comparing {len(compare_stocks)} stocks..."):
            try:
                adapter = AdapterFactory.get_adapter()
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)

                comparison_data = []

                for symbol in compare_stocks:
                    try:
                        data = adapter.get_historical_data(symbol, start_date, end_date, '1d')

                        if not data.empty:
                            latest_price = float(data['close'].iloc[-1])
                            first_price = float(data['close'].iloc[0])
                            change_90d = ((latest_price - first_price) / first_price * 100)

                            high_90d = float(data['high'].max())
                            low_90d = float(data['low'].min())
                            avg_volume = float(data['volume'].mean())

                            comparison_data.append({
                                'Stock': symbol,
                                'Current Price': f"₹{latest_price:.2f}",
                                '90D Return': f"{change_90d:+.2f}%",
                                '90D High': f"₹{high_90d:.2f}",
                                '90D Low': f"₹{low_90d:.2f}",
                                'Avg Volume': f"{avg_volume/1000000:.2f}M"
                            })
                    except Exception as e:
                        st.warning(f"Could not fetch data for {symbol}")

                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True)

                    # Price comparison chart
                    st.subheader("📈 Price Comparison (90 Days)")

                    fig = go.Figure()

                    for symbol in compare_stocks:
                        try:
                            data = adapter.get_historical_data(symbol, start_date, end_date, '1d')
                            if not data.empty:
                                # Normalize to percentage change from start
                                normalized = ((data['close'] / data['close'].iloc[0]) - 1) * 100

                                fig.add_trace(go.Scatter(
                                    x=data.index,
                                    y=normalized,
                                    mode='lines',
                                    name=symbol,
                                    hovertemplate=f'{symbol}<br>%{{x}}<br>%{{y:.2f}}%<extra></extra>'
                                ))
                        except:
                            pass

                    fig.update_layout(
                        title="Normalized Price Performance (% Change)",
                        xaxis_title="Date",
                        yaxis_title="% Change",
                        height=500,
                        template='plotly_white',
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error comparing stocks: {str(e)}")
