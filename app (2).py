"""
╔══════════════════════════════════════════════════════════════════╗
║  PYKUPZ INSTITUTIONAL TERMINAL  v7                              ║
║  78-Stock Research Terminal · Multi-Source Live Data · Q1 2026  ║
╠══════════════════════════════════════════════════════════════════╣
║  DATA SOURCES (in priority order):                              ║
║  1. Financial Modeling Prep (FMP) — free key at fmp.com        ║
║     → Real-time quotes, income stmt, ratios, earnings           ║
║  2. yfinance — Python wrapper for Yahoo Finance                  ║
║     → Price history, financial statements, backup quotes        ║
║  3. stocks_data.json — your Pyk-Inv-List Excel data             ║
║     → Always works, 100% offline fallback                       ║
║  4. Gemini AI — analysis, thesis, scenarios, risk matrix        ║
╠══════════════════════════════════════════════════════════════════╣
║  DEPLOY: Upload app.py + stocks_data.json + requirements.txt    ║
║  to GitHub → share.streamlit.io                                 ║
║                                                                  ║
║  requirements.txt:                                               ║
║    streamlit==1.32.0                                             ║
║    yfinance==0.2.54                                              ║
║    pandas==2.2.1                                                 ║
║    numpy==1.26.4                                                 ║
║    plotly==5.20.0                                                ║
║    requests==2.31.0                                              ║
║    google-generativeai==0.8.0                                    ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ── Guaranteed safe imports ──────────────────────────────────────
import sys, os, json, re, time, math, warnings
from datetime import datetime, timedelta
from functools import wraps
warnings.filterwarnings("ignore")

import streamlit as st

# ─────────────────── IMPORT GUARD ────────────────────────────────
def safe_import(package, attr=None):
    """Import with user-friendly error instead of crash."""
    import importlib
    try:
        mod = importlib.import_module(package)
        return getattr(mod, attr) if attr else mod
    except ImportError:
        st.error(
            f"**Package missing:** `{package}`\n\n"
            f"Make sure `requirements.txt` contains `{package.split('.')[0]}` "
            f"and **reboot** the app on Streamlit Cloud."
        )
        st.stop()

pd   = safe_import("pandas")
np   = safe_import("numpy")
go   = safe_import("plotly.graph_objects")
px   = safe_import("plotly.express")
make_subplots = safe_import("plotly.subplots", "make_subplots")
requests = safe_import("requests")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

# ─────────────────── PAGE CONFIG ─────────────────────────────────
st.set_page_config(
    page_title="PYKUPZ · Institutional Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────── MASTER CSS ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:#030508; --bg1:#080a0f; --bg2:#0c0e14; --bg3:#11141b; --bg4:#171b24;
  --bd:#1c2030;  --bd2:#262d3f;
  --g:#00d97e;  --g2:rgba(0,217,126,.1);  --g3:rgba(0,217,126,.05);
  --r:#f04444;  --r2:rgba(240,68,68,.08);
  --a:#f5a623;  --a2:rgba(245,166,35,.08);
  --b:#4f8ef7;  --b2:rgba(79,142,247,.08);
  --c:#22d3ee;  --c2:rgba(34,211,238,.08);
  --p:#a78bfa;  --p2:rgba(167,139,250,.08);
  --t:#b8c4d8;  --t2:#5a6480;  --t3:#2a3040;
  --w:#eef2ff;
  --mono:'IBM Plex Mono',monospace;
  --sans:'IBM Plex Sans',sans-serif;
}

/* Reset */
html,body,[class*="css"],.main{background:var(--bg)!important;color:var(--t)!important}
.block-container{padding:0!important;max-width:100%!important;background:var(--bg)!important}
*{box-sizing:border-box}

/* Scrollbar */
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:var(--bg1)}
::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:var(--g)}

/* Sidebar */
section[data-testid="stSidebar"]{background:var(--bg1)!important;border-right:1px solid var(--bd)!important}
section[data-testid="stSidebar"]>div{padding:0!important}
section[data-testid="stSidebar"] *{color:var(--t)!important}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox>div>div{
  background:var(--bg2)!important;border:1px solid var(--bd2)!important;
  color:var(--w)!important;font-family:var(--mono)!important;font-size:11px!important;border-radius:3px!important}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:var(--bg1)!important;border-bottom:1px solid var(--bd)!important;padding:0 16px!important;gap:0!important}
.stTabs [data-baseweb="tab"]{font-family:var(--mono)!important;font-size:10px!important;letter-spacing:1.5px!important;color:var(--t3)!important;padding:10px 18px!important;border-bottom:2px solid transparent!important;background:transparent!important;text-transform:uppercase!important}
.stTabs [aria-selected="true"]{color:var(--g)!important;border-bottom-color:var(--g)!important}
.stTabs [data-baseweb="tab-panel"]{background:var(--bg)!important;padding:16px!important}

/* Buttons */
.stButton>button{background:transparent!important;border:1px solid var(--bd2)!important;color:var(--t2)!important;font-family:var(--mono)!important;font-size:10px!important;letter-spacing:1px!important;border-radius:3px!important;padding:5px 14px!important;transition:all .15s!important}
.stButton>button:hover{border-color:var(--g)!important;color:var(--g)!important;background:var(--g3)!important}

/* Inputs */
.stTextInput input,.stTextArea textarea{background:var(--bg2)!important;border:1px solid var(--bd)!important;color:var(--w)!important;font-family:var(--mono)!important;font-size:11px!important;border-radius:3px!important}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--g)!important;box-shadow:0 0 0 2px rgba(0,217,126,.15)!important}
.stSelectbox>div>div{background:var(--bg2)!important;border:1px solid var(--bd)!important;color:var(--w)!important;font-family:var(--mono)!important;font-size:11px!important}

/* Metrics */
div[data-testid="metric-container"]{background:var(--bg2)!important;border:1px solid var(--bd)!important;border-radius:4px!important;padding:10px 14px!important}
div[data-testid="metric-container"] label{font-family:var(--mono)!important;font-size:8px!important;letter-spacing:1.5px!important;color:var(--t3)!important;text-transform:uppercase!important}
div[data-testid="metric-container"]>div{color:var(--w)!important;font-family:var(--mono)!important}

/* Dataframe */
.stDataFrame iframe{border:1px solid var(--bd)!important;border-radius:4px!important}

/* Expander */
details{background:var(--bg2)!important;border:1px solid var(--bd)!important;border-radius:4px!important}
.streamlit-expanderHeader{font-family:var(--mono)!important;font-size:10px!important;letter-spacing:1px!important;color:var(--t2)!important;text-transform:uppercase!important}
.streamlit-expanderContent{background:var(--bg2)!important}

/* Progress */
.stProgress .st-bo{background:var(--g)!important}
.stProgress>div{background:var(--bg3)!important;border-radius:2px!important}

/* Alerts */
.stAlert{background:var(--bg2)!important;border-radius:4px!important}

/* Component classes */
.pyk-header{background:var(--bg1);border-bottom:1px solid var(--bd);padding:10px 20px;display:flex;align-items:center;justify-content:space-between}
.pyk-logo{font-family:var(--mono);font-size:16px;font-weight:700;letter-spacing:4px;color:var(--g)}
.pyk-sub{font-family:var(--mono);font-size:8px;letter-spacing:2px;color:var(--t3);margin-top:2px}

.kpi{background:var(--bg2);border:1px solid var(--bd);border-radius:4px;padding:10px 14px;margin:3px 0}
.kpi.g{border-top:2px solid var(--g)}.kpi.r{border-top:2px solid var(--r)}
.kpi.a{border-top:2px solid var(--a)}.kpi.b{border-top:2px solid var(--b)}
.kpi.c{border-top:2px solid var(--c)}.kpi.p{border-top:2px solid var(--p)}
.kpi-v{font-family:var(--mono);font-size:17px;font-weight:600;color:var(--w);line-height:1.1}
.kpi-l{font-family:var(--mono);font-size:8px;letter-spacing:1.5px;color:var(--t3);text-transform:uppercase;margin-top:3px}
.kpi-s{font-family:var(--mono);font-size:9px;color:var(--t2);margin-top:2px}

.sh{font-family:var(--mono);font-size:9px;letter-spacing:2.5px;color:var(--t3);text-transform:uppercase;border-bottom:1px solid var(--bd);padding-bottom:5px;margin:12px 0 10px}
.sh.g{color:var(--g)}

.dr{display:flex;align-items:center;padding:5px 0;border-bottom:1px solid var(--bg3);font-family:var(--mono);font-size:10px}
.dr:last-child{border-bottom:none}
.dk{color:var(--t3);min-width:170px;flex-shrink:0}
.dv{color:var(--w)}

.sig{display:inline-block;padding:2px 8px;border-radius:2px;font-family:var(--mono);font-size:9px;letter-spacing:.5px;font-weight:600}
.sig-sb{background:rgba(0,217,126,.15);border:1px solid rgba(0,217,126,.4);color:#00d97e}
.sig-b{background:rgba(0,217,126,.1);border:1px solid rgba(0,217,126,.3);color:#00d97e}
.sig-a{background:rgba(34,211,238,.1);border:1px solid rgba(34,211,238,.3);color:#22d3ee}
.sig-h{background:rgba(79,142,247,.1);border:1px solid rgba(79,142,247,.3);color:#4f8ef7}
.sig-w{background:rgba(245,166,35,.1);border:1px solid rgba(245,166,35,.3);color:#f5a623}
.sig-s{background:rgba(240,68,68,.1);border:1px solid rgba(240,68,68,.3);color:#f04444}

.ai-p{background:linear-gradient(135deg,#030508 0%,#070910 60%,#040810 100%);border:1px solid rgba(79,142,247,.3);border-radius:5px;padding:16px;margin:6px 0;position:relative}
.ai-p::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;border-radius:5px 5px 0 0;background:linear-gradient(90deg,#4f8ef7,#22d3ee,#00d97e,#a78bfa)}
.ai-badge{display:inline-block;background:rgba(79,142,247,.12);border:1px solid rgba(79,142,247,.3);border-radius:2px;padding:1px 7px;font-family:var(--mono);font-size:8px;color:#4f8ef7;letter-spacing:1px}

.tl{border-left:2px solid var(--bd2);padding:5px 12px;margin-bottom:6px}
.tl-n{border-left-color:var(--g)}.tl-m{border-left-color:var(--a)}.tl-l{border-left-color:var(--t3)}

.sc-bear{background:var(--r2);border:1px solid rgba(240,68,68,.2);border-top:2px solid var(--r);border-radius:4px;padding:16px;text-align:center}
.sc-base{background:var(--g3);border:1px solid rgba(0,217,126,.2);border-top:2px solid var(--g);border-radius:4px;padding:16px;text-align:center}
.sc-bull{background:var(--a2);border:1px solid rgba(245,166,35,.2);border-top:2px solid var(--a);border-radius:4px;padding:16px;text-align:center}

.mc{background:var(--bg2);border:1px solid var(--bd);border-radius:3px;padding:10px 14px;margin-bottom:6px}
.mc:hover{border-color:var(--bd2)}

.rq-hh{background:rgba(240,68,68,.05);border:1px solid rgba(240,68,68,.2);border-radius:3px;padding:10px}
.rq-hl{background:rgba(245,166,35,.04);border:1px solid rgba(245,166,35,.2);border-radius:3px;padding:10px}
.rq-lh{background:rgba(245,166,35,.04);border:1px solid rgba(245,166,35,.2);border-radius:3px;padding:10px}
.rq-ll{background:rgba(0,217,126,.03);border:1px solid rgba(0,217,126,.15);border-radius:3px;padding:10px}

.ds-panel{background:var(--bg2);border:1px solid var(--bd);border-radius:4px;padding:10px 14px;margin-bottom:8px}
.ds-ok{color:var(--g);font-family:var(--mono);font-size:9px}
.ds-warn{color:var(--a);font-family:var(--mono);font-size:9px}
.ds-err{color:var(--r);font-family:var(--mono);font-size:9px}

/* Ticker tape */
.tape{background:var(--bg1);border-bottom:1px solid var(--bd);padding:5px 0;overflow:hidden;white-space:nowrap}
.tape-inner{display:inline-block;animation:scroll 120s linear infinite}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ti{display:inline-block;margin:0 20px;font-family:var(--mono);font-size:10px}
.ti-g{color:var(--g)}.ti-r{color:var(--r)}.ti-n{color:var(--t3)}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
#  STOCK UNIVERSE (loaded from JSON)
# ═════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_universe():
    paths = [
        "stocks_data.json",
        os.path.join(os.path.dirname(__file__), "stocks_data.json"),
        "data/stocks_data.json",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    st.error(
        "**stocks_data.json not found.**\n\n"
        "Upload `stocks_data.json` to the same folder as `app.py` in your GitHub repo."
    )
    st.stop()

ALL_STOCKS = load_universe()
TICKERS    = [s['ticker'] for s in ALL_STOCKS]

SECTORS = {
    'NVDA':'Semiconductors','ANET':'AI Networking','PLTR':'Gov AI/Analytics',
    'HUBS':'CRM/SaaS','HIMS':'Digital Health','LLY':'Pharma/GLP-1',
    'PMRTY':'Consumer Toys','CRWD':'Cybersecurity','DKNG':'Online Gaming',
    'APP':'Mobile AdTech','AFRM':'BNPL/FinTech','ONON':'Performance Sports',
    'SHOP':'E-Commerce SaaS','NU':'LatAm Digital Bank','NFLX':'Streaming',
    'AVGO':'AI Semiconductors','SPOT':'Audio Streaming','META':'Social/AI Ads',
    'MU':'Memory Chips','FTNT':'Cybersecurity','SOFI':'Digital Banking',
    'ALAB':'AI Connectivity','AMD':'Semiconductors','RDDT':'Social Media',
    'TTD':'Programmatic Ads','AMZN':'Cloud/E-Commerce','ROKU':'CTV Streaming',
    'MELI':'LatAm E-Commerce','PANW':'Cybersecurity','XYZ':'FinTech Payments',
    'TSM':'Semiconductor Foundry','GOOG':'Search/Cloud','MSFT':'Enterprise Cloud',
    'JD':'China E-Commerce','VEEV':'Pharma SaaS','ASML':'Chip Equipment',
    'IREN':'AI/Bitcoin Mining','BKNG':'Online Travel','UBER':'Mobility Platform',
    'HOOD':'Retail Brokerage','BABA':'China E-Commerce','ARGX':'Biotech',
    'NET':'Cloud Security','DUOL':'EdTech','ELF':'Beauty/Consumer',
    'AXP':'Premium Finance','ISRG':'Robotic Surgery','DOCS':'Healthcare IT',
    'RYCEY':'Aerospace/Defence','ETSY':'Craft E-Commerce','UPWK':'Freelance Platform',
    'BRK.B':'Diversified Finance','CRWV':'AI Infrastructure','COIN':'Crypto Exchange',
    'IBKR':'Online Brokerage','BYDDY':'EV/Battery','UPST':'AI Lending',
    'CRM':'Enterprise SaaS','NVO':'Pharma/Obesity','WPLCF':'Cross-Border Payments',
    'KNSL':'Specialty Insurance','ETOR':'Social Trading','MGNI':'AdTech',
    'AAPL':'Consumer Tech','PDD':'China E-Commerce','BIDU':'China Search/AI',
    'TCEHY':'China Internet','MAR':'Global Hospitality','ON':'Power Semiconductors',
    'DOCU':'eSignature SaaS','TSLA':'EV/Energy/AI','ENPH':'Solar/Energy',
    'Peri':'AdTech','TCOM':'Online Travel','FUBO':'Live TV Streaming',
    'GCT':'B2B Marketplace','LC':'AI Lending','NBIS':'AI Infrastructure',
}

SIG_CSS_MAP = {
    'STRONG BUY':'sig-sb','Strong Buy':'sig-sb',
    'BUY':'sig-b','Buy':'sig-b',
    'ACCUMULATE':'sig-a','Accumulate':'sig-a',
    'HOLD':'sig-h','Hold':'sig-h',
    'WATCH':'sig-w','Watch':'sig-w',
    'SELL':'sig-s','Sell':'sig-s','REDUCE':'sig-s',
}
SIG_CLR = {
    'STRONG BUY':'#00d97e','Strong Buy':'#00d97e','BUY':'#00d97e','Buy':'#00d97e',
    'ACCUMULATE':'#22d3ee','Accumulate':'#22d3ee',
    'HOLD':'#4f8ef7','Hold':'#4f8ef7',
    'WATCH':'#f5a623','Watch':'#f5a623',
    'SELL':'#f04444','Sell':'#f04444','REDUCE':'#f04444',
}

# ═════════════════════════════════════════════════════════════════
#  MULTI-SOURCE LIVE DATA ENGINE
# ═════════════════════════════════════════════════════════════════

class DataEngine:
    """
    Multi-source data engine with automatic fallback.

    Priority chain:
    1. FMP (Financial Modeling Prep) — institutional grade, free key
    2. yfinance — Python wrapper, good for history & financials
    3. Excel data (stocks_data.json) — always available, 100% reliable

    Why FMP as primary:
    - Structured JSON API, not web scraping
    - Has real-time quotes, income statements, ratios, earnings
    - 250 free requests/day → enough for 78 stocks with aggressive caching
    - Used by hedge funds, fintech startups, retail platforms
    - Stable: not dependent on website HTML structure

    Why yfinance as backup:
    - Works on Streamlit Cloud (outbound HTTP allowed)
    - Rich financial statement data
    - Good for 5Y price history for charts

    Why NOT Alpha Vantage / Polygon as primary:
    - Alpha Vantage: 25 req/day free = too few for 78 stocks
    - Polygon: free tier is delayed 15 min, requires key for fundamentals
    """

    def __init__(self, fmp_key=""):
        self.fmp_key = fmp_key
        self.fmp_base = "https://financialmodelinprep.com/api/v3"
        self.timeout = 10
        self._status = {}  # Track source health

    def _fmp_get(self, endpoint, params=None):
        """Make FMP API call. Returns dict/list or None on failure."""
        if not self.fmp_key:
            return None
        try:
            url = f"{self.fmp_base}/{endpoint}"
            p = params or {}
            p['apikey'] = self.fmp_key
            r = requests.get(url, params=p, timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                # FMP returns empty list for bad tickers, error dict for bad key
                if isinstance(data, dict) and data.get('Error Message'):
                    return None
                self._status['fmp'] = 'ok'
                return data
            elif r.status_code == 401:
                self._status['fmp'] = 'bad_key'
            else:
                self._status['fmp'] = f'http_{r.status_code}'
            return None
        except Exception as e:
            self._status['fmp'] = f'error: {str(e)[:40]}'
            return None

    @st.cache_data(ttl=180, show_spinner=False)
    def quote_fmp(_self, ticker):
        """Real-time quote from FMP."""
        data = _self._fmp_get(f"quote/{ticker}")
        if data and isinstance(data, list) and len(data) > 0:
            q = data[0]
            return {
                'price': q.get('price'),
                'change': q.get('change'),
                'pct_change': q.get('changesPercentage', 0) / 100,
                'open': q.get('open'),
                'high': q.get('dayHigh'),
                'low': q.get('dayLow'),
                'volume': q.get('volume'),
                'avg_volume': q.get('avgVolume'),
                'market_cap': q.get('marketCap'),
                'pe': q.get('pe'),
                'eps': q.get('eps'),
                'year_high': q.get('yearHigh'),
                'year_low': q.get('yearLow'),
                'prev_close': q.get('previousClose'),
                'shares_outstanding': q.get('sharesOutstanding'),
                'source': 'FMP',
            }
        return None

    @st.cache_data(ttl=180, show_spinner=False)
    def quote_yf(_self, ticker):
        """Backup quote from yfinance."""
        if not YF_AVAILABLE:
            return None
        try:
            h = yf.Ticker(ticker).history(period="5d", timeout=8)
            if h.empty or len(h) < 2:
                return None
            p = float(h['Close'].iloc[-1])
            prev = float(h['Close'].iloc[-2])
            vol = float(h['Volume'].iloc[-1]) if 'Volume' in h.columns else None
            info = {}
            try:
                info = yf.Ticker(ticker).info or {}
            except Exception:
                pass
            return {
                'price': p,
                'change': p - prev,
                'pct_change': (p - prev) / prev,
                'volume': vol,
                'avg_volume': info.get('averageVolume'),
                'market_cap': info.get('marketCap'),
                'pe': info.get('trailingPE'),
                'eps': info.get('trailingEps'),
                'year_high': info.get('fiftyTwoWeekHigh'),
                'year_low': info.get('fiftyTwoWeekLow'),
                'prev_close': prev,
                'shares_outstanding': info.get('sharesOutstanding'),
                'source': 'yfinance',
            }
        except Exception:
            return None

    def get_quote(self, ticker, excel_data=None):
        """Get best available quote. Never returns None."""
        # Try FMP first
        q = self.quote_fmp(ticker)
        if q:
            return q, 'FMP ●'

        # Try yfinance backup
        q = self.quote_yf(ticker)
        if q:
            return q, 'yfinance ●'

        # Fallback to Excel data
        if excel_data:
            p = excel_data.get('price')
            return {
                'price': float(p) if p else None,
                'change': None, 'pct_change': None,
                'volume': None, 'avg_volume': None,
                'market_cap': (excel_data.get('mcap_b') or 0) * 1e9,
                'pe': excel_data.get('pe'),
                'eps': None,
                'year_high': excel_data.get('high'),
                'year_low': None,
                'source': 'Excel',
            }, 'Excel ●'

        return {'price': None, 'source': 'None'}, '⚠ No data'

    @st.cache_data(ttl=3600, show_spinner=False)
    def income_fmp(_self, ticker):
        """Annual income statements from FMP (3 years)."""
        data = _self._fmp_get(f"income-statement/{ticker}", {'limit': 4})
        if not data or not isinstance(data, list):
            return None
        results = []
        for d in data[:4]:
            results.append({
                'date': d.get('date','')[:4],
                'revenue': d.get('revenue'),
                'gross_profit': d.get('grossProfit'),
                'operating_income': d.get('operatingIncome'),
                'ebitda': d.get('ebitda'),
                'net_income': d.get('netIncome'),
                'eps': d.get('eps'),
                'eps_diluted': d.get('epsdiluted'),
                'gross_margin': d.get('grossProfitRatio'),
                'operating_margin': d.get('operatingIncomeRatio'),
                'net_margin': d.get('netIncomeRatio'),
            })
        return results if results else None

    @st.cache_data(ttl=3600, show_spinner=False)
    def cashflow_fmp(_self, ticker):
        """Cash flow statements from FMP (3 years)."""
        data = _self._fmp_get(f"cash-flow-statement/{ticker}", {'limit': 4})
        if not data or not isinstance(data, list):
            return None
        results = []
        for d in data[:4]:
            results.append({
                'date': d.get('date','')[:4],
                'operating_cf': d.get('operatingCashFlow'),
                'capex': d.get('capitalExpenditure'),
                'fcf': d.get('freeCashFlow'),
                'dividends': d.get('dividendsPaid'),
            })
        return results if results else None

    @st.cache_data(ttl=3600, show_spinner=False)
    def balance_fmp(_self, ticker):
        """Balance sheet from FMP."""
        data = _self._fmp_get(f"balance-sheet-statement/{ticker}", {'limit': 4})
        if not data or not isinstance(data, list):
            return None
        results = []
        for d in data[:4]:
            results.append({
                'date': d.get('date','')[:4],
                'cash': d.get('cashAndShortTermInvestments'),
                'total_debt': d.get('totalDebt'),
                'net_debt': d.get('netDebt'),
                'total_assets': d.get('totalAssets'),
                'total_equity': d.get('totalEquity'),
                'current_ratio': d.get('currentRatio'),
            })
        return results if results else None

    @st.cache_data(ttl=3600, show_spinner=False)
    def key_metrics_fmp(_self, ticker):
        """Key financial ratios from FMP."""
        data = _self._fmp_get(f"key-metrics/{ticker}", {'limit': 1})
        if data and isinstance(data, list) and len(data) > 0:
            m = data[0]
            return {
                'pe': m.get('peRatio'),
                'ps': m.get('priceToSalesRatio'),
                'pb': m.get('pbRatio'),
                'peg': m.get('pegRatio'),
                'ev_ebitda': m.get('enterpriseValueOverEBITDA'),
                'roe': m.get('roe'),
                'roa': m.get('roa'),
                'debt_to_equity': m.get('debtToEquity'),
                'current_ratio': m.get('currentRatio'),
                'fcf_yield': m.get('freeCashFlowYield'),
                'dividend_yield': m.get('dividendYield'),
                'revenue_per_share': m.get('revenuePerShare'),
                'book_value': m.get('bookValuePerShare'),
            }
        return None

    @st.cache_data(ttl=3600, show_spinner=False)
    def earnings_fmp(_self, ticker):
        """Earnings history + surprises from FMP."""
        data = _self._fmp_get(f"earnings-surprises/{ticker}")
        if not data or not isinstance(data, list):
            return None
        results = []
        for d in data[:8]:
            results.append({
                'date': d.get('date','')[:10],
                'actual': d.get('actualEarningResult'),
                'estimate': d.get('estimatedEarning'),
                'surprise': (d.get('actualEarningResult',0) or 0) - (d.get('estimatedEarning',0) or 0),
                'beat': (d.get('actualEarningResult',0) or 0) >= (d.get('estimatedEarning',0) or 0),
            })
        return results if results else None

    @st.cache_data(ttl=3600, show_spinner=False)
    def history_yf(_self, ticker, period="5y"):
        """Price history from yfinance (for charts)."""
        if not YF_AVAILABLE:
            return pd.DataFrame()
        try:
            h = yf.Ticker(ticker).history(period=period, timeout=12)
            if h.empty:
                return pd.DataFrame()
            h.index = (pd.to_datetime(h.index).tz_localize(None)
                       if h.index.tzinfo else pd.to_datetime(h.index))
            return h
        except Exception:
            return pd.DataFrame()

    @st.cache_data(ttl=3600, show_spinner=False)
    def income_yf(_self, ticker):
        """Income statement from yfinance (backup)."""
        if not YF_AVAILABLE:
            return None
        try:
            inc = yf.Ticker(ticker).income_stmt
            if inc is None or inc.empty:
                return None
            results = []
            for col in sorted(inc.columns, reverse=True)[:4]:
                def gv(*keys):
                    for k in keys:
                        if k in inc.index:
                            v = inc.loc[k, col]
                            if pd.notna(v): return float(v)
                    return None
                results.append({
                    'date': str(col)[:4],
                    'revenue': gv('Total Revenue','Revenue'),
                    'gross_profit': gv('Gross Profit'),
                    'ebitda': gv('EBITDA','Normalized EBITDA'),
                    'net_income': gv('Net Income','Net Income Common Stockholders'),
                    'eps': gv('Diluted EPS','Basic EPS'),
                })
            return list(reversed(results)) if results else None
        except Exception:
            return None

    @st.cache_data(ttl=3600, show_spinner=False)
    def cashflow_yf(_self, ticker):
        """Cash flow from yfinance (backup)."""
        if not YF_AVAILABLE:
            return None
        try:
            cf = yf.Ticker(ticker).cash_flow
            if cf is None or cf.empty:
                return None
            results = []
            for col in sorted(cf.columns, reverse=True)[:4]:
                def gv(*keys):
                    for k in keys:
                        if k in cf.index:
                            v = cf.loc[k, col]
                            if pd.notna(v): return float(v)
                    return None
                results.append({
                    'date': str(col)[:4],
                    'operating_cf': gv('Operating Cash Flow'),
                    'capex': gv('Capital Expenditure'),
                    'fcf': gv('Free Cash Flow'),
                })
            return list(reversed(results)) if results else None
        except Exception:
            return None

    def get_financials(self, ticker):
        """Get best available financials with source tracking."""
        # Income statement
        inc = self.income_fmp(ticker)
        inc_src = 'FMP' if inc else None
        if not inc:
            inc = self.income_yf(ticker)
            inc_src = 'yfinance' if inc else 'Excel'

        # Cash flow
        cf = self.cashflow_fmp(ticker)
        cf_src = 'FMP' if cf else None
        if not cf:
            cf = self.cashflow_yf(ticker)
            cf_src = 'yfinance' if cf else 'Excel'

        # Balance sheet
        bal = self.balance_fmp(ticker)

        # Key metrics
        metrics = self.key_metrics_fmp(ticker)

        # Earnings
        earnings = self.earnings_fmp(ticker)

        return {
            'income': inc, 'income_src': inc_src,
            'cashflow': cf, 'cf_src': cf_src,
            'balance': bal,
            'metrics': metrics,
            'earnings': earnings,
        }

    def data_status(self):
        """Return human-readable data source status."""
        fmp_ok = bool(self.fmp_key) and self._status.get('fmp','') == 'ok'
        yf_ok  = YF_AVAILABLE
        return {
            'fmp':  ('✓ Connected', '#00d97e') if fmp_ok else
                    ('✗ No key', '#f5a623') if not self.fmp_key else
                    (f'✗ {self._status.get("fmp","")}', '#f04444'),
            'yf':   ('✓ Available', '#00d97e') if yf_ok else ('✗ Not installed', '#f04444'),
            'excel':('✓ Loaded', '#00d97e'),
            'gemini':('✓ Connected', '#00d97e') if st.session_state.get('gkey') else ('✗ No key', '#f5a623'),
        }

# ═════════════════════════════════════════════════════════════════
#  SESSION STATE & ENGINE
# ═════════════════════════════════════════════════════════════════

for k, v in {
    'ticker': 'NVDA',
    'fkey': os.environ.get('FMP_API_KEY', ''),
    'gkey': os.environ.get('GEMINI_API_KEY', ''),
    'ai_cache': {},
    'chat_hist': [],
    'main_view': 'stock',
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

@st.cache_resource
def get_engine(fmp_key):
    return DataEngine(fmp_key)

@st.cache_resource
def get_gemini(key):
    if not key: return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        return genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"temperature": 0.35, "max_output_tokens": 2048}
        )
    except Exception:
        return None

def engine():   return get_engine(st.session_state.fkey)
def ai_model(): return get_gemini(st.session_state.gkey)

# ═════════════════════════════════════════════════════════════════
#  FORMAT HELPERS
# ═════════════════════════════════════════════════════════════════

def _safe_float(v):
    if v is None: return None
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    except: return None

def fn(v, pre='$', suf='', dec=1, na='—'):
    f = _safe_float(v)
    if f is None: return na
    return f"{pre}{f:,.{dec}f}{suf}"

def fm(v, dec=1, na='—'):  # Millions
    f = _safe_float(v)
    if f is None: return na
    if abs(f) >= 1e12: return f"${f/1e12:.{dec}f}T"
    if abs(f) >= 1e9:  return f"${f/1e9:.{dec}f}B"
    if abs(f) >= 1e6:  return f"${f/1e6:.{dec}f}M"
    return f"${f:,.{dec}f}"

def fp(v, mul=True, na='—'):
    f = _safe_float(v)
    if f is None: return na
    f2 = f * (100 if mul else 1)
    return f"{'+' if f2>=0 else ''}{f2:.1f}%"

def fv(v, na='—'):
    f = _safe_float(v)
    if f is None: return na
    return f"{f:.2f}x"

def clr_pct(v, mul=True):
    f = _safe_float(v)
    if f is None: return '#5a6480'
    return '#00d97e' if f * (100 if mul else 1) >= 0 else '#f04444'

def sig_badge(rec):
    rec = str(rec or '').strip()
    css = SIG_CSS_MAP.get(rec, SIG_CSS_MAP.get(rec.upper(), 'sig-w'))
    return f'<span class="sig {css}">{rec.upper()}</span>'

def kpi(val, label, acc='', size=17, sub=''):
    s_html = f'<div class="kpi-s">{sub}</div>' if sub else ''
    return f'<div class="kpi {acc}"><div class="kpi-v" style="font-size:{size}px">{val}</div><div class="kpi-l">{label}</div>{s_html}</div>'

def sh(text, acc=''):
    return f'<div class="sh {acc}">{text}</div>'

def dr(key, val, vc=None):
    vc_s = f' style="color:{vc}"' if vc else ''
    return f'<div class="dr"><span class="dk">{key}</span><span class="dv"{vc_s}>{val}</span></div>'

# ═════════════════════════════════════════════════════════════════
#  CHART BUILDERS
# ═════════════════════════════════════════════════════════════════

_LAYOUT = dict(
    paper_bgcolor='#030508', plot_bgcolor='#080a0f',
    font=dict(family="'IBM Plex Mono',monospace", color='#2a3040', size=9),
    margin=dict(l=8, r=8, t=40, b=8),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)',
                font=dict(size=9, color='#5a6480'), orientation='h', y=1.08, x=0),
    hovermode='x unified',
    hoverlabel=dict(bgcolor='#11141b', bordercolor='#1c2030',
                    font=dict(family="'IBM Plex Mono',monospace", color='#b8c4d8', size=9)),
)
_GRID = dict(gridcolor='#0c0e14', zeroline=False, zerolinecolor='#1c2030',
             tickfont=dict(size=9, color='#2a3040'), showline=True, linecolor='#1c2030')

def _theme(fig, title='', h=380):
    fig.update_layout(**_LAYOUT, title=dict(
        text=title, font=dict(color='#b8c4d8', size=12,
        family="'IBM Plex Mono',monospace"), x=0.01), height=h)
    fig.update_xaxes(**_GRID)
    fig.update_yaxes(**_GRID)
    return fig

def chart_price(ticker, hist):
    if hist is None or hist.empty: return None
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28], vertical_spacing=0.03)
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], name='Price',
        mode='lines', line=dict(color='#00d97e', width=1.5),
        fill='tozeroy', fillcolor='rgba(0,217,126,0.04)',
        hovertemplate='$%{y:.2f}<extra></extra>'
    ), row=1, col=1)
    if len(hist) >= 50:
        ma50 = hist['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(x=ma50.index, y=ma50, name='MA50',
            mode='lines', line=dict(color='#f5a623', width=1, dash='dot')), row=1, col=1)
    if len(hist) >= 200:
        ma200 = hist['Close'].rolling(200).mean()
        fig.add_trace(go.Scatter(x=ma200.index, y=ma200, name='MA200',
            mode='lines', line=dict(color='#a78bfa', width=1, dash='dot')), row=1, col=1)
    vc = ['rgba(0,217,126,.35)' if c >= o else 'rgba(240,68,68,.35)'
          for c, o in zip(hist['Close'], hist['Open'])]
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume',
        marker_color=vc, showlegend=False,
        hovertemplate='%{y:,.0f}<extra></extra>'), row=2, col=1)
    _theme(fig, f'Price & Volume — {ticker}', h=420)
    fig.update_yaxes(row=2, col=1, tickformat='.2s', **_GRID)
    return fig

def chart_revenue(ticker, fin):
    """Revenue + EBITDA + FCF from live data."""
    inc = fin.get('income') or []
    cf  = fin.get('cashflow') or []

    # Merge income + cashflow by date
    cf_map = {d['date']: d for d in cf}
    years, revs, ebitdas, fcfs, nets = [], [], [], [], []

    for d in sorted(inc, key=lambda x: x.get('date',''), reverse=False):
        yr = d.get('date','')
        if not yr: continue
        years.append(yr)
        revs.append((d.get('revenue') or 0) / 1e9)
        ebitdas.append((d.get('ebitda') or 0) / 1e9 if d.get('ebitda') else None)
        nets.append((d.get('net_income') or 0) / 1e9 if d.get('net_income') else None)
        fcf_d = cf_map.get(yr, {})
        fcfs.append((fcf_d.get('fcf') or 0) / 1e9 if fcf_d.get('fcf') else None)

    # Add projections from Excel
    s_data = next((s for s in ALL_STOCKS if s['ticker'] == ticker), {})
    for yr, rv, eb in [
        ('2026E', s_data.get('rev_2026e'), s_data.get('ebitda_2026e')),
        ('2027E', s_data.get('rev_2027e'), s_data.get('ebitda_2027e')),
        ('2028E', s_data.get('rev_2028e'), None),
    ]:
        rv_f = _safe_float(rv)
        if rv_f:
            years.append(yr); revs.append(rv_f / 1e6 if rv_f > 10000 else rv_f)
            ebitdas.append((_safe_float(eb) or 0) / 1e6 if _safe_float(eb) and _safe_float(eb) > 10000 else _safe_float(eb))
            fcfs.append(None); nets.append(None)

    if not years: return None
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    bar_colors = ['rgba(0,217,126,.6)' if not y.endswith('E') else 'rgba(0,217,126,.25)' for y in years]
    fig.add_trace(go.Bar(x=years, y=revs, name='Revenue ($B)',
        marker_color=bar_colors, marker_line_color='#00d97e', marker_line_width=0.5,
        hovertemplate='%{x}: $%{y:.2f}B<extra>Revenue</extra>'), secondary_y=False)
    eb_x = [y for y,v in zip(years,ebitdas) if v is not None]
    eb_y = [v for v in ebitdas if v is not None]
    if eb_x:
        fig.add_trace(go.Scatter(x=eb_x, y=eb_y, name='EBITDA ($B)',
            mode='lines+markers', line=dict(color='#f5a623', width=2),
            marker=dict(size=5, color='#f5a623'),
            hovertemplate='%{x}: $%{y:.2f}B<extra>EBITDA</extra>'), secondary_y=True)
    fcf_x = [y for y,v in zip(years,fcfs) if v is not None]
    fcf_y = [v for v in fcfs if v is not None]
    if fcf_x:
        fig.add_trace(go.Scatter(x=fcf_x, y=fcf_y, name='FCF ($B)',
            mode='lines+markers', line=dict(color='#22d3ee', width=2, dash='dot'),
            marker=dict(size=5, color='#22d3ee'),
            hovertemplate='%{x}: $%{y:.2f}B<extra>FCF</extra>'), secondary_y=True)
    _theme(fig, f'Revenue · EBITDA · FCF — {ticker}  (actual + projected)', h=300)
    fig.update_yaxes(title_text='Revenue ($B)', title_font=dict(size=8, color='#00d97e'),
                     secondary_y=False, **_GRID)
    fig.update_yaxes(title_text='EBITDA / FCF ($B)', title_font=dict(size=8, color='#f5a623'),
                     secondary_y=True, showgrid=False, **_GRID)
    return fig

def chart_eps(ticker, fin, s_data):
    """EPS history + estimates."""
    inc = fin.get('income') or []
    if not inc:
        # Fall back to Excel data
        items = [
            ('3Y Ago', s_data.get('eps_3y_ago')),
            ('Last Yr', s_data.get('eps_ly')),
            ('TTM', s_data.get('eps_ttm')),
        ]
    else:
        items = [(d['date'], d.get('eps') or d.get('eps_diluted')) for d in sorted(inc, key=lambda x: x.get('date',''))]

    # Append estimates
    for yr, v in [('2026E', s_data.get('eps_2026e')), ('2027E', s_data.get('eps_2027e')), ('2028E', s_data.get('eps_2028e'))]:
        if _safe_float(v): items.append((yr, v))

    clean = [(str(yr), float(v)) for yr, v in items if _safe_float(v) is not None]
    if not clean: return None
    xs = [p for p,_ in clean]; ys = [v for _,v in clean]
    is_proj = [x.endswith('E') for x in xs]
    colors = ['rgba(0,217,126,.65)' if not ip and v>=0 else 'rgba(0,217,126,.3)' if ip and v>=0 else 'rgba(240,68,68,.65)' for ip, v in zip(is_proj, ys)]
    fig = go.Figure(go.Bar(
        x=xs, y=ys, marker_color=colors,
        marker_line_color=['#00d97e' if v>=0 else '#f04444' for v in ys],
        marker_line_width=0.5,
        text=[f"${v:.2f}" for v in ys], textposition='outside',
        textfont=dict(size=9, color='#5a6480'),
        hovertemplate='%{x}: $%{y:.2f}<extra>EPS</extra>'
    ))
    _theme(fig, f'EPS — Actual & Estimates — {ticker}', h=240)
    return fig

def chart_earnings_beats(earnings):
    """EPS beats/misses chart from FMP earnings surprises."""
    if not earnings: return None
    dates = [e['date'] for e in reversed(earnings)]
    actuals = [e.get('actual') or 0 for e in reversed(earnings)]
    estimates = [e.get('estimate') or 0 for e in reversed(earnings)]
    surprises = [e.get('surprise') or 0 for e in reversed(earnings)]
    s_colors = ['rgba(0,217,126,.7)' if v >= 0 else 'rgba(240,68,68,.7)' for v in surprises]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.6, 0.4], vertical_spacing=0.05,
                        subplot_titles=['EPS: Actual vs Estimate', 'Surprise ($)'])
    fig.add_trace(go.Bar(x=dates, y=estimates, name='Estimate',
        marker_color='rgba(90,100,128,.4)', hovertemplate='%{x}<br>Est: $%{y:.2f}<extra></extra>'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=actuals, name='Actual',
        mode='markers+lines', marker=dict(color=['#00d97e' if e['beat'] else '#f04444' for e in reversed(earnings)], size=8),
        line=dict(color='#22d3ee', width=1),
        hovertemplate='%{x}<br>Actual: $%{y:.2f}<extra></extra>'), row=1, col=1)
    fig.add_trace(go.Bar(x=dates, y=surprises, name='Surprise',
        marker_color=s_colors, showlegend=False,
        hovertemplate='%{x}<br>Surprise: $%{y:.3f}<extra></extra>'), row=2, col=1)
    _theme(fig, 'Earnings Beats & Misses', h=320)
    return fig

def chart_valuation(ticker, s_data, metrics):
    """Valuation multiples: current vs history from Excel."""
    periods = ['3Y Ago', 'TTM', '2025E', '2026E']
    gaps = [_safe_float(s_data.get(k)) for k in ['gaps_3y_cagr','gaps_ttm','gaps_2025','gaps_2026']]
    gape = [_safe_float(s_data.get(k)) for k in ['gape_3y_cagr','gape_ttm','gape_2025','gape_2026']]
    if not any(v is not None for v in gaps+gape): return None
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if any(v is not None for v in gaps):
        fig.add_trace(go.Bar(x=periods, y=gaps, name='P/S (GAPS)',
            marker_color='rgba(34,211,238,.45)', marker_line_color='#22d3ee', marker_line_width=0.5,
            hovertemplate='%{x}: %{y:.1f}x<extra>P/S</extra>'), secondary_y=False)
    if any(v is not None for v in gape):
        fig.add_trace(go.Scatter(x=periods, y=gape, name='P/E (GAPE)',
            mode='lines+markers', line=dict(color='#f5a623', width=2),
            marker=dict(size=6, color='#f5a623'),
            hovertemplate='%{x}: %{y:.1f}x<extra>P/E</extra>'), secondary_y=True)
    # FMP live metrics as reference lines
    if metrics:
        lps = _safe_float(metrics.get('ps'))
        lpe = _safe_float(metrics.get('pe'))
        if lps: fig.add_hline(y=lps, line=dict(color='rgba(34,211,238,.25)', dash='dot', width=1), secondary_y=False)
        if lpe: fig.add_hline(y=lpe, line=dict(color='rgba(245,166,35,.25)', dash='dot', width=1), secondary_y=True)
    _theme(fig, f'P/S & P/E History + Projections — {ticker}', h=250)
    fig.update_yaxes(title_text='P/S', title_font=dict(size=8, color='#22d3ee'), secondary_y=False, **_GRID)
    fig.update_yaxes(title_text='P/E', title_font=dict(size=8, color='#f5a623'), secondary_y=True, showgrid=False, **_GRID)
    return fig

def chart_fcf_netdebt(ticker, fin, s_data):
    """FCF & Net Debt trend."""
    cf = fin.get('cashflow') or []
    bal = fin.get('balance') or []
    bal_map = {d['date']: d for d in bal}

    years_live = [d['date'] for d in cf]
    fcf_live  = [(d.get('fcf') or 0)/1e9 for d in cf]
    nd_live   = [(bal_map.get(d['date'],{}).get('net_debt') or 0)/1e9 for d in cf]

    # Fallback to Excel
    if not years_live:
        years_live = ['Year -3','Year -2','Year -1','TTM']
        fcf_live = [_safe_float(s_data.get(k)) or 0 for k in ['fcf_y3','fcf_y2','fcf_y1','fcf_ttm']]
        nd_live  = [(_safe_float(s_data.get(k)) or 0)/1e6 for k in ['net_debt_y3','net_debt_y2','net_debt_y1','net_debt_ttm']]

    if not years_live: return None
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fcl = ['rgba(0,217,126,.65)' if v >= 0 else 'rgba(240,68,68,.65)' for v in fcf_live]
    fig.add_trace(go.Bar(x=years_live, y=fcf_live, name='FCF ($B)',
        marker_color=fcl, marker_line_color=['#00d97e' if v>=0 else '#f04444' for v in fcf_live],
        marker_line_width=0.5, hovertemplate='%{x}: $%{y:.2f}B<extra>FCF</extra>'), secondary_y=False)
    ndl = ['rgba(240,68,68,.5)' if v>=0 else 'rgba(0,217,126,.5)' for v in nd_live]
    fig.add_trace(go.Bar(x=years_live, y=nd_live, name='Net Debt ($B)',
        marker_color=ndl, hovertemplate='%{x}: $%{y:.2f}B<extra>Net Debt</extra>'), secondary_y=True)
    _theme(fig, f'Free Cash Flow & Net Debt — {ticker}', h=260)
    fig.update_layout(barmode='group')
    fig.update_yaxes(title_text='FCF ($B)', title_font=dict(size=8, color='#00d97e'), secondary_y=False, **_GRID)
    fig.update_yaxes(title_text='Net Debt ($B)', title_font=dict(size=8, color='#f04444'), secondary_y=True, showgrid=False, **_GRID)
    return fig

def chart_universe_map(stocks):
    rows = []
    for s in stocks:
        pe = _safe_float(s.get('pe')); rg = _safe_float(s.get('rev_growth_ly'))
        mc = _safe_float(s.get('mcap_b')); rec = str(s.get('recommendation','')).strip()
        if pe and rg is not None and 0 < pe < 350:
            rows.append({'Ticker': s['ticker'], 'PE': pe,
                         'Rev Growth%': rg*100, 'MCap ($B)': mc or 10,
                         'Rec': rec, 'Sector': SECTORS.get(s['ticker'],'Other'),
                         'Name': s['name'][:25]})
    if not rows: return None
    df = pd.DataFrame(rows)
    cmap = {'Buy':'#00d97e','Strong Buy':'#00d97e','Accumulate':'#22d3ee',
            'Hold':'#4f8ef7','Watch':'#f5a623','Sell':'#f04444','':'#5a6480'}
    fig = px.scatter(df, x='Rev Growth%', y='PE', text='Ticker', size='MCap ($B)',
                     color='Rec', color_discrete_map=cmap, size_max=50,
                     hover_data={'Name':True,'Sector':True,'PE':':.1f','MCap ($B)':':.0f'})
    fig.update_traces(textposition='top center', textfont=dict(size=8, color='#5a6480'))
    _theme(fig, '78-Stock Universe — PE vs Revenue Growth  (bubble = Market Cap)', h=520)
    fig.update_xaxes(title_text='Revenue Growth % (Last Year)', title_font=dict(size=9, color='#5a6480'), **_GRID)
    fig.update_yaxes(title_text='PE Multiple (TTM)', title_font=dict(size=9, color='#5a6480'), **_GRID)
    fig.add_hline(y=30, line=dict(color='rgba(255,255,255,.04)', dash='dot', width=1))
    fig.add_vline(x=20, line=dict(color='rgba(255,255,255,.04)', dash='dot', width=1))
    return fig

# ═════════════════════════════════════════════════════════════════
#  AI ENGINE
# ═════════════════════════════════════════════════════════════════

def ai_analyze(model, ticker, s_data, quote, fin):
    if not model: return None
    key = f"ai_{ticker}"
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    # Build rich context from live + Excel data
    price = (quote or {}).get('price') or s_data.get('price')
    mktcap = fm((quote or {}).get('market_cap') or (s_data.get('mcap_b') or 0)*1e9)
    inc = (fin.get('income') or [{}])
    lat_inc = inc[-1] if inc else {}
    cf = (fin.get('cashflow') or [{}])
    lat_cf = cf[-1] if cf else {}
    metrics = fin.get('metrics') or {}
    earnings = fin.get('earnings') or []
    beat_rate = f"{sum(1 for e in earnings if e.get('beat'))/len(earnings)*100:.0f}%" if earnings else 'N/A'

    def sp(v, mul=True):
        f = _safe_float(v)
        if f is None: return 'N/A'
        return f"{f*(100 if mul else 1):.1f}%"

    prompt = f"""You are a Citadel Global Equities senior portfolio analyst.
Conduct institutional-grade research on {ticker} ({s_data['name']}).

LIVE MARKET DATA (source: {(quote or {}).get('source','Excel')}):
Price: ${price:.2f} | Market Cap: {mktcap} | Sector: {SECTORS.get(ticker,'Unknown')}
52W High: ${(quote or {}).get('year_high','N/A')} | 52W Low: ${(quote or {}).get('year_low','N/A')}
PE: {(quote or {}).get('pe') or s_data.get('pe','N/A')} | P/S: {metrics.get('ps') or s_data.get('ps','N/A')}
EV/EBITDA: {metrics.get('ev_ebitda','N/A')} | P/B: {metrics.get('pb','N/A')}
ROE: {sp(metrics.get('roe'), mul=False)} | Current Ratio: {metrics.get('current_ratio','N/A')}
FCF Yield: {sp(metrics.get('fcf_yield'), mul=False)}

FINANCIAL DATA (source: {fin.get('income_src','Excel')}):
Revenue LY: {fm(lat_inc.get('revenue') or (s_data.get('rev_ly') or 0)*1e6)}
Revenue Growth LY: {sp(s_data.get('rev_growth_ly'))} | 3Y CAGR: {sp(s_data.get('rev_3y_cagr'))}
EBITDA LY: {fm(lat_inc.get('ebitda') or (s_data.get('ebitda_ly') or 0)*1e6)}
EBITDA 3Y CAGR: {sp(s_data.get('ebitda_3y_cagr'))}
Net Income LY: {fm(lat_inc.get('net_income'))}
Free Cash Flow: {fm(lat_cf.get('fcf') or (s_data.get('fcf_ttm') or 0)*1e6)}
Net Debt TTM: {fm((s_data.get('net_debt_ttm') or 0)*1e6)}
EPS LY: ${s_data.get('eps_ly','N/A')} | EPS 3Y CAGR: {sp(s_data.get('eps_3y_cagr'))}

FORWARD ESTIMATES (from Pyk-Inv-List):
Revenue 2026E: {fm((s_data.get('rev_2026e') or 0)*1e6)} (+{sp(s_data.get('rev_growth_2026'))})
Revenue 2027E: {fm((s_data.get('rev_2027e') or 0)*1e6)} | 2028E: {fm((s_data.get('rev_2028e') or 0)*1e6)}
EPS 2026E: ${s_data.get('eps_2026e','N/A')} | 2027E: ${s_data.get('eps_2027e','N/A')}
EBITDA 2026E: {fm((s_data.get('ebitda_2026e') or 0)*1e6)} | 2027E: {fm((s_data.get('ebitda_2027e') or 0)*1e6)}
Guidance CAGR: {sp(s_data.get('guidance_cagr'))}

QUALITY SIGNALS:
EPS Beat Rate (last 8Q): {beat_rate}
Price Follows: {s_data.get('price_follows','N/A')} | Pykupz Score: {s_data.get('points','N/A')}/10
Hypothesis Price: {s_data.get('hypothesis_price','N/A')}
Rec from Pyk-Inv-List: {s_data.get('recommendation','N/A')}

Return ONLY valid JSON, no markdown, no backticks:
{{"thesis":"2-3 sentence institutional thesis","moat_summary":"1 sentence","moat_layers":[{{"layer":"name","stars":1-5,"verdict":"UNASSAILABLE|FORTRESS|STRUCTURAL|BUILDING|NARROW","detail":"1 line"}}],"why_now":"Why buy/watch at this exact price and time","bull_case":["pt1","pt2","pt3"],"bear_case":["risk1","risk2","risk3"],"signal":"STRONG BUY|BUY|ACCUMULATE|HOLD|WATCH|REDUCE|SELL","conviction":1-5,"risk_score":0-100,"antigravity_score":0-100,"antigravity_reason":"1 line","entry_price":"$X.XX","target_3y":"$X","return_3y":"+X%","pa":"+X% p.a.","scenarios":{{"bear":{{"price":0.0,"return":"-X%","trigger":"brief"}},"base":{{"price":0.0,"return":"+X%","trigger":"brief"}},"bull":{{"price":0.0,"return":"+X%","trigger":"brief"}}}},"catalysts":[{{"horizon":"NEAR|MID|LONG","text":"catalyst","timing":"Q1 2026 etc","impact":"HIGH|MEDIUM|LOW|CONFIRMED"}}],"risks":[{{"sev":"🔴|🟡|🟢","risk":"name","prob":"HIGH|LOW","imp":"HIGH|LOW","detail":"1 line"}}],"exit_trigger":"1 line","key_edge":"1-2 sentences","watch_item":"main Q1 2026 watch","grade":"A+|A|A-|B+|B|B-|C|D|F","verdict":"1 sentence"}}"""

    try:
        import google.generativeai as genai
        r = model.generate_content(prompt)
        text = re.sub(r'```(?:json)?', '', r.text).strip().strip('`')
        result = json.loads(text)
        result['_sources'] = {'quote': (quote or {}).get('source','Excel'), 'fin': fin.get('income_src','Excel')}
        st.session_state.ai_cache[key] = result
        return result
    except Exception as e:
        return {"error": str(e), "_raw": getattr(e, '__traceback__', None)}

def ai_chat(model, q, ctx):
    if not model: return "⚠️  Add Gemini API key in the sidebar to use AI chat."
    try:
        import google.generativeai as genai
        sys_prompt = f"You are PYKUPZ AI — elite hedge fund analyst. 78-stock universe, Q1 2026. Context: {ctx[:500]}. Be concise, data-driven, terminal-style. Max 250 words."
        msgs = [{"role":"user","parts":[sys_prompt]}]
        for h in st.session_state.chat_hist[-6:]:
            msgs.append({"role":h["role"],"parts":[h["content"]]})
        msgs.append({"role":"user","parts":[q]})
        r = model.generate_content(msgs)
        return r.text
    except Exception as e:
        return f"⚠️  Error: {e}"

# ═════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:14px 14px 10px;border-bottom:1px solid #1c2030">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:14px;font-weight:700;letter-spacing:3px;color:#00d97e">⚡ PYKUPZ</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#2a3040;margin-top:2px">INSTITUTIONAL TERMINAL · Q1 2026</div>
        </div>""", unsafe_allow_html=True)

        # ── API Keys ──
        st.markdown('<div style="padding:10px 14px 4px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#2a3040">DATA SOURCES</div></div>', unsafe_allow_html=True)

        fkey = st.text_input("##fmp",
            value=st.session_state.fkey, type="password",
            placeholder="FMP key (financialmodelinprep.com — free)",
            label_visibility="collapsed",
            help="FREE key at financialmodelinprep.com → My Account → API Key")
        if fkey != st.session_state.fkey:
            st.session_state.fkey = fkey
            st.cache_resource.clear()

        gkey = st.text_input("##gem",
            value=st.session_state.gkey, type="password",
            placeholder="Gemini key (aistudio.google.com — free)",
            label_visibility="collapsed",
            help="FREE key at aistudio.google.com")
        if gkey != st.session_state.gkey:
            st.session_state.gkey = gkey
            st.session_state.ai_cache = {}
            st.cache_resource.clear()

        # Status indicators
        eng = engine()
        ds  = eng.data_status()
        html = ""
        for src, (status, clr) in ds.items():
            label = {'fmp':'FMP','yf':'yfinance','excel':'Excel','gemini':'Gemini'}.get(src,src)
            html += f'<div style="display:flex;justify-content:space-between;padding:3px 0;font-family:IBM Plex Mono,monospace;font-size:9px"><span style="color:#2a3040">{label.upper()}</span><span style="color:{clr}">{status}</span></div>'
        st.markdown(f'<div style="padding:4px 14px 10px;border-bottom:1px solid #0c0e14">{html}</div>', unsafe_allow_html=True)

        # ── Navigation ──
        st.markdown('<div style="padding:8px 14px 4px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#2a3040">NAVIGATION</div></div>', unsafe_allow_html=True)
        nav_items = [('📊  Portfolio Overview', 'portfolio'),('🚀  AI Scanner', 'scanner'),('💬  AI Chat', 'chat')]
        for lbl, view in nav_items:
            if st.button(lbl, key=f"nav_{view}", use_container_width=True):
                st.session_state.main_view = view
                st.rerun()

        # ── Stock universe ──
        st.markdown('<div style="padding:8px 14px 4px;border-top:1px solid #0c0e14"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#2a3040">UNIVERSE · 78 STOCKS</div></div>', unsafe_allow_html=True)
        srch = st.text_input("##srch", placeholder="Search ticker or name...", label_visibility="collapsed")
        rf = st.selectbox("##rf", ["All","Buy","Watch","Hold","Sell"], label_visibility="collapsed")

        filtered = ALL_STOCKS
        if srch:
            s2 = srch.upper()
            filtered = [x for x in filtered if s2 in x['ticker'].upper() or s2 in x['name'].upper()]
        if rf != "All":
            filtered = [x for x in filtered if rf.lower() in str(x.get('recommendation','')).lower()]

        st.markdown(f'<div style="padding:0 14px 2px;font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040">{len(filtered)} stocks</div>', unsafe_allow_html=True)

        for s in filtered:
            t = s['ticker']
            pts = _safe_float(s.get('points') or s.get('reconcile'))
            score_txt = f"  ·  {pts:.0f}pts" if pts else ""
            lbl = f"**{t}**  ·  {s['name'][:18]}{score_txt}"
            if st.button(lbl, key=f"sb_{t}", use_container_width=True):
                st.session_state.ticker = t
                st.session_state.main_view = 'stock'
                st.rerun()

        st.markdown(f'<div style="padding:8px 14px;border-top:1px solid #0c0e14;font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040">AI cache: {len(st.session_state.ai_cache)} · {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
#  STOCK TEAR SHEET
# ═════════════════════════════════════════════════════════════════

def render_stock(ticker):
    s = next((x for x in ALL_STOCKS if x['ticker']==ticker), None)
    if not s:
        st.error(f"Stock {ticker} not found in universe."); return

    eng = engine()
    model = ai_model()

    # ── Fetch live data ──────────────────────────────────────────
    with st.spinner(f"⚡  Loading live data for {ticker}..."):
        quote, q_src = eng.get_quote(ticker, s)
        price = quote.get('price') or _safe_float(s.get('price')) or 0
        chg   = quote.get('pct_change') or 0
        fin   = eng.get_financials(ticker)
        metrics = fin.get('metrics') or {}

    # ── AI analysis ──────────────────────────────────────────────
    ai = None
    if model:
        key = f"ai_{ticker}"
        if key not in st.session_state.ai_cache:
            with st.spinner(f"🤖  Gemini analysing {ticker}..."):
                ai = ai_analyze(model, ticker, s, quote, fin)
        else:
            ai = st.session_state.ai_cache[key]

    # ── Stock header ─────────────────────────────────────────────
    clr  = '#00d97e' if chg >= 0 else '#f04444'
    arr  = '▲' if chg >= 0 else '▼'
    rec  = str(s.get('recommendation','')).strip()
    ath_r = _safe_float(s.get('ath_retrace'))
    ath_txt = f"{ath_r*100:.1f}% from ATH" if ath_r else ""
    yr_h = _safe_float(quote.get('year_high') or s.get('high'))
    yr_l = _safe_float(quote.get('year_low'))
    vol  = quote.get('volume')
    mktcap = quote.get('market_cap') or (_safe_float(s.get('mcap_b')) or 0) * 1e9

    st.markdown(f"""
    <div class="pyk-header">
      <div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{clr};letter-spacing:2px">{ticker}</span>
          <span style="font-family:'IBM Plex Sans',sans-serif;font-size:13px;color:#5a6480">{s['name']}</span>
          <span style="background:#11141b;border:1px solid #1c2030;border-radius:2px;padding:1px 7px;font-family:IBM Plex Mono,monospace;font-size:9px;color:#5a6480">{SECTORS.get(ticker,'—')}</span>
          {f'<span class="sig {SIG_CSS_MAP.get(rec,SIG_CSS_MAP.get(rec.upper(),"sig-w"))}">{rec.upper()}</span>' if rec else ''}
          <span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040">src: {q_src}</span>
        </div>
        <div style="display:flex;align-items:baseline;gap:14px;margin-top:6px;flex-wrap:wrap">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:24px;font-weight:600;color:#eef2ff">${price:,.2f}</span>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:{clr}">{arr} {abs(chg*100):.2f}%</span>
          {f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#2a3040">{ath_txt}</span>' if ath_txt else ''}
          {f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#2a3040">52W: ${yr_l:.0f} – ${yr_h:.0f}</span>' if yr_h and yr_l else ''}
          {f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#2a3040">Vol: {vol:,.0f}</span>' if vol else ''}
        </div>
      </div>
      <div style="text-align:right">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:#eef2ff">{_safe_float(s.get('points')) and f"{_safe_float(s.get('points')):.0f}" or "—"}<span style="font-size:10px;color:#2a3040">/10</span></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#2a3040">PYKUPZ SCORE</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#2a3040;margin-top:4px">{datetime.now().strftime('%H:%M:%S UTC')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI strip ────────────────────────────────────────────────
    live_pe  = _safe_float(quote.get('pe')) or _safe_float(metrics.get('pe')) or _safe_float(s.get('pe'))
    live_ps  = _safe_float(metrics.get('ps')) or _safe_float(s.get('ps'))
    live_mc  = fm(mktcap)
    rg_ly    = _safe_float(s.get('rev_growth_ly'))
    fcf_ttm  = _safe_float(s.get('fcf_ttm'))

    kpis = [
        (fv(live_pe), 'PE TTM', 'a'),
        (fv(live_ps), 'P/S', ''),
        (live_mc, 'Market Cap', 'b'),
        (fp(rg_ly), 'Rev Grw LY', 'g' if (rg_ly or 0)>0.15 else ''),
        (fp(s.get('rev_3y_cagr')), 'Rev 3Y CAGR', 'g'),
        (fp(s.get('eps_3y_cagr')), 'EPS 3Y CAGR', 'g'),
        (fm((fcf_ttm or 0)*1e6) if fcf_ttm else '—', 'FCF TTM', 'g' if (fcf_ttm or 0)>0 else 'r'),
        (fn(s.get('eps_2026e'), pre='$', suf='', dec=2), 'EPS 2026E', 'c'),
    ]
    cols = st.columns(8)
    for col, (val, lbl, acc) in zip(cols, kpis):
        col.markdown(kpi(val, lbl, acc, 15), unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────
    tabs = st.tabs(["📋  Overview","📐  Valuation","📈  Growth","💰  Earnings",
                    "🏰  Moat","🎯  Scenarios","⚠️  Risk","💼  Decision","📉  Charts"])

    # ── OVERVIEW ─────────────────────────────────────────────────
    with tabs[0]:
        if ai and 'error' not in ai:
            sig = ai.get('signal','—'); sig_clr = SIG_CLR.get(sig,'#f5a623')
            col_l, col_r = st.columns([2,1])
            with col_l:
                sources_txt = f"FMP: {ai.get('_sources',{}).get('quote','—')} · Financials: {ai.get('_sources',{}).get('fin','—')}"
                st.markdown(f"""
                <div class="ai-p">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                    <span class="ai-badge">GEMINI · INSTITUTIONAL ANALYSIS</span>
                    <span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040">{sources_txt}</span>
                  </div>
                  <div style="font-family:'IBM Plex Sans',sans-serif;font-size:12px;line-height:1.75;color:#b8c4d8;margin-bottom:10px">{ai.get('thesis','—')}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#f5a623;margin-bottom:10px">{ai.get('why_now','')}</div>
                  <div style="padding:8px 12px;background:#080a0f;border-left:2px solid #4f8ef7;border-radius:0 2px 2px 0">
                    <div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;letter-spacing:2px;margin-bottom:3px">MOAT IN ONE LINE</div>
                    <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#4f8ef7;font-style:italic">"{ai.get('moat_summary','—')}"</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                with b1:
                    st.markdown(sh('🟢  Bull Case','g'), unsafe_allow_html=True)
                    for pt in ai.get('bull_case',[]):
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;padding:4px 0;border-bottom:1px solid #0c0e14;color:#5a6480">✦ {pt}</div>', unsafe_allow_html=True)
                with b2:
                    st.markdown(sh('🔴  Bear Case'), unsafe_allow_html=True)
                    for pt in ai.get('bear_case',[]):
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;padding:4px 0;border-bottom:1px solid #0c0e14;color:#5a6480">⚑ {pt}</div>', unsafe_allow_html=True)

                for section, icon, bc in [('key_edge','⚡ KEY EDGE','#00d97e'),('watch_item','👁  WATCH ITEM','#f5a623'),('verdict','📌  VERDICT','#4f8ef7')]:
                    txt = ai.get(section,'')
                    if txt:
                        st.markdown(f'<div style="background:#080a0f;border:1px solid {bc}22;border-left:2px solid {bc};border-radius:3px;padding:10px 14px;margin-top:5px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:{bc};margin-bottom:4px">{icon}</div><div style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#5a6480;line-height:1.6">{txt}</div></div>', unsafe_allow_html=True)

            with col_r:
                conv = int(ai.get('conviction',3)); grade = ai.get('grade','—')
                risk = ai.get('risk_score',50); ag = ai.get('antigravity_score',50)
                ag_c = '#00d97e' if ag>=70 else '#f5a623' if ag>=40 else '#f04444'
                st.markdown(f"""
                <div class="kpi" style="text-align:center;border-color:{sig_clr}33;border-top:2px solid {sig_clr};padding:16px">
                  <div class="kpi-l">AI SIGNAL</div>
                  <div style="font-family:'IBM Plex Sans',sans-serif;font-size:16px;font-weight:700;color:{sig_clr};margin:5px 0">{sig}</div>
                  <div class="kpi-l" style="margin-top:10px">GRADE</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:32px;font-weight:700;color:#22d3ee;line-height:1">{grade}</div>
                  <div class="kpi-l" style="margin-top:10px">CONVICTION</div>
                  <div style="color:#f5a623;font-size:14px;letter-spacing:2px">{"★"*conv}{"☆"*(5-conv)}</div>
                  <div class="kpi-l" style="margin-top:10px">RISK SCORE</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;color:#f04444">{risk}<span style="font-size:10px;color:#2a3040">/100</span></div>
                  <div class="kpi-l" style="margin-top:10px">ANTIGRAVITY</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:24px;color:{ag_c};font-weight:700">{ag}<span style="font-size:10px;color:#2a3040">/100</span></div>
                  <div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;margin-top:3px;line-height:1.4">{ai.get('antigravity_reason','')[:80]}</div>
                </div>
                <div class="kpi" style="margin-top:6px">
                  <div class="kpi-l">3Y BASE TARGET</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:700;color:#00d97e">{ai.get('target_3y','—')}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#00d97e">{ai.get('return_3y','—')}  ·  {ai.get('pa','—')}</div>
                  <div class="kpi-l" style="margin-top:6px">ENTRY PRICE</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:#b8c4d8">{ai.get('entry_price','—')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            # No AI — show raw data
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(sh('📋  Portfolio Data (Pyk-Inv-List)'), unsafe_allow_html=True)
                rows = [
                    ('Price (Excel)', fn(s.get('price'), suf='', dec=2)),
                    ('ATH', fn(s.get('high'), suf='', dec=2)),
                    ('ATH Retrace', fp(s.get('ath_retrace'))),
                    ('PE', fv(s.get('pe'))), ('P/S', fv(s.get('ps'))),
                    ('MCap Category', s.get('mcap_cat','—')),
                    ('Price Follows', s.get('price_follows','—')),
                    ('Score /10', fn(s.get('points'), pre='', suf='', dec=1)),
                    ('Recommendation', str(s.get('recommendation','—'))),
                ]
                st.markdown(''.join(dr(k,v) for k,v in rows), unsafe_allow_html=True)
            with c2:
                st.markdown(sh('📊  Growth Metrics'), unsafe_allow_html=True)
                rows2 = [
                    ('Rev LY', fm((s.get('rev_ly') or 0)*1e6)),
                    ('Rev Growth LY', fp(s.get('rev_growth_ly'))),
                    ('Rev 3Y CAGR', fp(s.get('rev_3y_cagr'))),
                    ('Rev 2026E', fm((s.get('rev_2026e') or 0)*1e6)),
                    ('EBITDA LY', fm((s.get('ebitda_ly') or 0)*1e6)),
                    ('EBITDA 3Y CAGR', fp(s.get('ebitda_3y_cagr'))),
                    ('EPS LY', fn(s.get('eps_ly'), pre='$', suf='', dec=2)),
                    ('EPS 2026E', fn(s.get('eps_2026e'), pre='$', suf='', dec=2)),
                    ('FCF TTM', fm((s.get('fcf_ttm') or 0)*1e6)),
                ]
                st.markdown(''.join(dr(k,v) for k,v in rows2), unsafe_allow_html=True)
            st.info("💡  Enter **FMP API key** (free at financialmodelingrep.com) for live data + **Gemini key** for AI thesis, moat, scenarios, risk & decision.")

    # ── VALUATION ────────────────────────────────────────────────
    with tabs[1]:
        c1, c2 = st.columns([1,2])
        with c1:
            st.markdown(sh('📐  Valuation Dashboard'), unsafe_allow_html=True)
            fpe_v = _safe_float(metrics.get('pe'))  # FMP live PE
            items = [
                ('PE (Live, FMP)', fv(fpe_v) if fpe_v else fv(s.get('pe')), '#f5a623' if fpe_v else None),
                ('P/S (Live, FMP)', fv(metrics.get('ps')) if metrics.get('ps') else fv(s.get('ps')), '#22d3ee'),
                ('EV/EBITDA', fv(metrics.get('ev_ebitda')), None),
                ('P/B', fv(metrics.get('pb')), None),
                ('PEG Ratio', fv(metrics.get('peg')), None),
                ('ROE', fp(metrics.get('roe'), mul=False), '#00d97e' if (metrics.get('roe') or 0)>0.15 else None),
                ('FCF Yield', fp(metrics.get('fcf_yield'), mul=False), '#00d97e'),
                ('Market Cap', fm(mktcap), '#4f8ef7'),
                ('52W High', fn(yr_h, suf='', dec=2) if yr_h else '—', None),
                ('52W Low', fn(yr_l, suf='', dec=2) if yr_l else '—', None),
                ('ATH Retrace', fp(s.get('ath_retrace')), '#f04444' if (s.get('ath_retrace') or 0)<-0.2 else None),
                ('GAPS (P/S model)', fv(s.get('gaps')), '#22d3ee'),
                ('GAPE (P/E model)', fv(s.get('gape')), '#f5a623'),
                ('Score /10', fn(s.get('points'), pre='', suf='', dec=1), '#00d97e'),
                ('Hypothesis Price', str(s.get('hypothesis_price','—') or '—'), '#00d97e'),
            ]
            st.markdown(''.join(dr(k,v,vc) for k,v,vc in items), unsafe_allow_html=True)
            if metrics.get('pe') or metrics.get('ps'):
                st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#4f8ef7;margin-top:6px">● Live ratios sourced from FMP</div>', unsafe_allow_html=True)
        with c2:
            fv2 = chart_valuation(ticker, s, metrics)
            if fv2: st.plotly_chart(fv2, use_container_width=True)
            # Current multiples bar
            mult_vals = [(k,v) for k,v in [
                ('PE (TTM)', _safe_float(fpe_v or s.get('pe'))),
                ('P/S', _safe_float(metrics.get('ps') or s.get('ps'))),
                ('EV/EBITDA', _safe_float(metrics.get('ev_ebitda'))),
                ('P/B', _safe_float(metrics.get('pb'))),
            ] if v and 0<v<500]
            if mult_vals:
                clrs = ['#f5a623','#22d3ee','#4f8ef7','#a78bfa']
                fig_m = go.Figure(go.Bar(
                    x=[k for k,_ in mult_vals], y=[v for _,v in mult_vals],
                    marker_color=clrs[:len(mult_vals)], marker_line_width=0,
                    text=[f"{v:.1f}x" for _,v in mult_vals], textposition='outside',
                    textfont=dict(size=9, color='#5a6480')
                ))
                _theme(fig_m, f'Current Valuation Multiples — {ticker}  (FMP + Excel)', h=220)
                st.plotly_chart(fig_m, use_container_width=True)

    # ── GROWTH ───────────────────────────────────────────────────
    with tabs[2]:
        grow_kpis = [
            (fp(s.get('rev_growth_ly')), 'Rev Grw LY', 'g' if (s.get('rev_growth_ly') or 0)>0.2 else ''),
            (fp(s.get('rev_3y_cagr')), 'Rev 3Y CAGR', 'g'),
            (fm((s.get('rev_2026e') or 0)*1e6), 'Rev 2026E', 'c'),
            (fp(s.get('ebitda_3y_cagr')), 'EBITDA 3Y CAGR', 'a'),
            (fp(s.get('eps_3y_cagr')), 'EPS 3Y CAGR', 'g'),
            (fn(s.get('eps_2026e'), pre='$', suf='', dec=2), 'EPS 2026E', 'c'),
            (fm((s.get('fcf_ttm') or 0)*1e6), 'FCF TTM', 'g' if (s.get('fcf_ttm') or 0)>0 else 'r'),
            (fp(s.get('guidance_cagr')), 'Guidance CAGR', 'g'),
        ]
        cols = st.columns(8)
        for col, (val, lbl, acc) in zip(cols, grow_kpis):
            col.markdown(kpi(val, lbl, acc, 14), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig_rv = chart_revenue(ticker, fin)
            if fig_rv: st.plotly_chart(fig_rv, use_container_width=True)
        with c2:
            fig_ep = chart_eps(ticker, fin, s)
            if fig_ep: st.plotly_chart(fig_ep, use_container_width=True)
        fig_fd = chart_fcf_netdebt(ticker, fin, s)
        if fig_fd: st.plotly_chart(fig_fd, use_container_width=True)

        # Score breakdown
        st.markdown(sh('🎯  Pykupz Score Breakdown'), unsafe_allow_html=True)
        sc_items = [('Rev Growth',s.get('rev_score'),'g'),('EPS',s.get('eps_score'),'g'),
                    ('EBITDA',s.get('ebitda_score'),'a'),('Cashflow',s.get('cashflow_score'),'c'),
                    ('Net Debt',s.get('net_debt_score'),'b'),('Factor Adj',s.get('factor_adj'),'p')]
        cols = st.columns(6)
        for col, (lbl,v,acc) in zip(cols, sc_items):
            vt = f"{_safe_float(v):.0f}/10" if _safe_float(v) is not None else '—'
            col.markdown(kpi(vt, lbl, acc, 15), unsafe_allow_html=True)

    # ── EARNINGS ─────────────────────────────────────────────────
    with tabs[3]:
        earnings = fin.get('earnings') or []
        if earnings:
            beat_ct = sum(1 for e in earnings if e.get('beat'))
            beat_rt = beat_ct / len(earnings) * 100
            c1, c2, c3 = st.columns(3)
            c1.markdown(kpi(f"{beat_rt:.0f}%", 'EPS Beat Rate', 'g' if beat_rt>=75 else 'a' if beat_rt>=50 else 'r', 22), unsafe_allow_html=True)
            c2.markdown(kpi(f"{beat_ct}/{len(earnings)}", 'Beats / Quarters', 'g', 22), unsafe_allow_html=True)
            last_s = earnings[0].get('surprise') if earnings else None
            c3.markdown(kpi(f"${last_s:.3f}" if last_s else '—', 'Last Surprise', 'g' if (last_s or 0)>=0 else 'r', 22), unsafe_allow_html=True)
            fig_eb = chart_earnings_beats(earnings)
            if fig_eb: st.plotly_chart(fig_eb, use_container_width=True)
            # Table
            st.markdown(sh('📋  Earnings History (FMP)'), unsafe_allow_html=True)
            df_e = pd.DataFrame([{
                'Date': e['date'], 'Actual EPS': f"${e.get('actual',0):.3f}",
                'Estimate EPS': f"${e.get('estimate',0):.3f}",
                'Surprise': f"${e.get('surprise',0):.3f}",
                'Beat': '✅' if e.get('beat') else '❌',
            } for e in earnings])
            st.dataframe(df_e, use_container_width=True, hide_index=True)
            st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#4f8ef7">● Earnings data sourced from Financial Modeling Prep (FMP)</div>', unsafe_allow_html=True)
        else:
            st.info("Earnings history available with FMP API key. Enter your free key in the sidebar.")
            # Show Excel estimates
            st.markdown(sh('📊  EPS Estimates (from Pyk-Inv-List)'), unsafe_allow_html=True)
            est_items = [
                ('EPS 3Y Ago', fn(s.get('eps_3y_ago'), pre='$', suf='', dec=2)),
                ('EPS Last Year', fn(s.get('eps_ly'), pre='$', suf='', dec=2)),
                ('EPS TTM', fn(s.get('eps_ttm'), pre='$', suf='', dec=2)),
                ('EPS 2026E', fn(s.get('eps_2026e'), pre='$', suf='', dec=2)),
                ('EPS 2027E', fn(s.get('eps_2027e'), pre='$', suf='', dec=2)),
                ('EPS 2028E', fn(s.get('eps_2028e'), pre='$', suf='', dec=2)),
                ('EPS 3Y CAGR', fp(s.get('eps_3y_cagr'))),
            ]
            st.markdown(''.join(dr(k,v) for k,v in est_items), unsafe_allow_html=True)

    # ── MOAT ─────────────────────────────────────────────────────
    with tabs[4]:
        if ai and 'error' not in ai and ai.get('moat_layers'):
            st.markdown(f'<div style="background:#080a0f;border:1px solid rgba(79,142,247,.25);border-radius:4px;padding:12px 16px;margin-bottom:12px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#4f8ef7;margin-bottom:5px">MOAT SUMMARY</div><div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4f8ef7;font-style:italic">"{ai.get("moat_summary","—")}"</div></div>', unsafe_allow_html=True)
            for m in ai.get('moat_layers',[]):
                n = int(m.get('stars',3)); v = m.get('verdict','—')
                vc = '#00d97e' if 'UNASS' in v else '#22d3ee' if 'FORT' in v else '#f5a623' if 'STRUCT' in v else '#5a6480'
                st.markdown(f'<div class="mc"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px"><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#b8c4d8;font-weight:600;flex:1">{m.get("layer","—")}</div><div style="color:#f5a623;font-size:12px;letter-spacing:2px;margin:0 10px">{"★"*n}{"☆"*(5-n)}</div><span style="background:{vc}18;border:1px solid {vc}44;color:{vc};font-family:IBM Plex Mono,monospace;font-size:8px;padding:1px 7px;border-radius:2px">{v}</span></div><div style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#2a3040;font-style:italic">{m.get("detail","")}</div></div>', unsafe_allow_html=True)
        else:
            st.info("🤖  Add Gemini key to generate moat architecture with ★★★★★ ratings per layer.")
            st.markdown(''.join(dr(k,v) for k,v in [('Sector',SECTORS.get(ticker,'Unknown')),('Price Driver',s.get('price_follows','—')),('Rev 3Y CAGR',fp(s.get('rev_3y_cagr'))),('FCF TTM',fm((s.get('fcf_ttm') or 0)*1e6)),('Net Debt',fm((s.get('net_debt_ttm') or 0)*1e6))]), unsafe_allow_html=True)

    # ── SCENARIOS ────────────────────────────────────────────────
    with tabs[5]:
        if ai and 'error' not in ai and ai.get('scenarios'):
            sc = ai['scenarios']
            c1,c2,c3 = st.columns(3)
            for col,key,lbl,css in [(c1,'bear','🐻  BEAR','sc-bear'),(c2,'base','📊  BASE','sc-base'),(c3,'bull','🐂  BULL','sc-bull')]:
                d = sc.get(key,{}); p = _safe_float(d.get('price')) or 0
                with col:
                    st.markdown(f'<div class="{css}"><div style="font-family:IBM Plex Mono,monospace;font-size:10px;font-weight:600;margin-bottom:8px">{lbl}</div><div style="font-family:IBM Plex Sans,sans-serif;font-size:26px;font-weight:700;margin-bottom:4px">${p:,.0f}</div><div style="font-family:IBM Plex Mono,monospace;font-size:14px;margin-bottom:14px">{d.get("return","—")}</div><div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#5a6480;text-align:left;line-height:1.6">{d.get("trigger","—")}</div></div>', unsafe_allow_html=True)
            if ai.get('catalysts'):
                st.markdown(sh('⚡  Catalyst Timeline'), unsafe_allow_html=True)
                for c in ai.get('catalysts',[]):
                    h = c.get('horizon','MID'); tc = 'tl-n' if h=='NEAR' else 'tl-m' if h=='MID' else 'tl-l'
                    imp = c.get('impact','MEDIUM'); ic = '#00d97e' if imp=='CONFIRMED' else '#f04444' if imp=='HIGH' else '#f5a623' if imp=='MEDIUM' else '#2a3040'
                    st.markdown(f'<div class="tl {tc}"><div style="display:flex;align-items:center;justify-content:space-between"><span style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#b8c4d8;flex:1">{c.get("text","")}</span><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;margin:0 10px">{c.get("timing","")}</span><span style="background:{ic}15;border:1px solid {ic}40;color:{ic};font-family:IBM Plex Mono,monospace;font-size:7px;padding:1px 5px;border-radius:2px">{imp}</span></div></div>', unsafe_allow_html=True)
        else:
            hyp = s.get('hypothesis_price','')
            if hyp: st.markdown(f'<div style="background:#080a0f;border:1px solid rgba(0,217,126,.2);border-radius:3px;padding:12px 16px;font-family:IBM Plex Mono,monospace;font-size:10px;color:#00d97e;line-height:1.7">{hyp}</div>', unsafe_allow_html=True)
            st.info("🤖  Add Gemini key to generate Bear/Base/Bull scenarios and catalyst timeline.")

    # ── RISK ─────────────────────────────────────────────────────
    with tabs[6]:
        if ai and 'error' not in ai and ai.get('risks'):
            qs = [('HIGH PROB / HIGH IMPACT','HIGH','HIGH','rq-hh','#f04444'),
                  ('HIGH PROB / LOW IMPACT','HIGH','LOW','rq-hl','#f5a623'),
                  ('LOW PROB / HIGH IMPACT','LOW','HIGH','rq-lh','#f5a623'),
                  ('LOW PROB / LOW IMPACT','LOW','LOW','rq-ll','#00d97e')]
            cols = st.columns(2)
            for i,(lbl,prob,imp,css,bc) in enumerate(qs):
                items = [r for r in ai['risks'] if r.get('prob')==prob and r.get('imp')==imp]
                with cols[i%2]:
                    html = f'<div class="{css}" style="margin-bottom:8px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:1px;color:{bc};margin-bottom:8px">{lbl}</div>'
                    for r in (items or []):
                        s2 = r.get('sev','🟡'); rc = '#f04444' if s2=='🔴' else '#f5a623' if s2=='🟡' else '#00d97e'
                        html += f'<div style="background:#080a0f;border-radius:2px;padding:6px 8px;margin-bottom:4px;border-left:2px solid {rc}"><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#b8c4d8">{s2} {r.get("risk","")}</div><div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;margin-top:2px">{r.get("detail","")}</div></div>'
                    if not items: html += '<div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#1c2030;font-style:italic">No items</div>'
                    html += '</div>'
                    st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("🤖  Add Gemini key to generate the Risk Matrix.")
        # Balance sheet risk from FMP
        bal = fin.get('balance') or []
        if bal:
            lat_b = bal[-1] if bal else {}
            st.markdown(sh('📊  Balance Sheet (FMP)'), unsafe_allow_html=True)
            b_items = [('Cash & Equivalents',fm(lat_b.get('cash'))),('Total Debt',fm(lat_b.get('total_debt'))),
                       ('Net Debt',fm(lat_b.get('net_debt'))),('Total Assets',fm(lat_b.get('total_assets'))),
                       ('Equity',fm(lat_b.get('total_equity'))),('Current Ratio',fv(lat_b.get('current_ratio')))]
            st.markdown(''.join(dr(k,v) for k,v in b_items), unsafe_allow_html=True)

    # ── DECISION ─────────────────────────────────────────────────
    with tabs[7]:
        if ai and 'error' not in ai:
            sig2 = ai.get('signal','—'); sig_c2 = SIG_CLR.get(sig2,'#f5a623')
            conv2 = int(ai.get('conviction',3)); grade2 = ai.get('grade','—')
            c_l, c_r = st.columns([1,1])
            with c_l:
                rows_d = [('SIGNAL',sig2,sig_c2,14,700),('GRADE',grade2,'#22d3ee',18,700),
                          ('CONVICTION','★'*conv2+'☆'*(5-conv2),'#f5a623',14,400),
                          ('ENTRY PRICE',ai.get('entry_price','—'),sig_c2,13,600),
                          ('3Y TARGET',ai.get('target_3y','—'),'#00d97e',13,600),
                          ('3Y RETURN',ai.get('return_3y','—'),'#00d97e',13,600),
                          ('P.A. RETURN',ai.get('pa','—'),'#00d97e',11,400),
                          ('RISK SCORE',f"{ai.get('risk_score',50)}/100",'#f04444',11,400),
                          ('ANTIGRAVITY',f"{ai.get('antigravity_score',50)}/100",'#a78bfa',11,400)]
                row_html = ''.join([f'<div style="display:flex;justify-content:space-between;border-bottom:1px solid #0c0e14;padding:7px 0"><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;letter-spacing:1px">{k}</span><span style="font-family:IBM Plex Mono,monospace;font-size:{sz}px;color:{vc};font-weight:{wt}">{v}</span></div>' for k,v,vc,sz,wt in rows_d])
                st.markdown(f'<div style="background:#080a0f;border:2px solid {sig_c2}55;border-radius:5px;padding:18px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#2a3040;margin-bottom:8px">INVESTMENT DECISION</div>{row_html}<div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:{sig_c2};margin-top:8px">VERDICT</div><div style="font-family:IBM Plex Mono,monospace;font-size:9px;color:{sig_c2};line-height:1.6;margin-top:4px">{ai.get("verdict","—")}</div></div>', unsafe_allow_html=True)
            with c_r:
                for sec,icon,bc in [('key_edge','⚡ KEY EDGE','#00d97e'),('exit_trigger','🚪 EXIT TRIGGER','#f04444'),('watch_item','👁  WATCH ITEM','#f5a623')]:
                    txt = ai.get(sec,'')
                    if txt: st.markdown(f'<div style="background:#080a0f;border:1px solid {bc}22;border-left:2px solid {bc};border-radius:3px;padding:10px 14px;margin-bottom:6px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:{bc};margin-bottom:4px">{icon}</div><div style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#5a6480;line-height:1.6">{txt}</div></div>', unsafe_allow_html=True)
        else:
            c1,c2,c3 = st.columns(3)
            c1.markdown(kpi(str(s.get('recommendation','—')), 'Recommendation', 'g', 16), unsafe_allow_html=True)
            pts_v = _safe_float(s.get('points') or s.get('reconcile'))
            c2.markdown(kpi(f"{pts_v:.1f}/10" if pts_v else '—', 'Pykupz Score', 'c', 16), unsafe_allow_html=True)
            c3.markdown(kpi(str(s.get('hypothesis_price','—') or '—'), 'Hypothesis Price', '', 12), unsafe_allow_html=True)
            st.info("🤖  Add Gemini key for full decision box: entry, target, exit trigger, key edge, grade A+→F.")
        if model and ai and 'error' not in ai:
            if st.button(f"🔄  Re-analyse {ticker} with Gemini"):
                st.session_state.ai_cache.pop(f"ai_{ticker}", None)
                st.rerun()

    # ── CHARTS ───────────────────────────────────────────────────
    with tabs[8]:
        hist = eng.history_yf(ticker, "5y")
        fig_p = chart_price(ticker, hist)
        if fig_p:
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#5a6480">● Price history: yfinance · MA50/MA200 included</div>', unsafe_allow_html=True)
        else:
            st.warning(f"Price chart unavailable for {ticker}. Check if ticker is listed on US exchanges.")
        hist1 = eng.history_yf(ticker, "1y")
        if not hist1.empty:
            f1 = chart_price(ticker, hist1)
            if f1:
                f1.update_layout(title=dict(text=f'Price & Volume — {ticker}  (1 Year)'))
                st.plotly_chart(f1, use_container_width=True)

# ═════════════════════════════════════════════════════════════════
#  PORTFOLIO OVERVIEW
# ═════════════════════════════════════════════════════════════════

def render_portfolio():
    st.markdown('<div class="pyk-header"><div><div class="pyk-logo">⚡  PYKUPZ — 78-STOCK UNIVERSE</div><div class="pyk-sub">CITADEL GLOBAL EQUITIES · FUNDAMENTAL RESEARCH · Q1 2026 · CONFIDENTIAL</div></div><div style="text-align:right;font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040">{}</div></div>'.format(datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)
    total = len(ALL_STOCKS)
    buys  = sum(1 for s in ALL_STOCKS if 'buy' in str(s.get('recommendation','')).lower())
    watch = sum(1 for s in ALL_STOCKS if 'watch' in str(s.get('recommendation','')).lower())
    pe_vals = [_safe_float(s.get('pe')) for s in ALL_STOCKS if _safe_float(s.get('pe')) and 0 < _safe_float(s.get('pe')) < 500]
    avg_pe = np.mean(pe_vals) if pe_vals else 0
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(kpi(total,'Total Stocks','b',22), unsafe_allow_html=True)
    c2.markdown(kpi(buys,'Buy Signals','g',22), unsafe_allow_html=True)
    c3.markdown(kpi(watch,'Watch','a',22), unsafe_allow_html=True)
    c4.markdown(kpi(len(st.session_state.ai_cache),'AI Analyses','c',22), unsafe_allow_html=True)
    c5.markdown(kpi(f"{avg_pe:.0f}x",'Avg PE (Universe)','a',22), unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    fig_map = chart_universe_map(ALL_STOCKS)
    if fig_map: st.plotly_chart(fig_map, use_container_width=True)
    st.markdown(sh('📋  Master Table — All 78 Stocks'), unsafe_allow_html=True)
    rows = []
    for s in ALL_STOCKS:
        ai_s = st.session_state.ai_cache.get(f"ai_{s['ticker']}", {})
        pe_v = _safe_float(s.get('pe'))
        rows.append({
            '#': s.get('sr',''), 'Ticker': s['ticker'], 'Name': s['name'][:28],
            'Sector': SECTORS.get(s['ticker'],'—'),
            'PE': f"{pe_v:.1f}x" if pe_v and 0<pe_v<500 else '—',
            'PS': fv(s.get('ps')),
            'MCap ($B)': fn(s.get('mcap_b'), pre='', suf='', dec=1),
            'Price': fn(s.get('price'), suf='', dec=2),
            'Rev Grw%': fp(s.get('rev_growth_ly')),
            'EPS CAGR': fp(s.get('eps_3y_cagr')),
            'FCF TTM': fm((_safe_float(s.get('fcf_ttm')) or 0)*1e6),
            'Score /10': f"{_safe_float(s.get('points')):.1f}" if _safe_float(s.get('points')) else '—',
            'Rec': str(s.get('recommendation','')).strip(),
            'AI Signal': ai_s.get('signal','—') if ai_s and 'error' not in ai_s else '—',
            'Grade': ai_s.get('grade','—') if ai_s and 'error' not in ai_s else '—',
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=560, hide_index=True)
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        sec_cnt = {}
        for s in ALL_STOCKS:
            k = SECTORS.get(s['ticker'],'Other'); sec_cnt[k] = sec_cnt.get(k,0)+1
        df_s = pd.DataFrame(list(sec_cnt.items()), columns=['Sector','Count']).sort_values('Count')
        fig_s = go.Figure(go.Bar(x=df_s['Count'],y=df_s['Sector'],orientation='h',
            marker=dict(color=df_s['Count'],colorscale=[[0,'#1c2030'],[0.5,'#22d3ee'],[1,'#00d97e']]),
            text=df_s['Count'],textposition='outside',textfont=dict(size=8,color='#5a6480')))
        _theme(fig_s,'Stocks by Sector',h=380); st.plotly_chart(fig_s,use_container_width=True)
    with c_s2:
        mc_cnt = {}
        for s in ALL_STOCKS:
            k = str(s.get('mcap_cat','?')).strip() or '?'; mc_cnt[k] = mc_cnt.get(k,0)+1
        df_mc = pd.DataFrame(list(mc_cnt.items()), columns=['Cat','Count'])
        fig_mc = go.Figure(go.Pie(labels=df_mc['Cat'],values=df_mc['Count'],hole=0.45,
            marker_colors=['#00d97e','#22d3ee','#4f8ef7','#a78bfa','#f5a623','#f04444','#5a6480'],
            textfont=dict(family="'IBM Plex Mono',monospace",size=9,color='#b8c4d8'),
            hovertemplate='%{label}: %{value}<extra></extra>'))
        _theme(fig_mc,'MCap Distribution',h=380); st.plotly_chart(fig_mc,use_container_width=True)

# ═════════════════════════════════════════════════════════════════
#  SCANNER
# ═════════════════════════════════════════════════════════════════

def render_scanner():
    st.markdown('<div class="pyk-header"><div><div class="pyk-logo">🚀  ANTIGRAVITY SCANNER</div><div class="pyk-sub">AI IDENTIFIES STOCKS DEFYING MARKET GRAVITY · MULTI-SOURCE LIVE DATA</div></div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    model = ai_model(); eng = engine()
    if not model:
        st.info("🤖  Add your free Gemini API key in the sidebar to run the Antigravity Scanner.")
        return
    c1,c2 = st.columns([3,1])
    with c1: n = st.slider("Stocks to scan",5,20,10)
    with c2: run = st.button("🚀  RUN SCAN",use_container_width=True)
    if run:
        top = sorted([s for s in ALL_STOCKS if _safe_float(s.get('points'))],
                     key=lambda x: _safe_float(x.get('points',0)), reverse=True)[:n]
        prog = st.progress(0,"Scanning...")
        for i,s in enumerate(top):
            t = s['ticker']
            if f"ai_{t}" not in st.session_state.ai_cache:
                q,_ = eng.get_quote(t,s); fin = eng.get_financials(t)
                ai_analyze(model,t,s,q,fin)
            prog.progress((i+1)/len(top),f"Scanning {t}... {i+1}/{len(top)}")
        prog.empty(); st.rerun()
    cached = [(k.replace('ai_',''),v) for k,v in st.session_state.ai_cache.items() if 'error' not in v]
    if cached:
        cached.sort(key=lambda x: x[1].get('antigravity_score',0),reverse=True)
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;padding:4px 0">{len(cached)} stocks analysed · sorted by Antigravity Score</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(t,ai_r) in enumerate(cached[:12]):
            s_d = next((s for s in ALL_STOCKS if s['ticker']==t),{})
            ag = ai_r.get('antigravity_score',0); sig = ai_r.get('signal','—')
            grade = ai_r.get('grade','—'); sig_c = SIG_CLR.get(sig,'#f5a623')
            ag_c = '#00d97e' if ag>=70 else '#f5a623' if ag>=40 else '#f04444'
            with cols[i%3]:
                st.markdown(f'<div style="background:#080a0f;border:1px solid {ag_c}33;border-top:2px solid {ag_c};border-radius:4px;padding:14px;margin-bottom:8px"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-family:IBM Plex Mono,monospace;font-size:16px;font-weight:700;color:{ag_c}">{t}</span><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040">{SECTORS.get(t,"")[:18]}</span></div><div style="display:flex;justify-content:space-between;margin-bottom:8px"><div><div style="font-family:IBM Plex Mono,monospace;font-size:28px;color:{ag_c};line-height:1;font-weight:700">{ag}</div><div style="font-family:IBM Plex Mono,monospace;font-size:7px;color:#2a3040;letter-spacing:1px">ANTIGRAVITY</div></div><div style="text-align:right"><div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:{sig_c}">{sig}</div><div style="font-family:IBM Plex Sans,sans-serif;font-size:22px;font-weight:700;color:#22d3ee">{grade}</div></div></div><div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040;line-height:1.5">{ai_r.get("antigravity_reason","")[:90]}</div><div style="margin-top:6px"><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#00d97e">{ai_r.get("target_3y","—")}</span><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#2a3040"> · </span><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#00d97e">{ai_r.get("return_3y","—")}</span></div></div>', unsafe_allow_html=True)
                if st.button(f"Open {t}",key=f"open_{t}",use_container_width=True):
                    st.session_state.ticker=t; st.session_state.main_view='stock'; st.rerun()

# ═════════════════════════════════════════════════════════════════
#  CHAT
# ═════════════════════════════════════════════════════════════════

def render_chat():
    st.markdown('<div class="pyk-header"><div><div class="pyk-logo">💬  AI ANALYST CHAT</div><div class="pyk-sub">ASK ANYTHING — LIVE DATA + 78-STOCK UNIVERSE CONTEXT</div></div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    model = ai_model()
    for h in st.session_state.chat_hist[-12:]:
        ic = "🤖" if h['role']=='model' else "👤"
        bg = '#080a0f' if h['role']=='model' else '#0c0e14'
        bc = 'rgba(79,142,247,.2)' if h['role']=='model' else '#1c2030'
        st.markdown(f'<div style="background:{bg};border:1px solid {bc};border-radius:4px;padding:10px 14px;margin-bottom:6px;font-family:IBM Plex Mono,monospace;font-size:10px;line-height:1.7;color:#b8c4d8">{ic}  {h["content"]}</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([5,1])
    with c1: q = st.text_input("##cq",placeholder="Compare NVDA vs AMD · Is MELI cheap? · Best FCF yields · Explain CRM moat ...",label_visibility="collapsed")
    with c2: clear = st.button("Clear",use_container_width=True)
    if clear: st.session_state.chat_hist=[]; st.rerun()
    if q:
        ctx = f"Selected: {st.session_state.ticker}. Analysed: {list(st.session_state.ai_cache.keys())[:6]}. FMP: {'connected' if st.session_state.fkey else 'no key'}. yfinance: {'available' if YF_AVAILABLE else 'no'}."
        with st.spinner("🤖"): reply = ai_chat(model, q, ctx)
        st.session_state.chat_hist.append({'role':'user','content':q})
        st.session_state.chat_hist.append({'role':'model','content':reply})
        st.rerun()

# ═════════════════════════════════════════════════════════════════
#  TICKER TAPE
# ═════════════════════════════════════════════════════════════════

def render_tape():
    items = []
    for s in ALL_STOCKS[:30]:
        p = _safe_float(s.get('price')) or 0
        r = _safe_float(s.get('ath_retrace')) or 0
        cls = 'ti-g' if r >= 0 else 'ti-r'
        items.append(f'<span class="ti {cls}">{s["ticker"]}  ${p:,.2f}</span>')
    tape = ''.join(items) * 2
    st.markdown(f'<div class="tape"><div class="tape-inner">{tape}</div></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════

def main():
    render_sidebar()
    render_tape()
    view = st.session_state.main_view
    if view == 'portfolio':
        render_portfolio()
    elif view == 'scanner':
        render_scanner()
    elif view == 'chat':
        render_chat()
    else:
        render_stock(st.session_state.ticker)

if __name__ == "__main__":
    main()
