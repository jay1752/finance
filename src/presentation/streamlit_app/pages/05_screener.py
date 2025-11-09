"""
Stock Screener Page - Find opportunities across multiple stocks.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.screener import StockScreener
from src.strategies.registry import StrategyRegistry
import src.strategies.technical

st.set_page_config(page_title="Stock Screener", page_icon="🔍", layout="wide")

st.title("🔍 Stock Screener")
st.markdown("Scan multiple stocks with multiple strategies to find trading opportunities.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Screener Settings")

    # Stock selection method
    stock_input_method = st.radio(
        "Stock Selection",
        ["NIFTY 50", "Custom List", "Popular Stocks"]
    )

    # Stock list based on selection
    if stock_input_method == "NIFTY 50":
        # Use NIFTY 50 stocks
        stock_symbols = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
            'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA',
            'TITAN', 'BAJFINANCE', 'NESTLEIND', 'ULTRACEMCO', 'WIPRO',
            'ONGC', 'NTPC', 'POWERGRID', 'TECHM', 'HCLTECH',
            'M&M', 'TATAMOTORS', 'BAJAJFINSV', 'ADANIPORTS', 'TATASTEEL',
            'COALINDIA', 'INDUSINDBK', 'DRREDDY', 'DIVISLAB', 'BRITANNIA',
            'GRASIM', 'CIPLA', 'EICHERMOT', 'HEROMOTOCO', 'TATACONSUM',
            'APOLLOHOSP', 'JSWSTEEL', 'BPCL', 'HINDALCO', 'UPL',
            'SBILIFE', 'BAJAJ-AUTO', 'SHREECEM', 'TATAPOWER', 'ADANIENT'
        ]
        st.info(f"📊 Scanning all {len(stock_symbols)} NIFTY 50 stocks")

    elif stock_input_method == "Popular Stocks":
        default_popular = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
                          'BHARTIARTL', 'ITC', 'SBIN', 'WIPRO', 'LT']
        stock_symbols = st.multiselect(
            "Select Stocks",
            default_popular + ['MARUTI', 'TATAMOTORS', 'AXISBANK', 'KOTAKBANK', 'SUNPHARMA'],
            default=default_popular
        )
    else:  # Custom List
        stock_input = st.text_area(
            "Enter Stock Symbols (one per line)",
            value="RELIANCE\nTCS\nINFY\nHDFCBANK\nICICIBANK",
            height=150
        )
        stock_symbols = [s.strip().upper() for s in stock_input.split('\n') if s.strip()]

    st.markdown("---")

    # Strategy selection
    available_strategies = StrategyRegistry.list_strategies()
    selected_strategies = st.multiselect(
        "Select Strategies",
        available_strategies,
        default=available_strategies,
        format_func=lambda x: x.replace('_', ' ').title()
    )

    st.markdown("---")

    # Filters
    st.subheader("🔧 Filters")

    signal_filter = st.multiselect(
        "Signal Type",
        ['BUY', 'SELL'],
        default=['BUY', 'SELL']
    )

    min_confidence = st.slider(
        "Minimum Confidence (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5
    )

    lookback_days = st.selectbox(
        "Lookback Period",
        [180, 365, 730],
        index=1,
        format_func=lambda x: f"{x} days ({x//365} year{'s' if x > 365 else ''})"
    )

    st.markdown("---")

    # Scan button
    scan_button = st.button(
        "🔍 Scan Stocks",
        type="primary",
        use_container_width=True
    )

# Main content
if scan_button:
    if not stock_symbols:
        st.warning("⚠️ Please select at least one stock to scan.")
        st.stop()

    if not selected_strategies:
        st.warning("⚠️ Please select at least one strategy.")
        st.stop()

    with st.spinner(f"Scanning {len(stock_symbols)} stocks with {len(selected_strategies)} strategies..."):
        # Create screener
        screener = StockScreener(
            lookback_days=lookback_days,
            min_confidence=min_confidence
        )

        # Run scan
        results = screener.scan(
            stock_symbols=stock_symbols,
            strategy_names=selected_strategies,
            signal_types=signal_filter if signal_filter else None
        )

    st.success(f"✅ Scan complete! Found {len(results)} signals.")

    # Summary metrics
    st.subheader("📊 Summary")

    summary = screener.get_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Signals", summary['total_signals'])
    with col2:
        st.metric("BUY Signals", summary['buy_signals'], delta=None, delta_color="normal")
    with col3:
        st.metric("SELL Signals", summary['sell_signals'], delta=None, delta_color="inverse")
    with col4:
        st.metric("Avg Confidence", f"{summary['avg_confidence']:.1f}%")

    st.markdown("---")

    # Display results
    if results:
        # Results table
        st.subheader("📋 Screening Results")

        df = screener.get_results_dataframe()

        # Format the dataframe for display
        display_df = df.copy()
        display_df = display_df[[
            'stock_symbol', 'strategy_name', 'signal_type',
            'price', 'confidence', 'signal_date'
        ]]

        # Rename columns
        display_df.columns = ['Stock', 'Strategy', 'Signal', 'Price (₹)', 'Confidence (%)', 'Date']

        # Style the dataframe
        def highlight_signal(row):
            if row['Signal'] == 'BUY':
                return ['background-color: #d4edda'] * len(row)
            elif row['Signal'] == 'SELL':
                return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)

        styled_df = display_df.style.apply(highlight_signal, axis=1).format({
            'Price (₹)': '₹{:,.2f}',
            'Confidence (%)': '{:.1f}%'
        })

        st.dataframe(styled_df, use_container_width=True, height=400)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"screener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        st.markdown("---")

        # Top signals
        st.subheader("🏆 Top Signals")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top 5 BUY Signals**")
            top_buys = screener.get_top_signals(5, 'BUY')

            if top_buys:
                for i, result in enumerate(top_buys, 1):
                    with st.container():
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                        st.write(f"{medal} **{result.stock_symbol}**")
                        st.write(f"   Strategy: {result.strategy_name}")
                        st.write(f"   Price: ₹{result.price:,.2f}")
                        st.write(f"   Confidence: {result.confidence:.1f}%")
                        st.write(f"   Date: {result.signal_date}")
                        st.markdown("---")
            else:
                st.info("No BUY signals found")

        with col2:
            st.markdown("**Top 5 SELL Signals**")
            top_sells = screener.get_top_signals(5, 'SELL')

            if top_sells:
                for i, result in enumerate(top_sells, 1):
                    with st.container():
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                        st.write(f"{medal} **{result.stock_symbol}**")
                        st.write(f"   Strategy: {result.strategy_name}")
                        st.write(f"   Price: ₹{result.price:,.2f}")
                        st.write(f"   Confidence: {result.confidence:.1f}%")
                        st.write(f"   Date: {result.signal_date}")
                        st.markdown("---")
            else:
                st.info("No SELL signals found")

        # Analysis charts
        st.markdown("---")
        st.subheader("📈 Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Signals by strategy
            signals_by_strategy = screener.get_signals_by_strategy()
            strategy_counts = {
                name: len(signals)
                for name, signals in signals_by_strategy.items()
            }

            if strategy_counts:
                fig1 = go.Figure(data=[
                    go.Bar(
                        x=list(strategy_counts.keys()),
                        y=list(strategy_counts.values()),
                        marker_color='lightblue'
                    )
                ])
                fig1.update_layout(
                    title="Signals by Strategy",
                    xaxis_title="Strategy",
                    yaxis_title="Signal Count",
                    height=350
                )
                st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # BUY vs SELL distribution
            buy_count = summary['buy_signals']
            sell_count = summary['sell_signals']

            fig2 = go.Figure(data=[
                go.Pie(
                    labels=['BUY', 'SELL'],
                    values=[buy_count, sell_count],
                    marker_colors=['#28a745', '#dc3545']
                )
            ])
            fig2.update_layout(
                title="Signal Type Distribution",
                height=350
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Stocks with most signals
        st.subheader("🎯 Most Active Stocks")
        signals_by_stock = screener.get_signals_by_stock()
        stock_counts = {
            symbol: len(signals)
            for symbol, signals in signals_by_stock.items()
        }

        # Sort by count
        sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        fig3 = go.Figure(data=[
            go.Bar(
                x=[s[0] for s in sorted_stocks],
                y=[s[1] for s in sorted_stocks],
                marker_color='orange'
            )
        ])
        fig3.update_layout(
            title="Top 10 Stocks by Signal Count",
            xaxis_title="Stock Symbol",
            yaxis_title="Signal Count",
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("ℹ️ No signals found matching your criteria. Try adjusting the filters.")

else:
    # Instructions when no scan has been run
    st.info("👈 Configure your screening parameters in the sidebar and click **Scan Stocks** to begin.")

    st.markdown("### 📚 How to Use")
    st.markdown("""
    1. **Choose stocks** - Select NIFTY 50, popular stocks, or enter custom symbols
    2. **Select strategies** - Choose which technical strategies to use
    3. **Set filters** - Configure signal type and minimum confidence
    4. **Scan** - Click the scan button to find opportunities
    5. **Analyze results** - View signals, charts, and export data
    """)

    st.markdown("### 💡 Tips")
    st.markdown("""
    - Use **minimum confidence** filter to focus on high-quality signals
    - Scan with **multiple strategies** to get diverse perspectives
    - **BUY signals** appear with green background, **SELL** with red
    - Download results as CSV for further analysis
    - Look for stocks with signals from multiple strategies (higher conviction)
    """)
