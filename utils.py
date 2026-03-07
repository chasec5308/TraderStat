"""
TraderStat — Shared Utilities
Styling, metrics calculation, and chart helpers.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Brand colours ──────────────────────────────────────────────────────────────
BRAND_PRIMARY   = "#00D4AA"   # teal-green
BRAND_SECONDARY = "#1A1A2E"   # deep navy
BRAND_ACCENT    = "#E94560"   # red-pink for losses / warnings
BRAND_SURFACE   = "#16213E"   # card background
BRAND_TEXT      = "#EAEAEA"   # light text
WIN_COLOR       = "#00D4AA"
LOSS_COLOR      = "#E94560"
NEUTRAL_COLOR   = "#A0AEC0"

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,33,62,0.6)",
        font=dict(color=BRAND_TEXT, family="Inter, sans-serif"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=BRAND_TEXT)),
        margin=dict(l=40, r=20, t=40, b=40),
    )
)


def apply_plotly_theme(fig):
    fig.update_layout(**PLOTLY_TEMPLATE["layout"])
    return fig


# ── Trade Statistics ───────────────────────────────────────────────────────────

def compute_stats(trades: list[dict]) -> dict:
    """Compute aggregate statistics from a list of trade dicts."""
    if not trades:
        return {}

    df = pd.DataFrame(trades)
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0)
    df["r_multiple"] = pd.to_numeric(df["r_multiple"], errors="coerce").fillna(0)

    total_trades = len(df)
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] <= 0]

    win_rate = len(wins) / total_trades * 100 if total_trades else 0
    avg_win  = wins["pnl"].mean() if len(wins) else 0
    avg_loss = losses["pnl"].mean() if len(losses) else 0
    profit_factor = (wins["pnl"].sum() / abs(losses["pnl"].sum())
                     if losses["pnl"].sum() != 0 else float("inf"))
    avg_r    = df["r_multiple"].mean()
    total_pnl = df["pnl"].sum()

    # Equity curve
    df_sorted = df.sort_values("trade_date")
    df_sorted["equity"] = df_sorted["pnl"].cumsum()

    # Max drawdown
    equity = df_sorted["equity"].values
    peak = np.maximum.accumulate(equity)
    drawdown = equity - peak
    max_dd = drawdown.min() if len(drawdown) else 0

    # Expectancy = (WinRate * AvgWin) + (LossRate * AvgLoss)
    loss_rate = 1 - (win_rate / 100)
    expectancy = (win_rate / 100 * avg_win) + (loss_rate * avg_loss)

    return {
        "total_trades":   total_trades,
        "wins":           len(wins),
        "losses":         len(losses),
        "win_rate":       round(win_rate, 1),
        "avg_win":        round(avg_win, 2),
        "avg_loss":       round(avg_loss, 2),
        "profit_factor":  round(profit_factor, 2),
        "avg_r":          round(avg_r, 3),
        "total_pnl":      round(total_pnl, 2),
        "max_drawdown":   round(max_dd, 2),
        "expectancy":     round(expectancy, 2),
        "df_sorted":      df_sorted,
    }


# ── Chart Builders ─────────────────────────────────────────────────────────────

def equity_curve_chart(df_sorted: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted["trade_date"],
        y=df_sorted["equity"],
        mode="lines+markers",
        line=dict(color=BRAND_PRIMARY, width=2.5),
        marker=dict(size=5, color=BRAND_PRIMARY),
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.08)",
        name="Equity",
    ))
    fig.update_layout(title="Equity Curve", xaxis_title="Date", yaxis_title="Cumulative P&L ($)")
    return apply_plotly_theme(fig)


def win_rate_donut(win_rate: float):
    loss_rate = 100 - win_rate
    fig = go.Figure(go.Pie(
        values=[win_rate, loss_rate],
        labels=["Wins", "Losses"],
        hole=0.65,
        marker=dict(colors=[WIN_COLOR, LOSS_COLOR]),
        textinfo="percent",
        hoverinfo="label+percent",
    ))
    fig.update_layout(
        title="Win Rate",
        annotations=[dict(text=f"{win_rate:.1f}%", x=0.5, y=0.5,
                          font_size=22, font_color=BRAND_PRIMARY, showarrow=False)],
        showlegend=True,
    )
    return apply_plotly_theme(fig)


def r_distribution_chart(df: pd.DataFrame):
    colors = [WIN_COLOR if r > 0 else LOSS_COLOR for r in df["r_multiple"]]
    fig = go.Figure(go.Bar(
        x=list(range(1, len(df) + 1)),
        y=df["r_multiple"],
        marker_color=colors,
        name="R Multiple",
    ))
    fig.add_hline(y=0, line_color="white", line_dash="dot", opacity=0.4)
    fig.update_layout(title="R Multiple per Trade", xaxis_title="Trade #", yaxis_title="R")
    return apply_plotly_theme(fig)


def strategy_performance_chart(df: pd.DataFrame):
    if "strategy" not in df.columns or df["strategy"].isna().all():
        return None
    grp = df.groupby("strategy")["pnl"].sum().reset_index()
    grp.columns = ["Strategy", "Total P&L"]
    colors = [WIN_COLOR if v >= 0 else LOSS_COLOR for v in grp["Total P&L"]]
    fig = go.Figure(go.Bar(
        x=grp["Strategy"],
        y=grp["Total P&L"],
        marker_color=colors,
    ))
    fig.update_layout(title="P&L by Strategy", xaxis_title="Strategy", yaxis_title="Total P&L ($)")
    return apply_plotly_theme(fig)


def monthly_pnl_chart(df: pd.DataFrame):
    df = df.copy()
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")
    df["month"] = df["trade_date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["pnl"].sum().reset_index()
    colors = [WIN_COLOR if v >= 0 else LOSS_COLOR for v in monthly["pnl"]]
    fig = go.Figure(go.Bar(
        x=monthly["month"],
        y=monthly["pnl"],
        marker_color=colors,
    ))
    fig.update_layout(title="Monthly P&L", xaxis_title="Month", yaxis_title="P&L ($)")
    return apply_plotly_theme(fig)


# ── Risk Calculator Helpers ────────────────────────────────────────────────────

def calculate_position_size(account_size: float, risk_pct: float,
                             entry: float, stop: float,
                             contract_type: str = "Stocks") -> dict:
    """Return position sizing data for a given risk setup."""
    dollar_risk = account_size * (risk_pct / 100)
    risk_per_unit = abs(entry - stop)

    if risk_per_unit == 0:
        return {"error": "Entry and stop loss cannot be the same price."}

    raw_size = dollar_risk / risk_per_unit

    # Contract-specific rounding
    if contract_type in ("Futures", "Options"):
        position_size = max(1, round(raw_size))
    else:
        position_size = round(raw_size, 2)

    actual_dollar_risk = risk_per_unit * position_size

    # Profit targets (1R, 2R, 3R)
    direction = "long" if entry > stop else "short"
    r = risk_per_unit
    if direction == "long":
        targets = {
            "1R": round(entry + r, 4),
            "2R": round(entry + 2 * r, 4),
            "3R": round(entry + 3 * r, 4),
        }
    else:
        targets = {
            "1R": round(entry - r, 4),
            "2R": round(entry - 2 * r, 4),
            "3R": round(entry - 3 * r, 4),
        }

    return {
        "position_size":    position_size,
        "dollar_risk":      round(actual_dollar_risk, 2),
        "risk_per_unit":    round(risk_per_unit, 4),
        "profit_targets":   targets,
        "direction":        direction,
        "contract_type":    contract_type,
    }


# ── Prop Firm Helpers ──────────────────────────────────────────────────────────

def prop_firm_status(account: dict) -> dict:
    """Compute derived metrics for a prop firm account."""
    size    = account["account_size"]
    balance = account["current_balance"]
    target  = account["profit_target"]
    max_dd  = account["max_drawdown"]
    daily   = account["daily_loss_limit"]

    profit_needed   = size + target - balance
    drawdown_used   = size - balance
    drawdown_left   = max_dd - drawdown_used
    pct_to_target   = min(100, max(0, (balance - size) / target * 100)) if target > 0 else 0
    pct_dd_used     = min(100, max(0, drawdown_used / max_dd * 100)) if max_dd > 0 else 0

    status = "ON TRACK"
    if drawdown_left <= daily:
        status = "DANGER"
    elif pct_dd_used >= 70:
        status = "WARNING"

    return {
        "profit_needed":  round(profit_needed, 2),
        "drawdown_used":  round(drawdown_used, 2),
        "drawdown_left":  round(drawdown_left, 2),
        "pct_to_target":  round(pct_to_target, 1),
        "pct_dd_used":    round(pct_dd_used, 1),
        "status":         status,
        "daily_limit":    daily,
    }
