"""
Strategy Optimization & Comparison Page.

Optimize strategy parameters and compare multiple strategies.
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
from src.backtesting.optimizer import ParameterOptimizer
from src.backtesting.comparator import StrategyComparator
import src.strategies.technical

st.set_page_config(page_title="Optimization", page_icon="🎯", layout="wide")

st.title("🎯 Strategy Optimization & Comparison")
st.markdown("Find the best strategy parameters and compare performance across strategies.")

# Create tabs for different features
tab1, tab2 = st.tabs(["📊 Strategy Comparison", "🔧 Parameter Optimization"])

# Tab 1: Strategy Comparison
with tab1:
    st.header("Strategy Comparison")
    st.markdown("Compare multiple strategies on the same dataset to find the best performer.")

    # Sidebar configuration for comparison
    with st.sidebar:
        st.subheader("⚙️ Comparison Settings")

        # Stock selection
        symbol = st.text_input(
            "Stock Symbol",
            value="RELIANCE",
            help="Enter NSE stock symbol",
            key="comp_symbol"
        ).upper().strip()

        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=730),
                max_value=datetime.now(),
                key="comp_start"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now(),
                key="comp_end"
            )

        initial_capital = st.number_input(
            "Initial Capital (₹)",
            min_value=10000,
            max_value=10000000,
            value=100000,
            step=10000,
            key="comp_capital"
        )

        st.markdown("---")

        # Strategy selection (multiple)
        strategies = StrategyRegistry.list_strategies()
        selected_strategies = st.multiselect(
            "Select Strategies to Compare",
            strategies,
            default=strategies[:3] if len(strategies) >= 3 else strategies,
            format_func=lambda x: x.replace('_', ' ').title()
        )

        compare_button = st.button(
            "🔍 Compare Strategies",
            type="primary",
            use_container_width=True
        )

    # Main content for comparison
    if compare_button:
        if len(selected_strategies) < 2:
            st.warning("⚠️ Please select at least 2 strategies to compare.")
        else:
            with st.spinner(f"Fetching data for {symbol}..."):
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

            with st.spinner("Running comparisons..."):
                # Create comparator
                comparator = StrategyComparator(data=data, initial_capital=initial_capital)

                # Add strategies
                for strategy_name in selected_strategies:
                    strategy = StrategyRegistry.get_strategy(strategy_name)
                    comparator.add_strategy(strategy)

            st.success("✅ Comparison complete!")

            # Display summary
            summary = comparator.get_statistics()
            st.subheader("📊 Comparison Summary")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Strategies Compared", summary['total_strategies'])
            with col2:
                st.metric("Best Strategy", summary['best_strategy'])
            with col3:
                st.metric("Best Return", f"{summary['best_return']:.2f}%")
            with col4:
                st.metric("Avg Return", f"{summary['avg_return']:.2f}%")

            st.markdown("---")

            # Comparison table
            st.subheader("📈 Performance Metrics")
            table = comparator.get_comparison_table()

            # Style the dataframe
            styled_table = table.style.format({
                'total_return_pct': '{:.2f}%',
                'win_rate': '{:.1f}%',
                'profit_factor': '{:.2f}',
                'avg_profit': '₹{:,.0f}',
                'avg_loss': '₹{:,.0f}',
                'max_profit': '₹{:,.0f}',
                'max_loss': '₹{:,.0f}'
            }).background_gradient(subset=['total_return_pct'], cmap='RdYlGn')

            st.dataframe(styled_table, use_container_width=True)

            # Equity curves
            st.subheader("💹 Equity Curves")
            combined_curves = comparator.get_combined_equity_curve()

            if not combined_curves.empty:
                fig = go.Figure()

                for column in combined_curves.columns:
                    fig.add_trace(go.Scatter(
                        x=combined_curves.index,
                        y=combined_curves[column],
                        mode='lines',
                        name=column,
                        line=dict(width=2)
                    ))

                fig.update_layout(
                    title="Strategy Performance Comparison",
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value (₹)",
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

            # Rankings
            st.subheader("🏆 Rankings")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**By Total Return**")
                rankings = comparator.get_rankings('total_return_pct')
                for rank in rankings:
                    medal = "🥇" if rank['rank'] == 1 else "🥈" if rank['rank'] == 2 else "🥉" if rank['rank'] == 3 else f"{rank['rank']}."
                    st.write(f"{medal} {rank['strategy']}: {rank['total_return_pct']:.2f}%")

            with col2:
                st.markdown("**By Win Rate**")
                rankings = comparator.get_rankings('win_rate')
                for rank in rankings:
                    medal = "🥇" if rank['rank'] == 1 else "🥈" if rank['rank'] == 2 else "🥉" if rank['rank'] == 3 else f"{rank['rank']}."
                    st.write(f"{medal} {rank['strategy']}: {rank['win_rate']:.1f}%")

            with col3:
                st.markdown("**By Profit Factor**")
                rankings = comparator.get_rankings('profit_factor')
                for rank in rankings:
                    medal = "🥇" if rank['rank'] == 1 else "🥈" if rank['rank'] == 2 else "🥉" if rank['rank'] == 3 else f"{rank['rank']}."
                    st.write(f"{medal} {rank['strategy']}: {rank['profit_factor']:.2f}")


# Tab 2: Parameter Optimization
with tab2:
    st.header("Parameter Optimization")
    st.markdown("Find the best parameters for a strategy using grid search optimization.")

    with st.sidebar:
        st.markdown("---")
        st.subheader("🔧 Optimization Settings")

        opt_symbol = st.text_input(
            "Stock Symbol",
            value="RELIANCE",
            key="opt_symbol"
        ).upper().strip()

        col1, col2 = st.columns(2)
        with col1:
            opt_start = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=730),
                max_value=datetime.now(),
                key="opt_start"
            )
        with col2:
            opt_end = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now(),
                key="opt_end"
            )

        opt_capital = st.number_input(
            "Initial Capital (₹)",
            min_value=10000,
            max_value=10000000,
            value=100000,
            step=10000,
            key="opt_capital"
        )

        # Strategy selection
        opt_strategy = st.selectbox(
            "Strategy to Optimize",
            strategies,
            format_func=lambda x: x.replace('_', ' ').title(),
            key="opt_strategy"
        )

        # Optimization metric
        opt_metric = st.selectbox(
            "Optimization Metric",
            ["total_return_pct", "sharpe_ratio", "sortino_ratio", "profit_factor", "win_rate"],
            format_func=lambda x: x.replace('_', ' ').title()
        )

    # Parameter ranges based on selected strategy
    st.subheader("📊 Parameter Ranges")
    st.markdown("Define the parameter ranges to test:")

    param_ranges = {}

    if opt_strategy == 'rsi':
        col1, col2, col3 = st.columns(3)
        with col1:
            periods = st.multiselect("Period", [7, 10, 14, 20, 25], default=[10, 14, 20])
        with col2:
            oversold_levels = st.multiselect("Oversold", [20, 25, 30, 35], default=[25, 30, 35])
        with col3:
            overbought_levels = st.multiselect("Overbought", [65, 70, 75, 80], default=[65, 70, 75])

        param_ranges = {
            'period': periods,
            'oversold': oversold_levels,
            'overbought': overbought_levels
        }

    elif opt_strategy == 'macd':
        col1, col2, col3 = st.columns(3)
        with col1:
            fast_periods = st.multiselect("Fast Period", [8, 10, 12, 15], default=[10, 12])
        with col2:
            slow_periods = st.multiselect("Slow Period", [20, 24, 26, 30], default=[24, 26])
        with col3:
            signal_periods = st.multiselect("Signal Period", [7, 9, 11], default=[9])

        param_ranges = {
            'fast_period': fast_periods,
            'slow_period': slow_periods,
            'signal_period': signal_periods
        }

    elif opt_strategy == 'sma_crossover':
        col1, col2 = st.columns(2)
        with col1:
            fast_periods = st.multiselect("Fast SMA", [10, 15, 20, 25], default=[10, 20])
        with col2:
            slow_periods = st.multiselect("Slow SMA", [40, 50, 60, 70], default=[50, 70])

        param_ranges = {
            'fast_period': fast_periods,
            'slow_period': slow_periods
        }

    elif opt_strategy == 'bollinger_bands':
        col1, col2 = st.columns(2)
        with col1:
            periods = st.multiselect("Period", [15, 20, 25], default=[20])
        with col2:
            std_devs = st.multiselect("Std Dev", [1.5, 2.0, 2.5], default=[2.0])

        param_ranges = {
            'period': periods,
            'std_dev': std_devs
        }

    else:
        st.info(f"Using default parameters for {opt_strategy}")
        strategy_info = StrategyRegistry.get_strategy_info(opt_strategy)
        st.json(strategy_info['default_params'])

    optimize_button = st.button("🚀 Run Optimization", type="primary", use_container_width=True)

    if optimize_button and param_ranges:
        with st.spinner(f"Fetching data for {opt_symbol}..."):
            adapter = AdapterFactory.get_adapter(timeframe='1d')
            data = adapter.get_historical_data(
                symbol=opt_symbol,
                start_date=opt_start,
                end_date=opt_end,
                timeframe='1d'
            )

            if data.empty:
                st.error(f"❌ No data found for {opt_symbol}")
                st.stop()

        # Calculate total combinations
        total_combinations = 1
        for values in param_ranges.values():
            total_combinations *= len(values)

        st.info(f"Testing {total_combinations} parameter combinations...")

        with st.spinner("Running optimization (this may take a minute)..."):
            # Get strategy class
            strategy_class = StrategyRegistry._strategies[opt_strategy]

            # Run optimization
            optimizer = ParameterOptimizer(
                strategy_class=strategy_class,
                data=data,
                initial_capital=opt_capital,
                optimization_metric=opt_metric
            )

            results = optimizer.optimize(param_ranges, min_trades=3)

        if results:
            st.success(f"✅ Optimization complete! Tested {len(results)} valid combinations.")

            # Display best parameters
            st.subheader("🏆 Best Parameters")
            best = results[0]
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Optimal Parameters:**")
                for param, value in best.params.items():
                    st.write(f"- {param}: **{value}**")

            with col2:
                st.markdown("**Performance:**")
                st.write(f"- {opt_metric.replace('_', ' ').title()}: **{best.metrics[opt_metric]:.2f}**")
                st.write(f"- Total Return: **{best.metrics['total_return_pct']:.2f}%**")
                st.write(f"- Win Rate: **{best.metrics['win_rate']:.1f}%**")
                st.write(f"- Total Trades: **{best.metrics['total_trades']}**")

            # Top results table
            st.subheader("📊 Top 10 Results")
            results_df = optimizer.get_results_dataframe().head(10)

            # Select key columns to display
            display_cols = list(best.params.keys()) + [
                'total_return_pct', 'win_rate', 'total_trades',
                'sharpe_ratio', 'max_drawdown'
            ]
            display_cols = [col for col in display_cols if col in results_df.columns]

            st.dataframe(results_df[display_cols], use_container_width=True)

            # Summary statistics
            summary = optimizer.get_optimization_summary()
            st.subheader("📈 Optimization Summary")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Combinations Tested", summary['total_combinations_tested'])
            with col2:
                st.metric("Best Score", f"{summary['best_score']:.2f}")
            with col3:
                st.metric("Average Score", f"{summary['avg_score']:.2f}")
            with col4:
                st.metric("Worst Score", f"{summary['worst_score']:.2f}")

        else:
            st.warning("⚠️ No valid results found. Try adjusting parameter ranges or reducing minimum trades requirement.")
