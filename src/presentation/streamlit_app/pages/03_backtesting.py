"""
Backtesting Page - Test strategy performance on historical data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.adapters.adapter_factory import AdapterFactory
from src.strategies.registry import StrategyRegistry
from src.backtesting.engine import BacktestEngine
import src.strategies.technical

st.set_page_config(page_title="Backtesting", page_icon="📉", layout="wide")

st.title("📉 Strategy Backtesting")
st.markdown("Test strategy performance on historical data to validate trading ideas.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Backtest Configuration")

    # Stock selection
    symbol = st.text_input(
        "Stock Symbol",
        value="RELIANCE",
        help="Enter NSE stock symbol"
    ).upper().strip()

    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=730),  # 2 years
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )

    st.markdown("---")

    # Initial capital
    initial_capital = st.number_input(
        "Initial Capital (₹)",
        min_value=10000,
        max_value=10000000,
        value=100000,
        step=10000,
        help="Starting capital for backtest"
    )

    st.markdown("---")

    # Strategy selection
    strategies = StrategyRegistry.list_strategies()
    selected_strategy = st.selectbox(
        "Strategy",
        strategies,
        format_func=lambda x: x.replace('_', ' ').title()
    )

    # Get strategy info for default params
    strategy_info = StrategyRegistry.get_strategy_info(selected_strategy)

    st.markdown("---")

    # Run button
    run_button = st.button(
        "🚀 Run Backtest",
        type="primary",
        use_container_width=True
    )

# Main content
if run_button:
    with st.spinner(f"Running backtest for {symbol}..."):
        try:
            # Fetch data
            adapter = AdapterFactory.get_adapter(timeframe='1d')
            data = adapter.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe='1d'
            )

            if data.empty:
                st.error(f"❌ No data found for {symbol}")
                st.stop()

            # Create strategy instance
            strategy = StrategyRegistry.get_strategy(selected_strategy)

            # Run backtest
            engine = BacktestEngine(initial_capital=initial_capital)
            results = engine.run(data, strategy)

            # Display results
            st.success("✅ Backtest completed!")

            # Key metrics
            st.subheader("📊 Performance Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                return_color = "normal" if results['total_return_pct'] >= 0 else "inverse"
                st.metric(
                    "Total Return",
                    f"₹{results['total_return']:,.2f}",
                    f"{results['total_return_pct']:.2f}%",
                    delta_color=return_color
                )

            with col2:
                st.metric(
                    "Win Rate",
                    f"{results['win_rate']:.1f}%"
                )

            with col3:
                st.metric(
                    "Total Trades",
                    results['total_trades']
                )

            with col4:
                st.metric(
                    "Final Capital",
                    f"₹{results['final_capital']:,.2f}"
                )

            st.markdown("---")

            # Detailed metrics
            st.subheader("📈 Detailed Metrics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### 🎯 Trade Statistics")
                st.write(f"**Winning Trades:** {results['winning_trades']}")
                st.write(f"**Losing Trades:** {results['losing_trades']}")
                st.write(f"**Win Rate:** {results['win_rate']:.2f}%")
                st.write(f"**Profit Factor:** {results['profit_factor']:.2f}")

            with col2:
                st.markdown("### 💰 Profit/Loss")
                st.write(f"**Average Profit:** ₹{results['avg_profit']:,.2f}")
                st.write(f"**Average Loss:** ₹{results['avg_loss']:,.2f}")
                st.write(f"**Max Profit:** ₹{results['max_profit']:,.2f}")
                st.write(f"**Max Loss:** ₹{results['max_loss']:,.2f}")

            with col3:
                st.markdown("### 📅 Period")
                st.write(f"**Start Date:** {results['start_date']}")
                st.write(f"**End Date:** {results['end_date']}")
                days = (datetime.strptime(results['end_date'], '%Y-%m-%d') -
                        datetime.strptime(results['start_date'], '%Y-%m-%d')).days
                st.write(f"**Duration:** {days} days")
                st.write(f"**Data Points:** {len(data)}")

            st.markdown("---")

            # Equity curve
            if results['trades']:
                st.subheader("📈 Equity Curve")

                equity_curve = engine.get_equity_curve()

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=equity_curve.index,
                    y=equity_curve['capital'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='blue', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.1)'
                ))

                # Add initial capital line
                fig.add_hline(
                    y=initial_capital,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Initial Capital",
                    annotation_position="right"
                )

                fig.update_layout(
                    title="Portfolio Value Over Time",
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value (₹)",
                    height=400,
                    hovermode='x unified',
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)

            # Trade history
            if results['trades']:
                st.markdown("---")
                st.subheader("📋 Trade History")

                trades_df = pd.DataFrame([
                    {
                        'Entry Date': t.entry_date,
                        'Exit Date': t.exit_date,
                        'Entry Price': f"₹{t.entry_price:.2f}",
                        'Exit Price': f"₹{t.exit_price:.2f}",
                        'Quantity': t.quantity,
                        'P&L': f"₹{t.profit_loss:,.2f}",
                        'P&L %': f"{t.profit_loss_pct:.2f}%",
                        'Type': t.trade_type
                    }
                    for t in results['trades']
                ])

                # Color code P&L
                def color_pnl(val):
                    if 'P&L' in val.name:
                        try:
                            num = float(val.str.replace('₹', '').str.replace(',', '').str.replace('%', ''))
                            color = ['background-color: lightgreen' if x >= 0 else 'background-color: lightcoral'
                                     for x in num]
                            return color
                        except:
                            return ['' for _ in val]
                    return ['' for _ in val]

                styled_df = trades_df.style.apply(color_pnl)

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=400
                )

                # Download button
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Trade History (CSV)",
                    data=csv,
                    file_name=f"{symbol}_{selected_strategy}_backtest.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ Error running backtest: {str(e)}")
            with st.expander("📝 Error Details"):
                st.exception(e)

else:
    # Show instructions
    st.info("👈 **Configure backtest parameters and click 'Run Backtest'**")

    st.markdown("---")

    # Tips
    st.subheader("💡 Backtesting Tips")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📊 **Data Requirements**
        - Use at least 1-2 years of data for reliable results
        - More data = more statistically significant results
        - Consider different market conditions (bull/bear markets)

        ### 🎯 **Interpreting Results**
        - **Win Rate > 50%** = Strategy wins more often than it loses
        - **Profit Factor > 1** = Average wins > average losses
        - **Total Return** = Overall profitability
        """)

    with col2:
        st.markdown("""
        ### ⚠️ **Important Notes**
        - Past performance doesn't guarantee future results
        - This backtest assumes perfect execution (no slippage)
        - No transaction costs included
        - Results may vary in live trading

        ### 🔍 **What to Look For**
        - Consistent performance across different periods
        - Reasonable number of trades (not too many/few)
        - Good risk/reward ratio
        """)

    st.markdown("---")

    # Strategy comparison
    with st.expander("📈 Strategy Comparison Guide"):
        st.markdown("""
        ### How Different Strategies Perform

        **SMA Crossover:**
        - Best in trending markets
        - May generate late signals
        - Good for long-term trends

        **RSI:**
        - Best in ranging/choppy markets
        - Good for catching reversals
        - Can give false signals in strong trends

        **VWAP:**
        - Good for intraday bias (with daily data)
        - Combines price and volume
        - Works well with high volume stocks

        **Recommendation:** Test all strategies and see which works best for your chosen stock!
        """)
