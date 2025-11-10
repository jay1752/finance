"""
Multi-Timeframe Analysis Page.

Analyze stocks across multiple timeframes (1h, 4h, daily, weekly)
to identify high-confidence trading signals.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis import MultiTimeframeAnalyzer
from src.strategies.registry import StrategyRegistry
import src.strategies.technical

st.set_page_config(page_title="Multi-Timeframe Analysis", page_icon="📊", layout="wide")

st.title("📊 Multi-Timeframe Analysis")
st.markdown(
    "Analyze stocks across multiple timeframes to identify high-conviction trading signals. "
    "When signals align across timeframes, it indicates stronger signal reliability."
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Stock selection
    symbol = st.text_input(
        "Stock Symbol",
        value="RELIANCE",
        help="Enter NSE stock symbol (e.g., RELIANCE, TCS, INFY)"
    ).upper().strip()

    st.markdown("---")

    # Strategy selection
    strategies = StrategyRegistry.list_strategies()
    selected_strategy = st.selectbox(
        "Strategy",
        strategies,
        format_func=lambda x: x.replace('_', ' ').title(),
        help="Select which strategy to apply across timeframes"
    )

    # Get strategy parameters
    strategy_info = StrategyRegistry.get_strategy_info(selected_strategy)
    default_params = strategy_info['default_params']

    st.markdown("---")

    # Timeframe set selection
    timeframe_set = st.selectbox(
        "Timeframe Set",
        ['full', 'intraday', 'swing', 'daily_only'],
        format_func=lambda x: {
            'full': '📊 Full (1h, 4h, 1d, 1wk)',
            'intraday': '⚡ Intraday (1h, 4h, 1d)',
            'swing': '📈 Swing (4h, 1d, 1wk)',
            'daily_only': '📅 Daily Only (1d, 1wk)'
        }[x],
        help="Select which timeframes to analyze"
    )

    st.markdown("---")

    # Days back
    days_back = st.slider(
        "Days of Data",
        min_value=30,
        max_value=180,
        value=90,
        step=30,
        help="How many days of historical data to fetch"
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
    with st.spinner(f"Analyzing {symbol} across multiple timeframes..."):
        try:
            # Create analyzer
            analyzer = MultiTimeframeAnalyzer(timeframe_set=timeframe_set)

            # Run analysis
            result = analyzer.analyze(
                symbol=symbol,
                strategy_name=selected_strategy,
                strategy_params=default_params,
                days_back=days_back
            )

            # Display results
            st.markdown("---")

            # Overall Summary
            st.subheader("🎯 Overall Signal")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                signal_color = {
                    'BUY': '🟢',
                    'SELL': '🔴',
                    'NEUTRAL': '⚪',
                    'CONFLICTING': '🟡'
                }.get(result.overall_signal, '⚪')

                st.markdown(f"### {signal_color} {result.overall_signal}")
                st.caption("Overall Direction")

            with col2:
                strength_emoji = {
                    'VERY STRONG': '💪💪💪',
                    'STRONG': '💪💪',
                    'MODERATE': '💪',
                    'WEAK': '🤏',
                    'NONE': '❌'
                }.get(result.signal_strength, '❌')

                st.markdown(f"### {strength_emoji}")
                st.markdown(f"**{result.signal_strength}**")
                st.caption("Signal Strength")

            with col3:
                st.metric(
                    "Confidence",
                    f"{result.overall_confidence:.1f}%",
                    help="Weighted confidence based on timeframe alignment"
                )
                st.progress(result.overall_confidence / 100)

            with col4:
                total_tf = len(result.timeframe_signals)
                st.metric(
                    "Alignment",
                    f"{result.aligned_timeframes}/{total_tf}",
                    help="Number of timeframes with aligned signals"
                )

                alignment_pct = analyzer.get_timeframe_alignment_score(result)
                st.progress(alignment_pct / 100)

            st.markdown("---")

            # Recommendation
            st.subheader("💡 Recommendation")

            if result.overall_signal in ['BUY'] and result.signal_strength in ['VERY STRONG', 'STRONG']:
                st.success(f"**{result.recommendation}**")
            elif result.overall_signal in ['SELL'] and result.signal_strength in ['VERY STRONG', 'STRONG']:
                st.error(f"**{result.recommendation}**")
            elif result.overall_signal == 'CONFLICTING':
                st.warning(f"**{result.recommendation}**")
            else:
                st.info(f"**{result.recommendation}**")

            with st.expander("📋 Detailed Reasoning"):
                st.write(result.reasoning)

            st.markdown("---")

            # Individual Timeframe Signals
            st.subheader("📈 Timeframe Breakdown")

            # Create visualization
            fig = go.Figure()

            # Prepare data for visualization
            timeframes = []
            signal_types = []
            confidences = []
            colors = []

            for tf_signal in result.timeframe_signals:
                timeframes.append(tf_signal.timeframe)

                if tf_signal.has_signal:
                    signal_types.append(tf_signal.signal_type)
                    confidences.append(tf_signal.confidence)

                    if tf_signal.signal_type == 'BUY':
                        colors.append('green')
                    elif tf_signal.signal_type == 'SELL':
                        colors.append('red')
                    else:
                        colors.append('gray')
                else:
                    signal_types.append('NO SIGNAL')
                    confidences.append(0)
                    colors.append('lightgray')

            # Create bar chart
            fig.add_trace(go.Bar(
                x=timeframes,
                y=confidences,
                text=[f"{s}<br>{c:.0f}%" for s, c in zip(signal_types, confidences)],
                textposition='auto',
                marker=dict(color=colors),
                hovertemplate='<b>%{x}</b><br>Signal: %{text}<extra></extra>'
            ))

            fig.update_layout(
                title=f"Signal Confidence Across Timeframes",
                xaxis_title="Timeframe",
                yaxis_title="Confidence (%)",
                yaxis=dict(range=[0, 100]),
                height=400,
                template='plotly_white',
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # Detailed table
            st.subheader("📊 Detailed Signals")

            # Create DataFrame for signals
            signals_data = []
            for tf_signal in result.timeframe_signals:
                if tf_signal.has_signal:
                    signals_data.append({
                        'Timeframe': tf_signal.timeframe,
                        'Signal': tf_signal.signal_type,
                        'Confidence': f"{tf_signal.confidence:.1f}%",
                        'Date': tf_signal.metadata.get('date', 'N/A'),
                        'Price': f"₹{tf_signal.metadata.get('price', 0):.2f}" if tf_signal.metadata.get('price') else 'N/A'
                    })
                else:
                    signals_data.append({
                        'Timeframe': tf_signal.timeframe,
                        'Signal': 'NO SIGNAL',
                        'Confidence': '0%',
                        'Date': 'N/A',
                        'Price': 'N/A'
                    })

            signals_df = pd.DataFrame(signals_data)

            # Style the dataframe
            def style_signal(val):
                if val == 'BUY':
                    return 'background-color: #90EE90'
                elif val == 'SELL':
                    return 'background-color: #FFB6C1'
                return ''

            styled_df = signals_df.style.applymap(style_signal, subset=['Signal'])

            st.dataframe(styled_df, use_container_width=True, height=250)

            # Export functionality
            st.markdown("---")
            st.subheader("📥 Export Results")

            # Create export data
            export_data = {
                'Symbol': symbol,
                'Strategy': selected_strategy.replace('_', ' ').title(),
                'Analysis Date': result.analysis_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Overall Signal': result.overall_signal,
                'Signal Strength': result.signal_strength,
                'Confidence': f"{result.overall_confidence:.1f}%",
                'Alignment': f"{result.aligned_timeframes}/{len(result.timeframe_signals)}",
                'Recommendation': result.recommendation,
                'Reasoning': result.reasoning
            }

            # Add timeframe details
            for i, tf_signal in enumerate(result.timeframe_signals, 1):
                prefix = f"TF{i} ({tf_signal.timeframe})"
                export_data[f"{prefix} Signal"] = tf_signal.signal_type or 'NO SIGNAL'
                export_data[f"{prefix} Confidence"] = f"{tf_signal.confidence:.1f}%"

            export_df = pd.DataFrame([export_data])

            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Analysis (CSV)",
                data=csv,
                file_name=f"{symbol}_{selected_strategy}_mtf_analysis.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("📝 Error Details"):
                st.exception(e)

else:
    # Show instructions
    st.info("👈 **Configure parameters in the sidebar and click 'Analyze' to get started**")

    st.markdown("---")

    # Educational content
    st.subheader("📚 What is Multi-Timeframe Analysis?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎯 Why Multiple Timeframes?

        Multi-timeframe analysis increases signal confidence by checking if trends align across different time horizons:

        - **1 Week (1wk)**: Primary trend direction
        - **1 Day (1d)**: Secondary trend and key levels
        - **4 Hours (4h)**: Short-term momentum
        - **1 Hour (1h)**: Precise entry/exit timing

        **Key Principle**: When all timeframes align, the signal is stronger and more reliable.
        """)

        st.markdown("---")

        st.markdown("""
        ### 📊 Signal Strength Levels

        - **VERY STRONG**: 3-4 timeframes aligned, high confidence (75%+)
        - **STRONG**: 3 timeframes aligned, good confidence (60-75%)
        - **MODERATE**: 2 timeframes aligned, moderate confidence (50-60%)
        - **WEAK**: 1 timeframe only, low confidence (<50%)
        """)

    with col2:
        st.markdown("""
        ### 💡 Trading Guidelines

        **VERY STRONG Signals**:
        - ✅ High confidence trade setup
        - ✅ Consider full position size
        - ✅ Clear stop-loss and target

        **STRONG Signals**:
        - ✅ Good trade setup
        - ⚠️ Consider 75% position size
        - ✅ Monitor closely

        **MODERATE Signals**:
        - ⚠️ Caution required
        - ⚠️ Consider 50% position size
        - ⚠️ Wait for better alignment if possible

        **WEAK Signals**:
        - ❌ Avoid or use very small size
        - ❌ High risk, low confidence
        - ❌ Better to wait
        """)

    st.markdown("---")

    st.subheader("🎓 Example Use Cases")

    with st.expander("📈 Scenario 1: All Timeframes Align (BUY)"):
        st.markdown("""
        - **1wk**: BUY signal (uptrend)
        - **1d**: BUY signal (pullback completed)
        - **4h**: BUY signal (momentum turning up)
        - **1h**: BUY signal (breakout)

        **Result**: VERY STRONG BUY - High confidence trade setup with all timeframes supporting the direction.
        """)

    with st.expander("⚠️ Scenario 2: Mixed Signals"):
        st.markdown("""
        - **1wk**: BUY signal (uptrend)
        - **1d**: SELL signal (short-term pullback)
        - **4h**: NO SIGNAL
        - **1h**: SELL signal

        **Result**: CONFLICTING - Wait for clarity. Higher timeframe (1wk) suggests up, but lower timeframes show weakness.
        """)

    with st.expander("📉 Scenario 3: Partial Alignment (SELL)"):
        st.markdown("""
        - **1wk**: SELL signal (downtrend)
        - **1d**: SELL signal (breakdown)
        - **4h**: NO SIGNAL
        - **1h**: BUY signal (minor bounce)

        **Result**: STRONG SELL - 2 major timeframes aligned down. The 1h bounce is likely just a retracement.
        """)
