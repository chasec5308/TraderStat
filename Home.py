"""
TraderStat — Home / Dashboard
Main entry point for the Streamlit multi-page app.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
from datetime import date

import database as db
import utils

st.set_page_config(
    page_title="TraderStat — Trading Tools for Serious Traders",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0D1117;
    color: #EAEAEA;
}

/* Hero */
.hero-container {
    background: linear-gradient(135deg, #0D1117 0%, #1A1A2E 50%, #16213E 100%);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 20px;
    padding: 48px 56px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(0,212,170,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,212,170,0.1);
    border: 1px solid rgba(0,212,170,0.3);
    color: #00D4AA;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #EAEAEA 0%, #00D4AA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 12px;
    line-height: 1.15;
}
.hero-sub {
    color: #A0AEC0;
    font-size: 1.1rem;
    max-width: 600px;
    line-height: 1.7;
    margin-bottom: 28px;
}

/* Tool Cards */
.tool-card {
    background: linear-gradient(135deg, #16213E 0%, #1A1A2E 100%);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 16px;
    padding: 28px 24px;
    height: 100%;
    transition: border-color 0.2s;
    cursor: pointer;
}
.tool-card:hover { border-color: rgba(0,212,170,0.5); }
.tool-icon { font-size: 2.2rem; margin-bottom: 12px; }
.tool-title { color: #EAEAEA; font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
.tool-desc  { color: #A0AEC0; font-size: 0.88rem; line-height: 1.6; }
.tool-tag {
    display: inline-block;
    background: rgba(0,212,170,0.08);
    border: 1px solid rgba(0,212,170,0.2);
    color: #00D4AA;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 12px;
    margin-right: 4px;
}

/* Stat Cards */
.stat-card {
    background: linear-gradient(135deg, #16213E 0%, #1A1A2E 100%);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.stat-label { color: #A0AEC0; font-size: 0.75rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.stat-value { color: #EAEAEA; font-size: 1.8rem; font-weight: 700; }
.stat-value.green  { color: #00D4AA; }
.stat-value.red    { color: #E94560; }

.section-header { color: #00D4AA; font-size: 1.1rem; font-weight: 600; margin: 32px 0 16px; border-bottom: 1px solid rgba(0,212,170,0.2); padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

db.init_db()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px;">
        <div style="font-size:2rem">📊</div>
        <div style="color:#00D4AA; font-size:1.3rem; font-weight:800; letter-spacing:0.05em">TraderStat</div>
        <div style="color:#A0AEC0; font-size:0.78rem; margin-top:4px">Trading Tools Suite</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Navigate**")
    st.page_link("Home.py",                         label="🏠 Dashboard",         )
    st.page_link("pages/1_Trade_Journal.py",        label="📒 Trade Journal",     )
    st.page_link("pages/2_Risk_Calculator.py",      label="🧮 Risk Calculator",   )
    st.page_link("pages/3_Prop_Firm_Tracker.py",    label="🏦 Prop Firm Tracker", )
    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(0,212,170,0.1),rgba(0,212,170,0.05));
                border:1px solid rgba(0,212,170,0.2); border-radius:10px; padding:14px 16px; margin-top:8px;">
        <div style="color:#00D4AA; font-weight:700; font-size:0.9rem; margin-bottom:6px">⚡ Pro Plan</div>
        <div style="color:#A0AEC0; font-size:0.8rem; line-height:1.5;">Unlimited journal entries, advanced analytics, prop firm tracker</div>
        <div style="color:#00D4AA; font-size:1.1rem; font-weight:700; margin-top:8px">$9 / month</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.link_button("🚀 Upgrade to Pro", "https://traderstat.io/pricing", use_container_width=True, type="primary")

# ── Hero Section ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">📊 Trading Tools Suite</div>
    <div class="hero-title">TraderStat</div>
    <div class="hero-sub">
        Professional trading tools for futures, options, and prop firm traders.
        Track your edge, manage your risk, and pass your evaluation — all in one place.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick Stats ────────────────────────────────────────────────────────────────
trades   = db.get_trades()
accounts = db.get_prop_accounts()
# --- Trader Score ---
trader_score = 0

if not df.empty:
    total_trades = len(df)

    win_rate_decimal = (df["pnl"] > 0).mean()
    avg_r = df["r_multiple"].mean()

    # Max drawdown from cumulative P&L
    equity_curve = df["pnl"].cumsum()
    running_max = equity_curve.cummax()
    drawdown = equity_curve - running_max
    max_drawdown = abs(drawdown.min()) if not drawdown.empty else 0

    # Simple scoring model
    win_rate_score = win_rate_decimal * 40          # up to 40 pts
    avg_r_score = max(min(avg_r, 3), 0) / 3 * 30   # up to 30 pts
    trade_count_score = min(total_trades, 50) / 50 * 15  # up to 15 pts

    # Lower drawdown = better score
    if max_drawdown <= 100:
        drawdown_score = 15
    elif max_drawdown <= 300:
        drawdown_score = 10
    elif max_drawdown <= 500:
        drawdown_score = 5
    else:
        drawdown_score = 0

    trader_score = int(win_rate_score + avg_r_score + trade_count_score + drawdown_score)
col1, col2, col3, col4, col5 = st.columns(5)
if trades:
    stats = utils.compute_stats(trades)
    with col1:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Total Trades</div>
        <div class="stat-value">{stats['total_trades']}</div></div>""", unsafe_allow_html=True)
    with col2:
        cls = "green" if stats["win_rate"] >= 50 else "red"
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Win Rate</div>
        <div class="stat-value {cls}">{stats['win_rate']}%</div></div>""", unsafe_allow_html=True)
    with col3:
        cls = "green" if stats["total_pnl"] >= 0 else "red"
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Total P&L</div>
        <div class="stat-value {cls}">${stats['total_pnl']:,.2f}</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Prop Accounts</div>
        <div class="stat-value">{len(accounts)}</div></div>""", unsafe_allow_html=True)
        with col5:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Trader Score</div>
        <div class="stat-value">{trader_score}/100</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for col, (label, val) in zip([col1, col2, col3, col4], [
        ("Total Trades", "0"), ("Win Rate", "—"), ("Total P&L", "$0.00"), ("Prop Accounts", str(len(accounts)))
    ]):
        with col:
            st.markdown(f"""<div class="stat-card"><div class="stat-label">{label}</div>
            <div class="stat-value">{val}</div></div>""", unsafe_allow_html=True)

# ── Tool Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Your Tools</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">📒</div>
        <div class="tool-title">Trade Journal</div>
        <div class="tool-desc">
            Log every trade with full detail. Automatically calculates R multiples, P&L,
            win rate, equity curve, and strategy performance. Your trading data, organised.
        </div>
        <span class="tool-tag">Equity Curve</span>
        <span class="tool-tag">Win Rate</span>
        <span class="tool-tag">R Multiple</span>
        <span class="tool-tag">CSV Export</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Trade_Journal.py", label="Open Trade Journal →", use_container_width=True)

with c2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">🧮</div>
        <div class="tool-title">Risk Calculator</div>
        <div class="tool-desc">
            Never over-risk again. Enter your account size, risk %, entry, and stop loss
            to instantly get your correct position size, dollar risk, and profit targets.
        </div>
        <span class="tool-tag">Stocks</span>
        <span class="tool-tag">Futures</span>
        <span class="tool-tag">Options</span>
        <span class="tool-tag">1R/2R/3R Targets</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Risk_Calculator.py", label="Open Risk Calculator →", use_container_width=True)

with c3:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">🏦</div>
        <div class="tool-title">Prop Firm Tracker</div>
        <div class="tool-desc">
            Track your evaluation in real time. Monitor drawdown limits, daily loss rules,
            and progress to profit target. Get warnings before you break the rules.
        </div>
        <span class="tool-tag">FTMO</span>
        <span class="tool-tag">Apex</span>
        <span class="tool-tag">TopStep</span>
        <span class="tool-tag">Any Firm</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Prop_Firm_Tracker.py", label="Open Prop Firm Tracker →", use_container_width=True)

# ── Recent Trades ──────────────────────────────────────────────────────────────
if trades:
    st.markdown('<div class="section-header">Recent Trades</div>', unsafe_allow_html=True)
    df = pd.DataFrame(trades[:10])
    display_cols = ["trade_date", "ticker", "direction", "entry_price", "exit_price", "pnl", "r_multiple", "strategy"]
    display_cols = [c for c in display_cols if c in df.columns]

    def color_pnl(val):
        if isinstance(val, (int, float)):
            return f"color: {'#00D4AA' if val >= 0 else '#E94560'}; font-weight: 600"
        return ""

    styled = df[display_cols].style.applymap(
        color_pnl, subset=["pnl", "r_multiple"]
    ).format({
        "entry_price": "{:.4f}",
        "exit_price":  "{:.4f}",
        "pnl":         "${:,.2f}",
        "r_multiple":  "{:.2f}R",
    })
    st.dataframe(styled, use_container_width=True, hide_index=True)

# ── Getting Started ────────────────────────────────────────────────────────────
if not trades:
    st.markdown('<div class="section-header">Getting Started</div>', unsafe_allow_html=True)
    steps = [
        ("1", "📒", "Log Your First Trade", "Go to Trade Journal and log your first trade. The app will automatically calculate your R multiple and P&L."),
        ("2", "🧮", "Calculate Position Size", "Use the Risk Calculator before every trade to ensure you never risk more than your defined percentage."),
        ("3", "🏦", "Track Your Prop Evaluation", "Add your prop firm account to monitor your drawdown and progress toward the profit target."),
    ]
    c1, c2, c3 = st.columns(3)
    for col, (num, icon, title, desc) in zip([c1, c2, c3], steps):
        with col:
            st.markdown(f"""
            <div class="tool-card">
                <div style="color:#00D4AA; font-size:0.75rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px">STEP {num}</div>
                <div class="tool-icon">{icon}</div>
                <div class="tool-title">{title}</div>
                <div class="tool-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#A0AEC0; font-size:0.82rem; padding: 8px 0 16px;">
    <strong style="color:#00D4AA">TraderStat</strong> — Built for serious traders.
    &nbsp;|&nbsp; Trade smarter, not harder.
    &nbsp;|&nbsp; <a href="https://traderstat.io" style="color:#00D4AA; text-decoration:none;">traderstat.io</a>
</div>
""", unsafe_allow_html=True)
