"""
TraderStat — Database Layer
SQLite-based persistence for all trading data.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "traderstat.db")


def get_connection():
    """Return a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialise all tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Trade Journal ──────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       TEXT    NOT NULL DEFAULT 'default',
            trade_date    TEXT    NOT NULL,
            ticker        TEXT    NOT NULL,
            direction     TEXT    NOT NULL CHECK(direction IN ('Long','Short')),
            entry_price   REAL    NOT NULL,
            stop_loss     REAL    NOT NULL,
            exit_price    REAL    NOT NULL,
            position_size REAL    NOT NULL,
            strategy      TEXT,
            notes         TEXT,
            -- Calculated fields stored for fast retrieval
            pnl           REAL,
            r_multiple    REAL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Prop Firm Accounts ─────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prop_accounts (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           TEXT    NOT NULL DEFAULT 'default',
            firm_name         TEXT    NOT NULL,
            account_size      REAL    NOT NULL,
            profit_target     REAL    NOT NULL,
            max_drawdown      REAL    NOT NULL,
            daily_loss_limit  REAL    NOT NULL,
            current_balance   REAL    NOT NULL,
            start_date        TEXT    NOT NULL,
            notes             TEXT,
            created_at        TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Prop Firm Daily Snapshots ──────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prop_snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  INTEGER NOT NULL REFERENCES prop_accounts(id),
            snap_date   TEXT    NOT NULL,
            balance     REAL    NOT NULL,
            daily_pnl   REAL    NOT NULL,
            notes       TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ── Trade Journal CRUD ─────────────────────────────────────────────────────────

def insert_trade(user_id, trade_date, ticker, direction, entry_price,
                 stop_loss, exit_price, position_size, strategy, notes):
    """Insert a new trade and return its id."""
    risk_per_unit = abs(entry_price - stop_loss)
    if direction == "Long":
        pnl = (exit_price - entry_price) * position_size
    else:
        pnl = (entry_price - exit_price) * position_size

    r_multiple = (pnl / (risk_per_unit * position_size)) if risk_per_unit > 0 else 0

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trades
            (user_id, trade_date, ticker, direction, entry_price,
             stop_loss, exit_price, position_size, strategy, notes, pnl, r_multiple)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (user_id, trade_date, ticker, direction, entry_price,
          stop_loss, exit_price, position_size, strategy, notes,
          round(pnl, 4), round(r_multiple, 4)))
    conn.commit()
    trade_id = cur.lastrowid
    conn.close()
    return trade_id


def get_trades(user_id="default"):
    """Return all trades for a user as a list of dicts."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM trades WHERE user_id = ?
        ORDER BY trade_date DESC, created_at DESC
    """, (user_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_trade(trade_id, user_id="default"):
    """Delete a trade by id."""
    conn = get_connection()
    conn.execute("DELETE FROM trades WHERE id=? AND user_id=?", (trade_id, user_id))
    conn.commit()
    conn.close()


# ── Prop Firm CRUD ─────────────────────────────────────────────────────────────

def insert_prop_account(user_id, firm_name, account_size, profit_target,
                        max_drawdown, daily_loss_limit, current_balance,
                        start_date, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prop_accounts
            (user_id, firm_name, account_size, profit_target, max_drawdown,
             daily_loss_limit, current_balance, start_date, notes)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (user_id, firm_name, account_size, profit_target, max_drawdown,
          daily_loss_limit, current_balance, start_date, notes))
    conn.commit()
    acct_id = cur.lastrowid
    conn.close()
    return acct_id


def get_prop_accounts(user_id="default"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM prop_accounts WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def update_prop_balance(account_id, new_balance, user_id="default"):
    conn = get_connection()
    conn.execute("""
        UPDATE prop_accounts SET current_balance=? WHERE id=? AND user_id=?
    """, (new_balance, account_id, user_id))
    conn.commit()
    conn.close()


def delete_prop_account(account_id, user_id="default"):
    conn = get_connection()
    conn.execute("DELETE FROM prop_accounts WHERE id=? AND user_id=?", (account_id, user_id))
    conn.execute("DELETE FROM prop_snapshots WHERE account_id=?", (account_id,))
    conn.commit()
    conn.close()


def insert_prop_snapshot(account_id, snap_date, balance, daily_pnl, notes=""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO prop_snapshots (account_id, snap_date, balance, daily_pnl, notes)
        VALUES (?,?,?,?,?)
    """, (account_id, snap_date, balance, daily_pnl, notes))
    conn.commit()
    conn.close()


def get_prop_snapshots(account_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM prop_snapshots WHERE account_id=?
        ORDER BY snap_date ASC
    """, (account_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
