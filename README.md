# 📊 TraderStat — Trading Tools Micro-SaaS

> Professional trading tools for futures, options, and prop firm traders. Built with Python + Streamlit + SQLite.

---

## What's Inside

TraderStat is a three-tool trading software suite designed to generate recurring subscription revenue from retail traders.

| Tool | Description |
| :--- | :--- |
| **📒 Trade Journal** | Log trades, auto-calculate R multiples and P&L, visualise equity curve, win rate, and strategy performance |
| **🧮 Risk Calculator** | Calculate exact position size for stocks, futures, and options based on account risk parameters |
| **🏦 Prop Firm Tracker** | Monitor prop firm evaluation progress, drawdown limits, and profit targets with live danger alerts |

---

## Tech Stack

- **Frontend & Backend**: Python 3.11 + Streamlit 1.32+
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **Charts**: Plotly (interactive, dark-themed)
- **Hosting**: Streamlit Community Cloud (free) or Render ($7/month)

---

## Running Locally

**1. Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/traderstat.git
cd traderstat
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the app:**
```bash
streamlit run Home.py
```

**4. Open your browser:**
Navigate to `http://localhost:8501`

---

## Project Structure

```
traderstat/
├── Home.py                    # Main dashboard (app entry point)
├── database.py                # SQLite database layer (all CRUD operations)
├── utils.py                   # Statistics, chart builders, risk calculator logic
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml            # Theme and server configuration
├── pages/
│   ├── 1_Trade_Journal.py     # Tool 1: Trade Journal with analytics
│   ├── 2_Risk_Calculator.py   # Tool 2: Position size calculator
│   └── 3_Prop_Firm_Tracker.py # Tool 3: Prop firm evaluation tracker
├── data/
│   └── traderstat.db          # SQLite database (auto-created on first run)
├── landing/
│   └── index.html             # Marketing landing page (standalone HTML)
└── docs/
    └── LAUNCH_GUIDE.md        # Deployment, monetization, and marketing guide
```

---

## Deployment

See `docs/LAUNCH_GUIDE.md` for full instructions. Short version:

**Streamlit Cloud (Free):**
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set main file to `Home.py`, deploy

**Render ($7/month, persistent disk):**
1. Push to GitHub
2. Create Web Service on Render
3. Build: `pip install -r requirements.txt`
4. Start: `streamlit run Home.py --server.port $PORT --server.address 0.0.0.0`

---

## Monetization

- **Free Tier**: Risk Calculator (unlimited) + 20 journal entries
- **Pro Tier**: $9/month — Unlimited journal, all analytics, Prop Firm Tracker
- **Payment**: Stripe Payment Links (no backend required to start)

---

## Revenue Goal

| Metric | Target |
| :--- | :--- |
| Paying users | 100 |
| Monthly price | $9 |
| Monthly revenue | **$900 MRR** |
| Annual revenue | **$10,800** |

---

## License

MIT License. Built for commercial use.
