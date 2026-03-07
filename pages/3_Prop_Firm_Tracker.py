"""
TraderStat — Tool 3: Prop Firm Tracker
Track evaluation progress, drawdown limits, and profit targets.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

import database as db
import utils

st.set_page_config(
    page_title="Prop Firm Tracker | TraderStat",
    page_icon="🏦",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.account-card {
    background: linear-gradient(135deg, #16213E 0%, #1A1A2E 100%);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.account-card.danger  { border: 2px solid #E94560; }
.account-card.warning { border: 2px solid #F6AD55; }
.account-card.ok      { border: 2px solid rgba(0,212,170,0.3); }

.firm-name { color: #EAEAEA; font-size: 1.3rem; font-weight: 700; margin-bottom: 4px; }
.status-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}
.badge-ok      { background: rgba(0,212,170,0.15); color: #00D4AA; }
.badge-warning { background: rgba(246,173,85,0.15); color: #F6AD55; }
.badge-danger  { background: rgba(233,69,96,0.15); color: #E94560; }

.stat-row { display: flex; gap: 20px; margin-top: 16px; flex-wrap: wrap; }
.stat-item { flex: 1; min-width: 120px; }
.stat-label { color: #A0AEC0; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.07em; }
.stat-val   { color: #EAEAEA; font-size: 1.1rem; font-weight: 600; margin-top: 2px; }
.stat-val.green { color: #00D4AA; }
.stat-val.red   { color: #E94560; }
.stat-val.orange { color: #F6AD55; }

.section-header { color: #00D4AA; font-size: 1.1rem; font-weight: 600; margin: 24px 0 12px; border-bottom: 1px solid rgba(0,212,170,0.2); padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

db.init_db()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Prop Firm Tracker")
    st.markdown("Stay within the rules. Pass the evaluation.")
    st.markdown("---")
    accounts = db.get_prop_accounts()
    st.metric("Active Accounts", len(accounts))

# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown("# 🏦 Prop Firm Tracker")
st.markdown("Monitor your evaluation progress, drawdown limits, and profit targets in real time.")
st.markdown("---")

# ── Add New Account ────────────────────────────────────────────────────────────
with st.expander("➕ Add New Prop Firm Account", expanded=len(db.get_prop_accounts()) == 0):
    with st.form("prop_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            firm_name    = st.text_input("Firm Name", placeholder="e.g. FTMO, Apex, TopStep, MFF")
            account_size = st.number_input("Account Size ($)", min_value=1000.0, value=100_000.0, step=1000.0)
            profit_target = st.number_input("Profit Target ($)", min_value=100.0, value=10_000.0, step=100.0,
                                            help="Dollar amount you need to earn to pass.")
            start_date   = st.date_input("Start Date", value=date.today())

        with col2:
            max_drawdown    = st.number_input("Max Drawdown ($)", min_value=100.0, value=5_000.0, step=100.0,
                                              help="Maximum total loss allowed before account is failed.")
            daily_loss_limit = st.number_input("Daily Loss Limit ($)", min_value=50.0, value=2_500.0, step=50.0,
                                               help="Maximum loss allowed in a single trading day.")
            current_balance  = st.number_input("Current Balance ($)", min_value=0.0, value=100_000.0, step=100.0)
            notes = st.text_area("Notes", placeholder="Firm rules, phase, notes...", height=68)

        submitted = st.form_submit_button("💾 Add Account", use_container_width=True, type="primary")
        if submitted:
            if not firm_name:
                st.error("Please enter a firm name.")
            else:
                db.insert_prop_account(
                    user_id="default",
                    firm_name=firm_name,
                    account_size=account_size,
                    profit_target=profit_target,
                    max_drawdown=max_drawdown,
                    daily_loss_limit=daily_loss_limit,
                    current_balance=current_balance,
                    start_date=str(start_date),
                    notes=notes,
                )
                st.success(f"Account added: {firm_name}")
                st.rerun()

# ── Account Dashboard ──────────────────────────────────────────────────────────
accounts = db.get_prop_accounts()

if not accounts:
    st.info("No prop firm accounts added yet. Add your first account above.")
    st.stop()

st.markdown('<div class="section-header">Your Accounts</div>', unsafe_allow_html=True)

for account in accounts:
    status_data = utils.prop_firm_status(account)
    status = status_data["status"]

    card_class  = {"ON TRACK": "ok", "WARNING": "warning", "DANGER": "danger"}[status]
    badge_class = {"ON TRACK": "badge-ok", "WARNING": "badge-warning", "DANGER": "badge-danger"}[status]
    badge_icon  = {"ON TRACK": "✅", "WARNING": "⚠️", "DANGER": "🚨"}[status]

    pct_target_color = "green" if status_data["pct_to_target"] >= 50 else "orange"
    dd_color = "red" if status == "DANGER" else ("orange" if status == "WARNING" else "green")

    st.markdown(f"""
    <div class="account-card {card_class}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="firm-name">🏦 {account['firm_name']}</div>
            <span class="status-badge {badge_class}">{badge_icon} {status}</span>
        </div>
        <div class="stat-row">
            <div class="stat-item">
                <div class="stat-label">Account Size</div>
                <div class="stat-val">${account['account_size']:,.0f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Current Balance</div>
                <div class="stat-val">${account['current_balance']:,.2f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Profit Needed</div>
                <div class="stat-val {'green' if status_data['profit_needed'] <= 0 else 'orange'}">${status_data['profit_needed']:,.2f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Progress to Target</div>
                <div class="stat-val {pct_target_color}">{status_data['pct_to_target']:.1f}%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Drawdown Used</div>
                <div class="stat-val {dd_color}">${status_data['drawdown_used']:,.2f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Drawdown Left</div>
                <div class="stat-val {dd_color}">${status_data['drawdown_left']:,.2f}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Daily Limit</div>
                <div class="stat-val">${account['daily_loss_limit']:,.2f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bars
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Progress to Profit Target** — {status_data['pct_to_target']:.1f}%")
            st.progress(min(1.0, status_data["pct_to_target"] / 100))
        with col_b:
            dd_pct = status_data["pct_dd_used"] / 100
            st.markdown(f"**Drawdown Used** — {status_data['pct_dd_used']:.1f}%")
            st.progress(min(1.0, dd_pct))

    # Danger / Warning alerts
    if status == "DANGER":
        st.error(f"🚨 **DANGER:** Drawdown remaining (${status_data['drawdown_left']:,.2f}) is less than or equal to your daily loss limit (${account['daily_loss_limit']:,.2f}). Do NOT trade today.")
    elif status == "WARNING":
        st.warning(f"⚠️ **WARNING:** You have used {status_data['pct_dd_used']:.1f}% of your max drawdown. Trade with reduced size.")

    # Update balance + log snapshot
    with st.expander(f"📝 Update Balance — {account['firm_name']}"):
        col_u1, col_u2, col_u3 = st.columns(3)
        with col_u1:
            new_balance = st.number_input(
                "New Balance ($)",
                min_value=0.0,
                value=float(account["current_balance"]),
                step=100.0,
                key=f"bal_{account['id']}"
            )
        with col_u2:
            snap_date = st.date_input("Date", value=date.today(), key=f"date_{account['id']}")
        with col_u3:
            snap_notes = st.text_input("Notes", key=f"notes_{account['id']}", placeholder="Today's summary")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Update Balance", key=f"upd_{account['id']}", type="primary"):
                daily_pnl = new_balance - account["current_balance"]
                db.update_prop_balance(account["id"], new_balance)
                db.insert_prop_snapshot(account["id"], str(snap_date), new_balance, daily_pnl, snap_notes)
                st.success(f"Balance updated to ${new_balance:,.2f} (Daily P&L: ${daily_pnl:+,.2f})")
                st.rerun()
        with col_btn2:
            if st.button("Delete Account", key=f"del_{account['id']}", type="secondary"):
                db.delete_prop_account(account["id"])
                st.success("Account deleted.")
                st.rerun()

    # Balance history chart
    snapshots = db.get_prop_snapshots(account["id"])
    if snapshots:
        df_snap = pd.DataFrame(snapshots)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_snap["snap_date"],
            y=df_snap["balance"],
            mode="lines+markers",
            line=dict(color=utils.BRAND_PRIMARY, width=2),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(0,212,170,0.06)",
            name="Balance",
        ))
        # Drawdown floor line
        floor = account["account_size"] - account["max_drawdown"]
        fig.add_hline(y=floor, line_color=utils.LOSS_COLOR, line_dash="dash",
                      annotation_text=f"  Max DD Floor: ${floor:,.0f}",
                      annotation_font_color=utils.LOSS_COLOR)
        # Profit target line
        target_line = account["account_size"] + account["profit_target"]
        fig.add_hline(y=target_line, line_color=utils.WIN_COLOR, line_dash="dot",
                      annotation_text=f"  Profit Target: ${target_line:,.0f}",
                      annotation_font_color=utils.WIN_COLOR)
        fig.update_layout(
            title=f"{account['firm_name']} — Balance History",
            xaxis_title="Date",
            yaxis_title="Balance ($)",
            height=320,
        )
        utils.apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# ── Prop Firm Rules Reference ──────────────────────────────────────────────────
st.markdown('<div class="section-header">Common Prop Firm Rules Reference</div>', unsafe_allow_html=True)

rules_data = {
    "Firm": ["FTMO", "Apex Trader Funding", "TopStep", "My Forex Funds", "The Funded Trader"],
    "Account Sizes": ["$10K–$200K", "$25K–$300K", "$50K–$150K", "$10K–$200K", "$5K–$200K"],
    "Profit Target": ["10%", "6%", "6%", "8–10%", "8–10%"],
    "Max Drawdown": ["10%", "6%", "6%", "12%", "10–12%"],
    "Daily Loss Limit": ["5%", "3%", "3%", "5%", "5%"],
    "Time Limit": ["30 days", "None", "None", "None", "None"],
}
df_rules = pd.DataFrame(rules_data)
st.dataframe(df_rules, use_container_width=True, hide_index=True)
st.caption("Note: Rules change frequently. Always verify with the firm's official documentation.")
