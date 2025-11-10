"""
Performance Dashboard - Track and analyze strategy performance over time.

Monitor your strategies with:
- Performance trends
- Strategy comparison
- Win rate tracking
- Historical analytics
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

from src.performance import PerformanceTracker
from src.strategies.registry import StrategyRegistry
from src.backtesting.engine import BacktestEngine
from src.data.adapters.adapter_factory import AdapterFactory
import src.strategies.technical

st.set_page_config(page_title="Performance Dashboard", page_icon="📈", layout="wide")

st.title("📈 Performance Dashboard")
st.markdown("Track and analyze your strategy performance over time.")

# Initialize tracker
tracker = PerformanceTracker()

# Get all strategies
all_strategies = StrategyRegistry.list_strategies()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📈 Performance Trends",
    "⚖️ Strategy Comparison",
    "🧪 New Backtest"
])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.header("📊 Performance Overview")

    # Load all records
    all_records = tracker.get_all_records()

    if not all_records.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Backtests", len(all_records))

        with col2:
            unique_strategies = all_records['strategy_name'].nunique()
            st.metric("Strategies Tested", unique_strategies)

        with col3:
            unique_stocks = all_records['symbol'].nunique()
            st.metric("Stocks Analyzed", unique_stocks)

        with col4:
            avg_return = all_records['total_return_pct'].mean()
            st.metric("Avg Return", f"{avg_return:.2f}%")

        st.markdown("---")

        # Recent backtests
        st.subheader("🕐 Recent Backtests")

        recent = all_records.sort_values('timestamp', ascending=False).head(10)

        display_df = recent[[
            'timestamp', 'symbol', 'strategy_name', 'total_return_pct',
            'sharpe_ratio', 'win_rate_pct', 'total_trades'
        ]].copy()

        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['Date', 'Stock', 'Strategy', 'Return %', 'Sharpe', 'Win Rate %', 'Trades']

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Top performing strategies
        st.subheader("🏆 Top Strategies by Average Return")

        strategy_stats = []
        for strategy in all_records['strategy_name'].unique():
            stats = tracker.get_strategy_stats(strategy)
            if stats:
                strategy_stats.append(stats)

        if strategy_stats:
            stats_df = pd.DataFrame(strategy_stats)
            stats_df = stats_df.sort_values('avg_return_pct', ascending=False)

            display_stats = stats_df[[
                'strategy_name', 'avg_return_pct', 'avg_sharpe',
                'avg_win_rate', 'total_backtests'
            ]].head(10)

            display_stats.columns = ['Strategy', 'Avg Return %', 'Avg Sharpe', 'Avg Win Rate %', 'Tests']

            st.dataframe(display_stats, use_container_width=True, hide_index=True)

    else:
        st.info("📝 No performance data yet. Run some backtests in the 'New Backtest' tab to get started!")


# ==================== TAB 2: PERFORMANCE TRENDS ====================
with tab2:
    st.header("📈 Performance Trends")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_strategy = st.selectbox(
            "Select Strategy",
            all_strategies,
            format_func=lambda x: x.replace('_', ' ').title(),
            key="trend_strategy"
        )

    with col2:
        days_back = st.selectbox(
            "Time Period",
            [30, 60, 90, 180, 365],
            index=2,
            format_func=lambda x: f"Last {x} days"
        )

    if st.button("📊 View Trends", type="primary"):
        with st.spinner("Loading performance data..."):
            df = tracker.get_strategy_performance(selected_strategy, days_back=days_back)

            if not df.empty:
                st.success(f"Found {len(df)} backtests for {selected_strategy.replace('_', ' ').title()}")

                # Performance metrics over time
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Return % Over Time', 'Sharpe Ratio Over Time',
                                   'Win Rate % Over Time', 'Max Drawdown % Over Time')
                )

                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')

                # Return %
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['total_return_pct'],
                              mode='lines+markers', name='Return %',
                              line=dict(color='blue')),
                    row=1, col=1
                )

                # Sharpe Ratio
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['sharpe_ratio'],
                              mode='lines+markers', name='Sharpe',
                              line=dict(color='green')),
                    row=1, col=2
                )

                # Win Rate
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['win_rate_pct'],
                              mode='lines+markers', name='Win Rate %',
                              line=dict(color='orange')),
                    row=2, col=1
                )

                # Max Drawdown
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['max_drawdown_pct'],
                              mode='lines+markers', name='Max DD %',
                              line=dict(color='red')),
                    row=2, col=2
                )

                fig.update_layout(height=700, showlegend=False, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

                # Summary statistics
                st.subheader("📊 Summary Statistics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    avg_return = df['total_return_pct'].mean()
                    st.metric("Avg Return", f"{avg_return:.2f}%")

                with col2:
                    avg_sharpe = df['sharpe_ratio'].mean()
                    st.metric("Avg Sharpe", f"{avg_sharpe:.2f}")

                with col3:
                    avg_win_rate = df['win_rate_pct'].mean()
                    st.metric("Avg Win Rate", f"{avg_win_rate:.1f}%")

                with col4:
                    avg_dd = df['max_drawdown_pct'].mean()
                    st.metric("Avg Max DD", f"{avg_dd:.2f}%")

            else:
                st.warning(f"No performance data found for {selected_strategy.replace('_', ' ').title()} in the last {days_back} days")


# ==================== TAB 3: STRATEGY COMPARISON ====================
with tab3:
    st.header("⚖️ Strategy Comparison")

    st.markdown("Compare performance across multiple strategies")

    # Multi-select strategies
    strategies_to_compare = st.multiselect(
        "Select Strategies to Compare (2-8)",
        all_strategies,
        default=all_strategies[:min(3, len(all_strategies))],
        format_func=lambda x: x.replace('_', ' ').title()
    )

    if len(strategies_to_compare) >= 2:
        if st.button("📊 Compare Strategies", type="primary"):
            with st.spinner("Comparing strategies..."):
                comparison_df = tracker.compare_strategies(strategies_to_compare)

                if not comparison_df.empty:
                    st.subheader("📊 Comparison Table")

                    # Sort by Avg Return
                    comparison_df = comparison_df.sort_values('Avg Return %', ascending=False)

                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

                    # Visualization
                    st.subheader("📈 Visual Comparison")

                    # Create radar chart for top 5 strategies
                    top_5 = comparison_df.head(5)

                    fig = go.Figure()

                    categories = ['Avg Return %', 'Avg Sharpe', 'Avg Win Rate %', 'Consistency']

                    for _, row in top_5.iterrows():
                        # Normalize values for radar chart (0-100)
                        values = [
                            min(100, max(0, row['Avg Return %'])),
                            min(100, row['Avg Sharpe'] * 20),  # Scale Sharpe to 0-100
                            row['Avg Win Rate %'],
                            row['Consistency']
                        ]

                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=row['Strategy']
                        ))

                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=True,
                        title="Strategy Performance Comparison (Top 5)",
                        height=600
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Bar chart comparison
                    fig2 = go.Figure()

                    fig2.add_trace(go.Bar(
                        x=comparison_df['Strategy'],
                        y=comparison_df['Avg Return %'],
                        name='Avg Return %',
                        marker_color='lightblue'
                    ))

                    fig2.update_layout(
                        title="Average Return by Strategy",
                        xaxis_title="Strategy",
                        yaxis_title="Avg Return %",
                        template='plotly_white',
                        height=400
                    )

                    st.plotly_chart(fig2, use_container_width=True)

                else:
                    st.warning("No performance data found for selected strategies")
    else:
        st.info("Select at least 2 strategies to compare")


# ==================== TAB 4: NEW BACKTEST ====================
with tab4:
    st.header("🧪 Run New Backtest")

    st.markdown("Run a backtest and automatically track its performance")

    col1, col2 = st.columns(2)

    with col1:
        symbol = st.text_input(
            "Stock Symbol",
            value="RELIANCE",
            help="Enter NSE stock symbol"
        ).upper().strip()

        selected_strategy = st.selectbox(
            "Strategy",
            all_strategies,
            format_func=lambda x: x.replace('_', ' ').title(),
            key="backtest_strategy"
        )

    with col2:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=730),
            max_value=datetime.now()
        )

        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )

    # Get strategy parameters
    strategy_info = StrategyRegistry.get_strategy_info(selected_strategy)
    default_params = strategy_info['default_params']

    if st.button("▶️ Run Backtest & Track", type="primary", use_container_width=True):
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
                    st.error(f"No data found for {symbol}")
                    st.stop()

                # Run backtest
                strategy = StrategyRegistry.get_strategy(selected_strategy, **default_params)
                engine = BacktestEngine(initial_capital=100000)

                results = engine.run(data, strategy)

                # Display results
                st.success("✅ Backtest completed!")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Return", f"{results['total_return_pct']:.2f}%")

                with col2:
                    st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")

                with col3:
                    st.metric("Win Rate", f"{results['win_rate']:.1f}%")

                with col4:
                    st.metric("Total Trades", results['total_trades'])

                # Add to tracker
                record = tracker.add_record(
                    symbol=symbol,
                    strategy_name=selected_strategy,
                    backtest_results=results,
                    timeframe='1d',
                    metadata={
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                )

                st.success("📊 Performance record saved!")

                # Show detailed results
                with st.expander("📋 Detailed Results"):
                    results_df = pd.DataFrame([results])
                    st.dataframe(results_df.T, use_container_width=True)

            except Exception as e:
                st.error(f"Error running backtest: {str(e)}")
                with st.expander("Error Details"):
                    st.exception(e)

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About")

    st.markdown("""
    ### Performance Dashboard

    Track your strategy performance over time:

    - **Overview**: See all backtests and top strategies
    - **Trends**: Analyze performance trends
    - **Comparison**: Compare multiple strategies
    - **New Backtest**: Run and track new backtests

    **Tip**: Run multiple backtests on different stocks
    to build a comprehensive performance history!
    """)

    st.markdown("---")

    # Quick stats
    all_records = tracker.get_all_records()

    if not all_records.empty:
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Records", len(all_records))

        latest = all_records.sort_values('timestamp', ascending=False).iloc[0]
        st.caption(f"Latest: {latest['symbol']} - {latest['strategy_name']}")
        st.caption(f"Return: {latest['total_return_pct']:.2f}%")

        # Clear old records button
        st.markdown("---")

        if st.button("🗑️ Clear Old Records (90+ days)"):
            deleted = tracker.clear_old_records(days_back=90)
            st.success(f"Deleted {deleted} old records")
            st.rerun()
