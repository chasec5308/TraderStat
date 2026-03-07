"""
TraderStat — Tool 1: Trade Journal
Log trades, view statistics, and analyse performance with charts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from datetime import date, datetime

import database as db
import utils

st.set_page_config(
    page_title="Trade Journal | TraderStat",
    page_icon="📒",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.metric-card {
    background: linear-gradient(135deg, #16213E 0%, #1A1A2E 100%);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.metric-label { color: #A0AEC0; font-size: 0.78rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.metric-value { color: #EAEAEA; font-size: 1.6rem; font-weight: 700; }
.metric-value.positive { color: #00D4AA; }
.metric-value.negative { color: #E94560; }
.section-header { color: #00D4AA; font-size: 1.1rem; font-weight: 600; margin: 24px 0 12px; border-bottom: 1px solid rgba(0,212,170,0.2); padding-bottom: 6px; }
.stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

db.init_db()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📒 Trade Journal")
    st.markdown("Log every trade. Track every edge.")
    st.markdown("---")
    st.markdown("**Quick Stats**")
    trades = db.get_trades()
    st.metric("Total Trades", len(trades))
    if trades:
        stats = utils.compute_stats(trades)
        st.metric("Win Rate", f"{stats['win_rate']}%")
        st.metric("Total P&L", f"${stats['total_pnl']:,.2f}")

# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown("# 📒 Trade Journal")
st.markdown("Log your trades, track your performance, and identify your edge.")
st.markdown("---")

# ── Log New Trade ──────────────────────────────────────────────────────────────
with st.expander("➕ Log New Trade", expanded=True):
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            trade_date = st.date_input("Trade Date", value=date.today())
            ticker = st.text_input("Ticker / Instrument", placeholder="e.g. ES, NQ, AAPL, SPY")
            direction = st.selectbox("Direction", ["Long", "Short"])

        with col2:
            entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01, format="%.4f")
            stop_loss   = st.number_input("Stop Loss",   min_value=0.0, step=0.01, format="%.4f")
            exit_price  = st.number_input("Exit Price",  min_value=0.0, step=0.01, format="%.4f")

        with col3:
            position_size = st.number_input("Position Size (units/contracts)", min_value=0.0, step=0.01)
            strategy = st.text_input("Strategy", placeholder="e.g. Breakout, VWAP Fade, ICT")
            notes = st.text_area("Notes", placeholder="What did you observe? Any lessons?", height=80)

        submitted = st.form_submit_button("💾 Save Trade", use_container_width=True, type="primary")

        if submitted:
            if not ticker:
                st.error("Please enter a ticker/instrument.")
            elif entry_price == 0 or stop_loss == 0 or exit_price == 0:
                st.error("Entry, stop loss, and exit price must all be greater than 0.")
            elif position_size <= 0:
                st.error("Position size must be greater than 0.")
            else:
                db.insert_trade(
                    user_id="default",
                    trade_date=str(trade_date),
                    ticker=ticker.upper(),
                    direction=direction,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    exit_price=exit_price,
                    position_size=position_size,
                    strategy=strategy,
                    notes=notes,
                )
                st.success(f"Trade logged: {ticker.upper()} {direction} on {trade_date}")
                st.rerun()

# ── Statistics Dashboard ───────────────────────────────────────────────────────
trades = db.get_trades()

if not trades:
    st.info("No trades logged yet. Add your first trade above to see statistics and charts.")
    st.stop()

stats = utils.compute_stats(trades)

st.markdown('<div class="section-header">Performance Overview</div>', unsafe_allow_html=True)

# KPI Cards
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (c1, "Total Trades",   str(stats["total_trades"]),           ""),
    (c2, "Win Rate",       f"{stats['win_rate']}%",              "positive" if stats["win_rate"] >= 50 else "negative"),
    (c3, "Total P&L",      f"${stats['total_pnl']:,.2f}",        "positive" if stats["total_pnl"] >= 0 else "negative"),
    (c4, "Avg R",          f"{stats['avg_r']:.2f}R",             "positive" if stats["avg_r"] >= 0 else "negative"),
    (c5, "Profit Factor",  f"{stats['profit_factor']:.2f}",      "positive" if stats["profit_factor"] >= 1 else "negative"),
    (c6, "Max Drawdown",   f"${stats['max_drawdown']:,.2f}",     "negative" if stats["max_drawdown"] < 0 else ""),
]
for col, label, value, cls in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {cls}">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# Secondary KPIs
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Win</div>
        <div class="metric-value positive">${stats['avg_win']:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Loss</div>
        <div class="metric-value negative">${stats['avg_loss']:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    exp_cls = "positive" if stats["expectancy"] >= 0 else "negative"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Expectancy ($/trade)</div>
        <div class="metric-value {exp_cls}">${stats['expectancy']:,.2f}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ── Charts ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Charts & Analytics</div>', unsafe_allow_html=True)

df_sorted = stats["df_sorted"]

tab1, tab2, tab3, tab4 = st.tabs(["📈 Equity Curve", "🎯 Win Rate", "📊 R Distribution", "📅 Monthly P&L"])

with tab1:
    fig = utils.equity_curve_chart(df_sorted)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        fig = utils.win_rate_donut(stats["win_rate"])
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        strat_fig = utils.strategy_performance_chart(df_sorted)
        if strat_fig:
            st.plotly_chart(strat_fig, use_container_width=True)
        else:
            st.info("Add strategy names to your trades to see strategy performance.")

with tab3:
    fig = utils.r_distribution_chart(df_sorted)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    fig = utils.monthly_pnl_chart(df_sorted)
    st.plotly_chart(fig, use_container_width=True)

# ── Trade Log Table ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Trade Log</div>', unsafe_allow_html=True)

df_display = pd.DataFrame(trades)
if not df_display.empty:
    # Filter controls
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tickers = ["All"] + sorted(df_display["ticker"].unique().tolist())
        sel_ticker = st.selectbox("Filter by Ticker", tickers)
    with col_f2:
        directions = ["All", "Long", "Short"]
        sel_dir = st.selectbox("Filter by Direction", directions)
    with col_f3:
        strategies = ["All"] + sorted(df_display["strategy"].dropna().unique().tolist())
        sel_strat = st.selectbox("Filter by Strategy", strategies)

    filtered = df_display.copy()
    if sel_ticker != "All":
        filtered = filtered[filtered["ticker"] == sel_ticker]
    if sel_dir != "All":
        filtered = filtered[filtered["direction"] == sel_dir]
    if sel_strat != "All":
        filtered = filtered[filtered["strategy"] == sel_strat]

    # Display columns
    display_cols = ["id", "trade_date", "ticker", "direction", "entry_price",
                    "stop_loss", "exit_price", "position_size", "pnl", "r_multiple", "strategy"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    def color_pnl(val):
        if isinstance(val, (int, float)):
            color = "#00D4AA" if val >= 0 else "#E94560"
            return f"color: {color}; font-weight: 600"
        return ""

    styled = filtered[display_cols].style.applymap(
        color_pnl, subset=["pnl", "r_multiple"]
    ).format({
        "entry_price": "{:.4f}",
        "stop_loss":   "{:.4f}",
        "exit_price":  "{:.4f}",
        "pnl":         "${:,.2f}",
        "r_multiple":  "{:.2f}R",
    })

    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Delete trade
    st.markdown("---")
    with st.expander("🗑️ Delete a Trade"):
        trade_ids = filtered["id"].tolist()
        if trade_ids:
            del_id = st.selectbox("Select Trade ID to delete", trade_ids)
            if st.button("Delete Trade", type="secondary"):
                db.delete_trade(del_id)
                st.success(f"Trade #{del_id} deleted.")
                st.rerun()

    # Export
    csv = filtered.to_csv(index=False)
    st.download_button(
        label="⬇️ Export Trades to CSV",
        data=csv,
        file_name=f"traderstat_journal_{date.today()}.csv",
        mime="text/csv",
    )
# --- Equity Curve ---
import plotly.express as px

if not df.empty:

    df = df.sort_values("trade_date")

    df["equity"] = df["pnl"].cumsum()

    st.subheader("Equity Curve")

    fig = px.line(
        df,
        x="trade_date",
        y="equity",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)


# --- Strategy Analytics ---
st.subheader("Strategy Performance")

strategy_stats = df.groupby("strategy").agg(
    trades=("strategy", "count"),
    pnl=("pnl", "sum"),
    avg_r=("r_multiple", "mean")
)

st.dataframe(strategy_stats)
