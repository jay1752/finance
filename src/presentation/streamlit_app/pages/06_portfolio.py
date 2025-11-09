"""
Portfolio Management Page - Track positions and manage risk.
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

from src.portfolio import Portfolio, PositionSizer, RiskManager

st.set_page_config(page_title="Portfolio Manager", page_icon="💼", layout="wide")

st.title("💼 Portfolio Manager")
st.markdown("Track your positions, manage risk, and monitor portfolio performance.")

# Initialize session state for portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = None

# Sidebar - Portfolio Setup
with st.sidebar:
    st.header("⚙️ Portfolio Setup")

    if st.session_state.portfolio is None:
        st.info("Create a new portfolio to get started")

        portfolio_name = st.text_input("Portfolio Name", value="My Trading Portfolio")
        initial_capital = st.number_input(
            "Initial Capital (₹)",
            min_value=10000,
            value=100000,
            step=10000
        )

        if st.button("Create Portfolio", type="primary"):
            st.session_state.portfolio = Portfolio(
                initial_capital=initial_capital,
                name=portfolio_name
            )
            st.success(f"Portfolio '{portfolio_name}' created!")
            st.rerun()

    else:
        portfolio = st.session_state.portfolio
        summary = portfolio.get_summary()

        st.success(f"**{summary['portfolio_name']}**")
        st.metric("Portfolio Value", f"₹{summary['current_value']:,.0f}")
        st.metric(
            "Total P&L",
            f"₹{summary['total_pnl']:,.0f}",
            f"{summary['total_pnl_pct']:.2f}%"
        )

        st.markdown("---")

        if st.button("Reset Portfolio", type="secondary"):
            st.session_state.portfolio = None
            st.rerun()

# Main content
if st.session_state.portfolio is None:
    st.info("👈 Create a portfolio in the sidebar to begin tracking positions")
    st.stop()

portfolio = st.session_state.portfolio

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Portfolio Overview",
    "➕ Add Position",
    "💹 Position Sizer",
    "📈 Performance"
])

# ==================== TAB 1: PORTFOLIO OVERVIEW ====================

with tab1:
    # Portfolio Summary
    summary = portfolio.get_summary()

    st.subheader("💼 Portfolio Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Value",
            f"₹{summary['current_value']:,.0f}",
            help="Current portfolio value (cash + positions)"
        )

    with col2:
        st.metric(
            "Cash Available",
            f"₹{summary['cash']:,.0f}",
            help="Available cash for new positions"
        )

    with col3:
        st.metric(
            "Positions Value",
            f"₹{summary['positions_value']:,.0f}",
            help="Total value of open positions"
        )

    with col4:
        st.metric(
            "Unrealized P&L",
            f"₹{summary['unrealized_pnl']:,.0f}",
            help="P&L from open positions"
        )

    with col5:
        st.metric(
            "Realized P&L",
            f"₹{summary['realized_pnl']:,.0f}",
            help="P&L from closed positions"
        )

    st.markdown("---")

    # Risk Metrics
    st.subheader("⚠️ Risk Exposure")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Open Positions",
            summary['num_open_positions']
        )

    with col2:
        st.metric(
            "Total Risk",
            f"₹{summary['total_risk']:,.0f}",
            help="Total amount at risk (based on stop-losses)"
        )

    with col3:
        st.metric(
            "Risk %",
            f"{summary['total_risk_pct']:.2f}%",
            help="Risk as % of initial capital"
        )

    with col4:
        st.metric(
            "Win Rate",
            f"{summary['win_rate']:.1f}%",
            help="Win rate from closed positions"
        )

    st.markdown("---")

    # Open Positions
    st.subheader("📋 Open Positions")

    open_positions = portfolio.get_all_positions(include_closed=False)

    if not open_positions:
        st.info("No open positions. Add positions in the 'Add Position' tab.")
    else:
        # Fetch current prices
        symbols = [pos.symbol for pos in open_positions]
        current_prices = portfolio.get_current_prices(symbols)

        # Build positions table
        positions_data = []
        for pos in open_positions:
            current_price = current_prices.get(pos.symbol, pos.entry_price)
            pnl_data = pos.calculate_pnl(current_price)

            positions_data.append({
                'Symbol': pos.symbol,
                'Shares': pos.shares,
                'Entry Price': f"₹{pos.entry_price:,.2f}",
                'Current Price': f"₹{current_price:,.2f}",
                'Entry Value': f"₹{pos.entry_value:,.0f}",
                'Current Value': f"₹{pos.shares * current_price:,.0f}",
                'P&L': f"₹{pnl_data['pnl']:,.2f}",
                'P&L %': f"{pnl_data['pnl_pct']:.2f}%",
                'Stop Loss': f"₹{pos.stop_loss.price:,.2f}" if pos.stop_loss else 'None',
                'Take Profit': f"₹{pos.take_profit.price:,.2f}" if pos.take_profit else 'None',
                'Entry Date': pos.entry_date.strftime('%Y-%m-%d')
            })

        df = pd.DataFrame(positions_data)

        # Color code based on P&L
        def highlight_pnl(row):
            pnl_str = row['P&L %']
            pnl_val = float(pnl_str.replace('%', ''))

            if pnl_val > 0:
                return ['background-color: #d4edda'] * len(row)
            elif pnl_val < 0:
                return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)

        styled_df = df.style.apply(highlight_pnl, axis=1)
        st.dataframe(styled_df, use_container_width=True)

        # Check stop-loss and take-profit
        alerts = portfolio.check_stops_and_targets(current_prices)

        if alerts['stop_loss_hit']:
            st.error(f"🛑 STOP-LOSS HIT: {', '.join(alerts['stop_loss_hit'])}")

        if alerts['take_profit_hit']:
            st.success(f"🎯 TAKE-PROFIT HIT: {', '.join(alerts['take_profit_hit'])}")

        # Close Position
        st.markdown("---")
        st.subheader("❌ Close Position")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            close_symbol = st.selectbox(
                "Select Position to Close",
                [pos.symbol for pos in open_positions],
                key='close_symbol'
            )

        with col2:
            current_price_for_close = current_prices.get(close_symbol, 0)
            close_price = st.number_input(
                "Exit Price (₹)",
                min_value=0.0,
                value=float(current_price_for_close),
                step=0.10,
                key='close_price'
            )

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Close Position", type="primary"):
                try:
                    portfolio.close_position(close_symbol, close_price)
                    st.success(f"Position {close_symbol} closed at ₹{close_price:.2f}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # Closed Positions
    st.subheader("📜 Closed Positions")

    closed_positions = [p for p in portfolio.positions if not p.is_open]

    if not closed_positions:
        st.info("No closed positions yet.")
    else:
        closed_data = []
        for pos in closed_positions:
            pnl_data = pos.calculate_pnl(pos.exit_price)

            closed_data.append({
                'Symbol': pos.symbol,
                'Shares': pos.shares,
                'Entry Price': f"₹{pos.entry_price:,.2f}",
                'Exit Price': f"₹{pos.exit_price:,.2f}",
                'P&L': f"₹{pnl_data['pnl']:,.2f}",
                'P&L %': f"{pnl_data['pnl_pct']:.2f}%",
                'Entry Date': pos.entry_date.strftime('%Y-%m-%d'),
                'Exit Date': pos.exit_date.strftime('%Y-%m-%d')
            })

        df_closed = pd.DataFrame(closed_data)

        # Color code
        def highlight_closed_pnl(row):
            pnl_str = row['P&L %']
            pnl_val = float(pnl_str.replace('%', ''))

            if pnl_val > 0:
                return ['background-color: #d4edda'] * len(row)
            else:
                return ['background-color: #f8d7da'] * len(row)

        styled_df_closed = df_closed.style.apply(highlight_closed_pnl, axis=1)
        st.dataframe(styled_df_closed, use_container_width=True)

# ==================== TAB 2: ADD POSITION ====================

with tab2:
    st.subheader("➕ Add New Position")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Position Details")

        symbol = st.text_input("Stock Symbol", value="RELIANCE", key='add_symbol')
        shares = st.number_input("Number of Shares", min_value=1, value=10, step=1, key='add_shares')
        entry_price = st.number_input("Entry Price (₹)", min_value=0.0, value=2847.50, step=0.10, key='add_entry_price')
        direction = st.selectbox("Direction", ["LONG", "SHORT"], key='add_direction')
        notes = st.text_area("Notes (optional)", key='add_notes')

    with col2:
        st.markdown("### Risk Management")

        # Stop-Loss
        sl_method = st.selectbox(
            "Stop-Loss Method",
            ["fixed", "atr", "none"],
            format_func=lambda x: {
                'fixed': 'Fixed %',
                'atr': 'ATR-based',
                'none': 'No Stop-Loss'
            }[x],
            key='sl_method'
        )

        stop_loss = None

        if sl_method == 'fixed':
            stop_pct = st.slider("Stop-Loss %", 1.0, 20.0, 5.0, 0.5, key='stop_pct')
            risk_mgr = RiskManager()
            stop_loss = risk_mgr.fixed_stop_loss(entry_price, stop_pct, direction)
            st.info(f"Stop-Loss Price: ₹{stop_loss.price:.2f}")

        elif sl_method == 'atr':
            atr = st.number_input("ATR Value", min_value=0.0, value=50.0, step=1.0, key='atr_value')
            multiplier = st.slider("ATR Multiplier", 1.0, 5.0, 2.0, 0.5, key='atr_multiplier')
            risk_mgr = RiskManager()
            stop_loss = risk_mgr.atr_stop_loss(entry_price, atr, multiplier, direction)
            st.info(f"Stop-Loss Price: ₹{stop_loss.price:.2f}")

        # Take-Profit
        tp_method = st.selectbox(
            "Take-Profit Method",
            ["fixed", "risk_reward", "none"],
            format_func=lambda x: {
                'fixed': 'Fixed %',
                'risk_reward': 'Risk-Reward Ratio',
                'none': 'No Take-Profit'
            }[x],
            key='tp_method'
        )

        take_profit = None

        if tp_method == 'fixed':
            profit_pct = st.slider("Take-Profit %", 1.0, 50.0, 10.0, 1.0, key='profit_pct')
            risk_mgr = RiskManager()
            take_profit = risk_mgr.fixed_take_profit(entry_price, profit_pct, direction)
            st.info(f"Take-Profit Price: ₹{take_profit.price:.2f}")

        elif tp_method == 'risk_reward' and stop_loss:
            rr_ratio = st.slider("Risk:Reward Ratio", 1.0, 5.0, 2.0, 0.5, key='rr_ratio')
            risk_mgr = RiskManager()
            take_profit = risk_mgr.risk_reward_take_profit(
                entry_price, stop_loss.price, rr_ratio, direction
            )
            st.info(f"Take-Profit Price: ₹{take_profit.price:.2f}")

    # Position Summary
    st.markdown("---")
    st.markdown("### Position Summary")

    col1, col2, col3, col4 = st.columns(4)

    position_cost = shares * entry_price

    with col1:
        st.metric("Position Cost", f"₹{position_cost:,.2f}")

    with col2:
        available_cash = portfolio.get_summary()['cash']
        st.metric("Available Cash", f"₹{available_cash:,.2f}")

    with col3:
        if stop_loss:
            if direction == 'LONG':
                risk_per_share = entry_price - stop_loss.price
            else:
                risk_per_share = stop_loss.price - entry_price
            position_risk = risk_per_share * shares
            st.metric("Position Risk", f"₹{position_risk:,.2f}")
        else:
            st.metric("Position Risk", "Not set")

    with col4:
        if take_profit:
            if direction == 'LONG':
                potential_profit = (take_profit.price - entry_price) * shares
            else:
                potential_profit = (entry_price - take_profit.price) * shares
            st.metric("Potential Profit", f"₹{potential_profit:,.2f}")
        else:
            st.metric("Potential Profit", "Not set")

    # Add Position Button
    if st.button("Add Position to Portfolio", type="primary", key='add_position_btn'):
        try:
            portfolio.open_position(
                symbol=symbol,
                shares=shares,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                direction=direction,
                notes=notes
            )
            st.success(f"Position added: {shares} shares of {symbol} at ₹{entry_price:.2f}")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Error adding position: {e}")

# ==================== TAB 3: POSITION SIZER ====================

with tab3:
    st.subheader("💹 Position Size Calculator")

    st.markdown("Calculate optimal position size using different methods.")

    capital = portfolio.get_summary()['cash']

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Input Parameters")

        sizing_symbol = st.text_input("Stock Symbol", value="TCS", key='sizing_symbol')
        sizing_price = st.number_input("Current Price (₹)", min_value=0.0, value=3445.80, step=0.10, key='sizing_price')

        sizing_method = st.selectbox(
            "Sizing Method",
            ["kelly_criterion", "fixed_fractional", "risk_based", "equal_weight", "fixed_amount"],
            format_func=lambda x: {
                'kelly_criterion': 'Kelly Criterion',
                'fixed_fractional': 'Fixed Fractional',
                'risk_based': 'Risk-Based (ATR)',
                'equal_weight': 'Equal Weight',
                'fixed_amount': 'Fixed Amount'
            }[x],
            key='sizing_method'
        )

        # Method-specific inputs
        if sizing_method == 'kelly_criterion':
            win_rate = st.slider("Win Rate (%)", 0.0, 100.0, 65.0, 1.0, key='kelly_win_rate') / 100
            avg_win = st.number_input("Average Win (%)", min_value=0.0, value=8.5, step=0.1, key='kelly_avg_win')
            avg_loss = st.number_input("Average Loss (%)", min_value=0.0, value=4.2, step=0.1, key='kelly_avg_loss')
            kelly_fraction = st.slider("Kelly Fraction", 0.1, 1.0, 0.25, 0.05, key='kelly_fraction')

        elif sizing_method == 'fixed_fractional':
            risk_pct = st.slider("Risk per Trade (%)", 0.1, 5.0, 2.0, 0.1, key='ff_risk_pct') / 100
            stop_loss_pct = st.slider("Stop-Loss (%)", 1.0, 20.0, 5.0, 0.5, key='ff_stop_pct')

        elif sizing_method == 'risk_based':
            atr_value = st.number_input("ATR Value", min_value=0.0, value=50.0, step=1.0, key='rb_atr')
            atr_mult = st.slider("ATR Multiplier", 1.0, 5.0, 2.0, 0.5, key='rb_mult')
            risk_pct = st.slider("Risk per Trade (%)", 0.1, 5.0, 2.0, 0.1, key='rb_risk_pct') / 100

        elif sizing_method == 'equal_weight':
            num_positions = st.number_input("Total Positions", min_value=1, value=5, step=1, key='ew_num_pos')

        elif sizing_method == 'fixed_amount':
            fixed_amount = st.number_input("Fixed Amount (₹)", min_value=0.0, value=20000.0, step=1000.0, key='fa_amount')

    with col2:
        st.markdown("### Calculation Results")

        # Calculate position size
        sizer = PositionSizer(capital=capital)

        try:
            if sizing_method == 'kelly_criterion':
                result = sizer.kelly_criterion(
                    win_rate=win_rate,
                    avg_win=avg_win,
                    avg_loss=avg_loss,
                    price=sizing_price,
                    kelly_fraction=kelly_fraction
                )

            elif sizing_method == 'fixed_fractional':
                result = sizer.fixed_fractional(
                    price=sizing_price,
                    risk_percentage=risk_pct,
                    stop_loss_pct=stop_loss_pct
                )

            elif sizing_method == 'risk_based':
                result = sizer.risk_based(
                    price=sizing_price,
                    atr=atr_value,
                    atr_multiplier=atr_mult,
                    risk_percentage=risk_pct
                )

            elif sizing_method == 'equal_weight':
                result = sizer.equal_weight(
                    price=sizing_price,
                    num_positions=num_positions
                )

            elif sizing_method == 'fixed_amount':
                result = sizer.fixed_amount(
                    price=sizing_price,
                    amount=fixed_amount
                )

            # Display results
            st.success("✅ Position Size Calculated")

            st.metric("Shares to Buy", result.shares)
            st.metric("Capital Allocation", f"₹{result.capital_allocation:,.2f}")
            st.metric("Risk Amount", f"₹{result.risk_amount:,.2f}")
            st.metric("Risk %", f"{(result.risk_amount / capital) * 100:.2f}%")

            # Show metadata
            with st.expander("📊 Calculation Details"):
                for key, value in result.metadata.items():
                    if isinstance(value, float):
                        st.write(f"**{key}**: {value:.4f}")
                    else:
                        st.write(f"**{key}**: {value}")

        except Exception as e:
            st.error(f"Error calculating position size: {e}")

# ==================== TAB 4: PERFORMANCE ====================

with tab4:
    st.subheader("📈 Portfolio Performance")

    summary = portfolio.get_summary()

    # Performance Summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Return",
            f"₹{summary['total_pnl']:,.0f}",
            f"{summary['total_pnl_pct']:.2f}%"
        )

    with col2:
        st.metric("Win Rate", f"{summary['win_rate']:.1f}%")

    with col3:
        total_trades = summary['num_closed_positions']
        st.metric("Total Trades", total_trades)

    st.markdown("---")

    # Performance Chart
    if summary['num_closed_positions'] > 0:
        st.markdown("### 📊 Trade History")

        # Build trade history
        trade_history = []
        cumulative_pnl = 0

        for pos in portfolio.positions:
            if not pos.is_open:
                pnl_data = pos.calculate_pnl(pos.exit_price)
                cumulative_pnl += pnl_data['pnl']

                trade_history.append({
                    'date': pos.exit_date,
                    'symbol': pos.symbol,
                    'pnl': pnl_data['pnl'],
                    'pnl_pct': pnl_data['pnl_pct'],
                    'cumulative_pnl': cumulative_pnl
                })

        df_history = pd.DataFrame(trade_history)

        # Cumulative P&L chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_history['date'],
            y=df_history['cumulative_pnl'],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title='Cumulative P&L Over Time',
            xaxis_title='Date',
            yaxis_title='Cumulative P&L (₹)',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Trade details
        st.markdown("### 📋 Trade Details")

        trade_details = []
        for pos in portfolio.positions:
            if not pos.is_open:
                pnl_data = pos.calculate_pnl(pos.exit_price)
                trade_details.append({
                    'Symbol': pos.symbol,
                    'Entry': f"₹{pos.entry_price:,.2f}",
                    'Exit': f"₹{pos.exit_price:,.2f}",
                    'Shares': pos.shares,
                    'P&L': f"₹{pnl_data['pnl']:,.2f}",
                    'P&L %': f"{pnl_data['pnl_pct']:.2f}%",
                    'Entry Date': pos.entry_date.strftime('%Y-%m-%d'),
                    'Exit Date': pos.exit_date.strftime('%Y-%m-%d'),
                    'Result': 'Win' if pnl_data['pnl'] > 0 else 'Loss'
                })

        df_trades = pd.DataFrame(trade_details)

        # Color code
        def highlight_result(row):
            if row['Result'] == 'Win':
                return ['background-color: #d4edda'] * len(row)
            else:
                return ['background-color: #f8d7da'] * len(row)

        styled_trades = df_trades.style.apply(highlight_result, axis=1)
        st.dataframe(styled_trades, use_container_width=True)

    else:
        st.info("No closed trades yet. Close some positions to see performance history.")

# Footer
st.markdown("---")
st.markdown("**Portfolio Manager** - Track positions, manage risk, and grow your wealth 📈")
