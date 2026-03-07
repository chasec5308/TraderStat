"""
TraderStat — Tool 2: Risk Calculator
Calculate correct position size based on account risk parameters.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import utils

st.set_page_config(
    page_title="Risk Calculator | TraderStat",
    page_icon="🧮",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.result-card {
    background: linear-gradient(135deg, #16213E 0%, #1A1A2E 100%);
    border: 1px solid rgba(0,212,170,0.25);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 16px;
}
.result-label { color: #A0AEC0; font-size: 0.8rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.result-value { color: #00D4AA; font-size: 2.2rem; font-weight: 700; }
.result-sub   { color: #EAEAEA; font-size: 0.9rem; margin-top: 4px; }

.target-card {
    background: rgba(0,212,170,0.06);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 10px;
}
.target-label { color: #A0AEC0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }
.target-price { color: #00D4AA; font-size: 1.4rem; font-weight: 700; }
.target-r     { color: #EAEAEA; font-size: 0.85rem; }

.warning-box {
    background: rgba(233,69,96,0.1);
    border: 1px solid rgba(233,69,96,0.4);
    border-radius: 10px;
    padding: 14px 18px;
    color: #E94560;
    font-weight: 500;
}
.info-box {
    background: rgba(0,212,170,0.06);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 10px;
    padding: 14px 18px;
    color: #EAEAEA;
}
.section-header { color: #00D4AA; font-size: 1.1rem; font-weight: 600; margin: 24px 0 12px; border-bottom: 1px solid rgba(0,212,170,0.2); padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown("# 🧮 Risk Calculator")
st.markdown("Calculate your exact position size to never risk more than you intend.")
st.markdown("---")

col_input, col_result = st.columns([1, 1], gap="large")

# ── Inputs ─────────────────────────────────────────────────────────────────────
with col_input:
    st.markdown('<div class="section-header">Trade Parameters</div>', unsafe_allow_html=True)

    contract_type = st.selectbox(
        "Contract / Instrument Type",
        ["Stocks", "Futures", "Options"],
        help="Futures and options round to whole contracts; stocks allow fractional shares."
    )

    account_size = st.number_input(
        "Account Size ($)",
        min_value=100.0,
        max_value=10_000_000.0,
        value=25_000.0,
        step=500.0,
        format="%.2f",
        help="Your total trading account balance."
    )

    risk_pct = st.slider(
        "Risk Per Trade (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Professional traders typically risk 0.5–2% per trade."
    )

    st.markdown("")
    col_e, col_s = st.columns(2)
    with col_e:
        entry_price = st.number_input(
            "Entry Price",
            min_value=0.0001,
            value=100.0,
            step=0.01,
            format="%.4f"
        )
    with col_s:
        stop_loss = st.number_input(
            "Stop Loss Price",
            min_value=0.0001,
            value=98.0,
            step=0.01,
            format="%.4f"
        )

    # Futures-specific multiplier hint
    if contract_type == "Futures":
        st.markdown("""
        <div class="info-box">
        <strong>Futures Note:</strong> Position size shown is in contracts.
        Common multipliers: ES = $50/pt, NQ = $20/pt, MES = $5/pt, MNQ = $2/pt.
        Adjust your stop distance accordingly.
        </div>
        """, unsafe_allow_html=True)

    if contract_type == "Options":
        st.markdown("""
        <div class="info-box">
        <strong>Options Note:</strong> Each contract controls 100 shares.
        Enter the option premium as your entry price and your max loss as stop.
        </div>
        """, unsafe_allow_html=True)

    calculate = st.button("⚡ Calculate Position Size", type="primary", use_container_width=True)

# ── Results ────────────────────────────────────────────────────────────────────
with col_result:
    st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)

    if calculate or True:  # Always show on load with defaults
        result = utils.calculate_position_size(
            account_size=account_size,
            risk_pct=risk_pct,
            entry=entry_price,
            stop=stop_loss,
            contract_type=contract_type,
        )

        if "error" in result:
            st.markdown(f'<div class="warning-box">⚠️ {result["error"]}</div>', unsafe_allow_html=True)
        else:
            unit_label = "Contracts" if contract_type in ("Futures", "Options") else "Shares"
            direction_label = "🟢 LONG" if result["direction"] == "long" else "🔴 SHORT"

            st.markdown(f"""
            <div class="result-card">
                <div class="result-label">Position Size</div>
                <div class="result-value">{result['position_size']:,} {unit_label}</div>
                <div class="result-sub">{direction_label} &nbsp;|&nbsp; {contract_type}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Dollar Risk</div>
                    <div class="result-value" style="font-size:1.6rem">${result['dollar_risk']:,.2f}</div>
                    <div class="result-sub">{risk_pct}% of ${account_size:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Risk Per Unit</div>
                    <div class="result-value" style="font-size:1.6rem">${result['risk_per_unit']:,.4f}</div>
                    <div class="result-sub">|Entry − Stop|</div>
                </div>
                """, unsafe_allow_html=True)

            # Profit Targets
            st.markdown('<div class="section-header">Profit Targets</div>', unsafe_allow_html=True)
            t1, t2, t3 = st.columns(3)
            targets = result["profit_targets"]
            for col, (label, price) in zip([t1, t2, t3], targets.items()):
                r_num = int(label[0])
                dollar_gain = result["dollar_risk"] * r_num
                with col:
                    st.markdown(f"""
                    <div class="target-card">
                        <div class="target-label">{label} Target</div>
                        <div class="target-price">{price:,.4f}</div>
                        <div class="target-r">+${dollar_gain:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Risk/Reward Visualisation
            st.markdown('<div class="section-header">Risk / Reward Visual</div>', unsafe_allow_html=True)

            prices = [stop_loss, entry_price] + list(targets.values())
            labels = ["Stop Loss", "Entry"] + list(targets.keys())
            colors = [utils.LOSS_COLOR, "#FFFFFF",
                      utils.WIN_COLOR, utils.WIN_COLOR, utils.WIN_COLOR]

            fig = go.Figure()
            for i, (p, l, c) in enumerate(zip(prices, labels, colors)):
                fig.add_hline(
                    y=p, line_color=c, line_width=1.5,
                    line_dash="solid" if l in ("Entry", "Stop Loss") else "dot",
                    annotation_text=f"  {l}: {p:,.4f}",
                    annotation_font_color=c,
                    annotation_position="right",
                )

            fig.update_layout(
                height=320,
                yaxis_title="Price",
                xaxis=dict(visible=False),
                showlegend=False,
            )
            utils.apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

# ── Risk Education ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">Risk Management Rules</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
rules = [
    ("🎯 The 1% Rule", "Never risk more than 1–2% of your account on a single trade. This ensures you can survive 50+ consecutive losses before blowing up."),
    ("📐 Position Sizing", "Your position size is determined by your risk, not your conviction. Bigger account ≠ bigger size. Risk controls size."),
    ("🔄 Consistency", "Use the same risk % on every trade. Varying risk leads to emotional decisions and inconsistent results."),
]
for col, (title, body) in zip([col1, col2, col3], rules):
    with col:
        st.markdown(f"""
        <div class="result-card" style="text-align:left">
            <div style="font-size:1.1rem; font-weight:600; color:#00D4AA; margin-bottom:8px">{title}</div>
            <div style="color:#EAEAEA; font-size:0.88rem; line-height:1.6">{body}</div>
        </div>
        """, unsafe_allow_html=True)
