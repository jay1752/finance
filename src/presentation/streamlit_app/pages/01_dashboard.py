"""
Stock Analysis Dashboard - Main analysis page.

Allows users to analyze any stock with different strategies.
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

st.set_page_config(page_title="Stock Dashboard", page_icon="📊", layout="wide")

st.title("📊 Stock Analysis Dashboard")
st.markdown("Analyze any stock with technical strategies and get trading signals.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Stock selection
    symbol = st.text_input(
        "Stock Symbol",
        value="RELIANCE",
        help="Enter NSE stock symbol (e.g., RELIANCE, TCS, INFY)"
    ).upper().strip()

    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )

    st.markdown("---")

    # Strategy selection
    strategies = StrategyRegistry.list_strategies()
    selected_strategy = st.selectbox(
        "Strategy",
        strategies,
        format_func=lambda x: x.replace('_', ' ').title()
    )

    # Get strategy info
    strategy_info = StrategyRegistry.get_strategy_info(selected_strategy)
    default_params = strategy_info['default_params']

    st.markdown("---")
    st.subheader("📊 Strategy Parameters")

    # Dynamic parameter inputs based on strategy
    params = {}

    if selected_strategy == 'sma_crossover':
        params['fast_period'] = st.slider(
            "Fast SMA Period",
            min_value=5,
            max_value=50,
            value=default_params['fast_period']
        )
        params['slow_period'] = st.slider(
            "Slow SMA Period",
            min_value=20,
            max_value=200,
            value=default_params['slow_period']
        )

    elif selected_strategy == 'rsi':
        params['period'] = st.slider(
            "RSI Period",
            min_value=5,
            max_value=30,
            value=default_params['period']
        )
        params['oversold'] = st.slider(
            "Oversold Threshold",
            min_value=20,
            max_value=40,
            value=default_params['oversold']
        )
        params['overbought'] = st.slider(
            "Overbought Threshold",
            min_value=60,
            max_value=80,
            value=default_params['overbought']
        )

    elif selected_strategy == 'vwap':
        params['period'] = st.slider(
            "VWAP Period",
            min_value=10,
            max_value=50,
            value=default_params['period']
        )
        params['threshold'] = st.slider(
            "Threshold (%)",
            min_value=0.1,
            max_value=2.0,
            value=default_params['threshold'],
            step=0.1
        )

    elif selected_strategy == 'macd':
        params['fast_period'] = st.slider(
            "Fast EMA Period",
            min_value=5,
            max_value=20,
            value=default_params['fast_period']
        )
        params['slow_period'] = st.slider(
            "Slow EMA Period",
            min_value=20,
            max_value=40,
            value=default_params['slow_period']
        )
        params['signal_period'] = st.slider(
            "Signal Period",
            min_value=5,
            max_value=15,
            value=default_params['signal_period']
        )
        params['min_histogram'] = st.slider(
            "Min Histogram",
            min_value=0.0,
            max_value=5.0,
            value=default_params['min_histogram'],
            step=0.1
        )

    elif selected_strategy == 'bollinger_bands':
        params['period'] = st.slider(
            "Period",
            min_value=10,
            max_value=30,
            value=default_params['period']
        )
        params['std_dev'] = st.slider(
            "Standard Deviation",
            min_value=1.0,
            max_value=3.0,
            value=default_params['std_dev'],
            step=0.5
        )
        params['oversold_threshold'] = st.slider(
            "Oversold Threshold",
            min_value=0.0,
            max_value=0.1,
            value=default_params['oversold_threshold'],
            step=0.01
        )
        params['overbought_threshold'] = st.slider(
            "Overbought Threshold",
            min_value=0.0,
            max_value=0.1,
            value=default_params['overbought_threshold'],
            step=0.01
        )

    elif selected_strategy == 'stochastic':
        params['k_period'] = st.slider(
            "%K Period",
            min_value=5,
            max_value=21,
            value=default_params['k_period']
        )
        params['d_period'] = st.slider(
            "%D Period",
            min_value=2,
            max_value=10,
            value=default_params['d_period']
        )
        params['oversold_level'] = st.slider(
            "Oversold Level",
            min_value=10.0,
            max_value=30.0,
            value=default_params['oversold_level']
        )
        params['overbought_level'] = st.slider(
            "Overbought Level",
            min_value=70.0,
            max_value=90.0,
            value=default_params['overbought_level']
        )

    elif selected_strategy == 'supertrend':
        params['period'] = st.slider(
            "ATR Period",
            min_value=5,
            max_value=20,
            value=default_params['period']
        )
        params['multiplier'] = st.slider(
            "ATR Multiplier",
            min_value=1.0,
            max_value=5.0,
            value=default_params['multiplier'],
            step=0.5
        )

    elif selected_strategy == 'adx':
        params['period'] = st.slider(
            "ADX Period",
            min_value=7,
            max_value=21,
            value=default_params['period']
        )
        params['adx_threshold'] = st.slider(
            "ADX Threshold",
            min_value=20.0,
            max_value=40.0,
            value=default_params['adx_threshold']
        )

    st.markdown("---")

    # Analyze button
    analyze_button = st.button(
        "🔍 Analyze",
        type="primary",
        use_container_width=True
    )

# Main content
if analyze_button:
    with st.spinner(f"Fetching data for {symbol}..."):
        try:
            # Fetch data using adapter
            adapter = AdapterFactory.get_adapter(timeframe='1d')
            data = adapter.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe='1d'
            )

            if data.empty:
                st.error(f"❌ No data found for {symbol}. Please check the symbol and try again.")
                st.stop()

            # Display basic metrics
            st.subheader(f"📈 {symbol}")

            col1, col2, col3, col4, col5 = st.columns(5)

            latest_price = float(data['close'].iloc[-1])
            prev_price = float(data['close'].iloc[-2]) if len(data) > 1 else latest_price
            change = latest_price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price > 0 else 0

            with col1:
                st.metric("Latest Price", f"₹{latest_price:.2f}", f"{change_pct:.2f}%")

            with col2:
                st.metric("High (Period)", f"₹{float(data['high'].max()):.2f}")

            with col3:
                st.metric("Low (Period)", f"₹{float(data['low'].min()):.2f}")

            with col4:
                avg_volume = float(data['volume'].mean())
                st.metric("Avg Volume", f"{avg_volume/1000000:.2f}M")

            with col5:
                st.metric("Data Points", len(data))

            st.markdown("---")

            # NSE-Specific Metrics (Indian Market Indicators)
            st.subheader("🇮🇳 NSE Market Indicators")

            # Fetch NSE data
            try:
                nse_adapter = NSEAdapter()

                col1, col2, col3 = st.columns(3)

                # FII/DII Data
                with col1:
                    with st.spinner("Fetching FII/DII data..."):
                        fii_dii = nse_adapter.get_fii_dii_data()

                    if fii_dii:
                        st.markdown("**📊 Institutional Activity**")
                        st.markdown(f"*Date: {fii_dii['date']}*")

                        # FII
                        fii_net = float(fii_dii['fii_net'])
                        fii_color = "🟢" if fii_net > 0 else "🔴" if fii_net < 0 else "⚪"
                        st.markdown(f"{fii_color} **FII Net:** ₹{abs(fii_net):.2f} Cr {'(Buying)' if fii_net > 0 else '(Selling)' if fii_net < 0 else ''}")

                        # DII
                        dii_net = float(fii_dii['dii_net'])
                        dii_color = "🟢" if dii_net > 0 else "🔴" if dii_net < 0 else "⚪"
                        st.markdown(f"{dii_color} **DII Net:** ₹{abs(dii_net):.2f} Cr {'(Buying)' if dii_net > 0 else '(Selling)' if dii_net < 0 else ''}")

                        # Total
                        total_net = fii_net + dii_net
                        total_color = "🟢" if total_net > 0 else "🔴" if total_net < 0 else "⚪"
                        st.markdown(f"{total_color} **Total Net:** ₹{abs(total_net):.2f} Cr")

                        # Sentiment indicator
                        if total_net > 500:
                            sentiment = "🚀 Very Bullish"
                        elif total_net > 0:
                            sentiment = "📈 Bullish"
                        elif total_net > -500:
                            sentiment = "📉 Bearish"
                        else:
                            sentiment = "⚠️ Very Bearish"
                        st.info(f"**Market Sentiment:** {sentiment}")
                    else:
                        st.warning("FII/DII data not available")

                # Delivery Percentage
                with col2:
                    with st.spinner(f"Fetching delivery data for {symbol}..."):
                        delivery = nse_adapter.get_delivery_percentage(symbol)

                    if delivery:
                        st.markdown(f"**📦 Delivery Analysis**")
                        st.markdown(f"*Date: {delivery['date']}*")

                        delivery_pct = float(delivery['delivery_percentage'])

                        # Delivery percentage with color coding
                        if delivery_pct >= 60:
                            pct_color = "🟢"
                            strength = "Strong"
                        elif delivery_pct >= 40:
                            pct_color = "🟡"
                            strength = "Moderate"
                        else:
                            pct_color = "🔴"
                            strength = "Weak"

                        st.markdown(f"{pct_color} **Delivery %:** {delivery_pct:.2f}%")
                        st.markdown(f"**Strength:** {strength}")

                        # Quantities
                        st.markdown(f"**Delivered:** {delivery['delivery_quantity']:,}")
                        st.markdown(f"**Traded:** {delivery['traded_quantity']:,}")

                        # Interpretation
                        if delivery_pct >= 60:
                            interpretation = "✅ Genuine buying interest"
                        elif delivery_pct >= 40:
                            interpretation = "⚖️ Mixed activity"
                        else:
                            interpretation = "⚠️ High speculation"
                        st.info(f"{interpretation}")
                    else:
                        st.warning(f"Delivery data not available for {symbol}")

                # Market Status
                with col3:
                    with st.spinner("Checking market status..."):
                        market_status = nse_adapter.get_market_status()

                    if market_status:
                        st.markdown("**🏛️ Market Status**")
                        status = market_status['market_status']
                        status_icon = "🟢" if status == "Open" else "🔴"

                        st.markdown(f"{status_icon} **Status:** {status}")
                        st.markdown(f"*As of {market_status['timestamp']}*")

                        # Index data
                        with st.spinner("Fetching NIFTY 50..."):
                            index_data = nse_adapter.get_index_data("NIFTY 50")

                        if index_data:
                            change_pct = float(index_data['percent_change'])
                            change_icon = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"

                            st.markdown(f"**NIFTY 50**")
                            st.markdown(f"{change_icon} {index_data['last_price']:.2f}")
                            st.markdown(f"{change_pct:+.2f}% ({index_data['change']:+.2f})")
                    else:
                        st.warning("Market status not available")

                # Close NSE adapter
                nse_adapter.close()

            except Exception as e:
                st.error(f"Error fetching NSE data: {str(e)}")
                st.info("💡 NSE data might be temporarily unavailable. Price analysis will continue.")

            st.markdown("---")

            # Run strategy analysis
            st.subheader(f"🎯 {strategy_info['description']}")

            with st.spinner("Analyzing..."):
                strategy = StrategyRegistry.get_strategy(selected_strategy, **params)
                signals = strategy.analyze(data.copy())

            # Display results
            col1, col2 = st.columns([2, 1])

            with col1:
                # Create candlestick chart
                st.subheader("📊 Price Chart with Signals")

                fig = go.Figure()

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name='Price',
                    increasing_line_color='green',
                    decreasing_line_color='red'
                ))

                # Add buy signals
                buy_signals = [s for s in signals if s.signal_type == 'BUY']
                if buy_signals:
                    fig.add_trace(go.Scatter(
                        x=[s.date for s in buy_signals],
                        y=[s.price for s in buy_signals],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up',
                            size=15,
                            color='green',
                            line=dict(width=2, color='darkgreen')
                        ),
                        name='Buy Signal',
                        text=[f"Confidence: {s.confidence}%" for s in buy_signals],
                        hovertemplate='<b>BUY</b><br>Date: %{x}<br>Price: ₹%{y:.2f}<br>%{text}<extra></extra>'
                    ))

                # Add sell signals
                sell_signals = [s for s in signals if s.signal_type == 'SELL']
                if sell_signals:
                    fig.add_trace(go.Scatter(
                        x=[s.date for s in sell_signals],
                        y=[s.price for s in sell_signals],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-down',
                            size=15,
                            color='red',
                            line=dict(width=2, color='darkred')
                        ),
                        name='Sell Signal',
                        text=[f"Confidence: {s.confidence}%" for s in sell_signals],
                        hovertemplate='<b>SELL</b><br>Date: %{x}<br>Price: ₹%{y:.2f}<br>%{text}<extra></extra>'
                    ))

                fig.update_layout(
                    title=f"{symbol} - {selected_strategy.replace('_', ' ').title()} Signals",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    height=600,
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified',
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📋 Signal Summary")

                # Signal counts
                signal_counts = strategy.get_signal_count()

                st.metric("Total Signals", len(signals))
                st.metric("🟢 Buy Signals", signal_counts['BUY'])
                st.metric("🔴 Sell Signals", signal_counts['SELL'])

                st.markdown("---")

                # Latest signal
                latest_signal = strategy.get_latest_signal()

                if latest_signal:
                    st.subheader("📌 Latest Signal")

                    if latest_signal.signal_type == 'BUY':
                        st.success(f"**🟢 {latest_signal.signal_type}**")
                    else:
                        st.error(f"**🔴 {latest_signal.signal_type}**")

                    st.write(f"**Date:** {latest_signal.date}")
                    st.write(f"**Price:** ₹{latest_signal.price:.2f}")

                    # Confidence progress bar
                    st.write(f"**Confidence:** {latest_signal.confidence}%")
                    st.progress(latest_signal.confidence / 100)

                    # Metadata
                    with st.expander("📊 Signal Details"):
                        for key, value in latest_signal.metadata.items():
                            if isinstance(value, float):
                                st.write(f"**{key.replace('_', ' ').title()}:** {value:.2f}")
                            else:
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                else:
                    st.info("No signals generated for this period.")

                st.markdown("---")

                # Recent signals
                st.subheader("📅 Recent Signals")

                if signals:
                    recent = signals[-5:][::-1]  # Last 5 signals, reversed

                    for signal in recent:
                        with st.container():
                            if signal.signal_type == 'BUY':
                                st.success(f"🟢 **BUY** - {signal.date}")
                            else:
                                st.error(f"🔴 **SELL** - {signal.date}")

                            st.caption(f"₹{signal.price:.2f} | Confidence: {signal.confidence}%")
                            st.markdown("---")
                else:
                    st.info("No signals in this period")

            # All signals table
            if signals:
                st.markdown("---")
                st.subheader("📋 All Signals")

                signals_df = pd.DataFrame([
                    {
                        'Date': s.date,
                        'Signal': s.signal_type,
                        'Price': f"₹{s.price:.2f}",
                        'Confidence': f"{s.confidence}%"
                    }
                    for s in signals
                ])

                st.dataframe(
                    signals_df,
                    use_container_width=True,
                    height=300
                )

                # Download button
                csv = signals_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Signals (CSV)",
                    data=csv,
                    file_name=f"{symbol}_{selected_strategy}_signals.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("📝 Error Details"):
                st.exception(e)

else:
    # Show instructions when not analyzing
    st.info("👈 **Configure parameters in the sidebar and click 'Analyze' to get started**")

    st.markdown("---")

    # Sample stocks
    st.subheader("💡 Popular NSE Stocks to Try")

    stocks = {
        "Blue Chips": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
        "Banking": ["SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK"],
        "IT": ["INFY", "TCS", "WIPRO", "TECHM", "HCLTECH"],
        "FMCG": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA"],
        "Auto": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO"],
    }

    for sector, symbols in stocks.items():
        with st.expander(f"🏢 {sector}"):
            st.write(", ".join(symbols))
