# ═══════════════════════════════════════════════════════════════════
#  PYKUPZ INSTITUTIONAL TERMINAL  v6
#  Bloomberg-Grade · 78-Stock Research Terminal · Q1 2026
# ═══════════════════════════════════════════════════════════════════
#
#  DEPLOYMENT: Upload app.py + stocks_data.json + requirements.txt
#  to GitHub and deploy on share.streamlit.io
#
#  requirements.txt:
#    streamlit==1.32.0
#    yfinance==0.2.54
#    pandas==2.2.1
#    numpy==1.26.4
#    plotly==5.20.0
#    google-generativeai==0.8.0
#    requests==2.31.0

import sys, os, json, re, time, warnings
from datetime import datetime
warnings.filterwarnings("ignore")

# ── Robust imports with fallback messages ────────────────────────
import streamlit as st

def _require(pkg, import_name=None):
    import importlib
    name = import_name or pkg
    try:
        return importlib.import_module(name)
    except ImportError:
        st.error(f"Missing: `{pkg}`. Ensure requirements.txt has `{pkg}` and reboot the app.")
        st.stop()

pd   = _require("pandas")
np   = _require("numpy")
yf   = _require("yfinance")
go   = _require("plotly.graph_objects", "plotly.graph_objects")
px   = _require("plotly.express", "plotly.express")
make_subplots = _require("plotly.subplots", "plotly.subplots").make_subplots
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf


# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="PYKUPZ · Institutional Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Master CSS — Institutional Bloomberg-grade theme ────────────
MASTER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:      #040508;
  --bg1:     #08090d;
  --bg2:     #0d0f14;
  --bg3:     #12141a;
  --bg4:     #1a1d26;
  --border:  #1e2230;
  --border2: #2a2f40;
  --green:   #00d97e;
  --green2:  rgba(0,217,126,0.08);
  --red:     #f04444;
  --red2:    rgba(240,68,68,0.08);
  --amber:   #f5a623;
  --amber2:  rgba(245,166,35,0.08);
  --blue:    #4f8ef7;
  --blue2:   rgba(79,142,247,0.08);
  --cyan:    #22d3ee;
  --pu:      #a78bfa;
  --text:    #c8d0e0;
  --text2:   #6b7691;
  --text3:   #3a4158;
  --white:   #f0f4ff;
  --fm: 'IBM Plex Mono', monospace;
  --fs: 'IBM Plex Sans', sans-serif;
}

/* ── Reset ── */
html, body, [class*="css"], .main { background: var(--bg) !important; color: var(--text) !important; }
.block-container { padding: 0 !important; max-width: 100% !important; background: var(--bg) !important; }
* { box-sizing: border-box; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--green); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--border) !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput input {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--white) !important;
  font-family: var(--fm) !important;
  font-size: 11px !important;
  border-radius: 3px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg1) !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0 16px !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--fm) !important;
  font-size: 10px !important;
  letter-spacing: 1.5px !important;
  color: var(--text3) !important;
  padding: 10px 18px !important;
  border-bottom: 2px solid transparent !important;
  background: transparent !important;
  text-transform: uppercase !important;
}
.stTabs [aria-selected="true"] {
  color: var(--green) !important;
  border-bottom: 2px solid var(--green) !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: var(--bg) !important;
  padding: 16px !important;
}

/* ── Buttons ── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--text2) !important;
  font-family: var(--fm) !important;
  font-size: 10px !important;
  letter-spacing: 1px !important;
  border-radius: 3px !important;
  padding: 5px 14px !important;
  transition: all 0.15s !important;
}
.stButton > button:hover {
  border-color: var(--green) !important;
  color: var(--green) !important;
  background: var(--green2) !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  color: var(--white) !important;
  font-family: var(--fm) !important;
  font-size: 11px !important;
  border-radius: 3px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 2px rgba(0,217,126,0.15) !important;
}
.stSelectbox > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  color: var(--white) !important;
  font-family: var(--fm) !important;
  font-size: 11px !important;
}

/* ── Metrics ── */
div[data-testid="metric-container"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  padding: 10px 14px !important;
}
div[data-testid="metric-container"] label {
  font-family: var(--fm) !important;
  font-size: 9px !important;
  letter-spacing: 1.5px !important;
  color: var(--text3) !important;
  text-transform: uppercase !important;
}
div[data-testid="metric-container"] > div { color: var(--white) !important; font-family: var(--fm) !important; }

/* ── Dataframe ── */
.stDataFrame { background: transparent !important; }
.stDataFrame iframe { border: 1px solid var(--border) !important; border-radius: 4px !important; }

/* ── Expander ── */
details { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; }
.streamlit-expanderHeader {
  font-family: var(--fm) !important; font-size: 10px !important; letter-spacing: 1px !important;
  color: var(--text2) !important; text-transform: uppercase !important;
}
.streamlit-expanderContent { background: var(--bg2) !important; }

/* ── Progress ── */
.stProgress .st-bo { background: var(--green) !important; }
.stProgress > div { background: var(--bg3) !important; border-radius: 2px !important; }

/* ── Alerts ── */
.stAlert { background: var(--bg2) !important; border-left-color: var(--blue) !important; border-radius: 4px !important; }

/* ── Sidebar buttons ── */
.sidebar-stock-btn {
  display: flex; align-items: center; padding: 7px 12px;
  border-bottom: 1px solid var(--bg3);
  cursor: pointer; transition: background 0.1s;
  font-family: var(--fm); font-size: 10px;
}
.sidebar-stock-btn:hover { background: var(--bg3); }
.sidebar-stock-btn.active { background: var(--bg3); border-left: 2px solid var(--green); }

/* ── Card components ── */
.pyk-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 4px 0;
}
.pyk-card.green  { border-top: 2px solid var(--green); }
.pyk-card.red    { border-top: 2px solid var(--red); }
.pyk-card.amber  { border-top: 2px solid var(--amber); }
.pyk-card.blue   { border-top: 2px solid var(--blue); }
.pyk-card.cyan   { border-top: 2px solid var(--cyan); }
.pyk-card.pu     { border-top: 2px solid var(--pu); }

.pyk-val  { font-family: var(--fm); font-size: 19px; font-weight: 600; color: var(--white); line-height: 1.1; }
.pyk-lbl  { font-family: var(--fm); font-size: 8px; letter-spacing: 1.5px; color: var(--text3); text-transform: uppercase; margin-top: 3px; }
.pyk-sub  { font-family: var(--fm); font-size: 10px; color: var(--text2); margin-top: 2px; }

.section-header {
  font-family: var(--fm); font-size: 9px; letter-spacing: 2.5px; color: var(--text3);
  text-transform: uppercase; border-bottom: 1px solid var(--border);
  padding-bottom: 5px; margin: 12px 0 10px;
}
.section-header.green { color: var(--green); border-color: var(--green); border-bottom-width: 1px; }

/* ── Ticker tape ── */
.ticker-tape {
  background: var(--bg1); border-bottom: 1px solid var(--border);
  padding: 5px 0; overflow: hidden; white-space: nowrap;
}
.ticker-inner { display: inline-block; animation: scroll-tape 120s linear infinite; }
@keyframes scroll-tape { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.tick-item { display: inline-block; margin: 0 20px; font-family: var(--fm); font-size: 10px; }
.tick-up   { color: var(--green); }
.tick-dn   { color: var(--red); }
.tick-fl   { color: var(--text3); }

/* ── Signal badges ── */
.sig { display: inline-block; padding: 2px 8px; border-radius: 2px; font-family: var(--fm); font-size: 9px; letter-spacing: 0.5px; font-weight: 600; }
.sig-sbuy  { background: rgba(0,217,126,0.15); border: 1px solid rgba(0,217,126,0.4); color: #00d97e; }
.sig-buy   { background: rgba(0,217,126,0.1); border: 1px solid rgba(0,217,126,0.3); color: #00d97e; }
.sig-hold  { background: rgba(79,142,247,0.1); border: 1px solid rgba(79,142,247,0.3); color: #4f8ef7; }
.sig-watch { background: rgba(245,166,35,0.1); border: 1px solid rgba(245,166,35,0.3); color: #f5a623; }
.sig-sell  { background: rgba(240,68,68,0.1); border: 1px solid rgba(240,68,68,0.3); color: #f04444; }

/* ── Table rows ── */
.data-row { display: flex; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--bg3); font-family: var(--fm); font-size: 10px; }
.data-row:last-child { border-bottom: none; }
.data-key { color: var(--text3); min-width: 160px; flex-shrink: 0; }
.data-val { color: var(--white); }

/* ── Risk quadrants ── */
.rq-hihi { background: rgba(240,68,68,0.06); border: 1px solid rgba(240,68,68,0.2); border-radius: 3px; padding: 10px; }
.rq-hilo { background: rgba(245,166,35,0.05); border: 1px solid rgba(245,166,35,0.2); border-radius: 3px; padding: 10px; }
.rq-lohi { background: rgba(245,166,35,0.05); border: 1px solid rgba(245,166,35,0.2); border-radius: 3px; padding: 10px; }
.rq-lolo { background: rgba(0,217,126,0.04); border: 1px solid rgba(0,217,126,0.15); border-radius: 3px; padding: 10px; }

/* ── AI panel ── */
.ai-panel {
  background: linear-gradient(135deg, #040508 0%, #08090f 60%, #040810 100%);
  border: 1px solid rgba(79,142,247,0.3);
  border-radius: 5px; padding: 16px; margin: 6px 0; position: relative;
}
.ai-panel::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 5px 5px 0 0;
  background: linear-gradient(90deg, #4f8ef7, #22d3ee, #00d97e, #a78bfa);
}
.ai-badge {
  display: inline-block; background: rgba(79,142,247,0.12); border: 1px solid rgba(79,142,247,0.3);
  border-radius: 2px; padding: 1px 7px; font-family: var(--fm); font-size: 8px; color: #4f8ef7; letter-spacing: 1px;
}

/* ── Timeline ── */
.tl-item { border-left: 2px solid var(--border2); padding: 5px 12px; margin-bottom: 6px; }
.tl-near { border-left-color: var(--green); }
.tl-mid  { border-left-color: var(--amber); }
.tl-long { border-left-color: var(--text3); }

/* ── Scenario cards ── */
.sc-bear { background: rgba(240,68,68,0.06); border: 1px solid rgba(240,68,68,0.2); border-top: 2px solid var(--red); border-radius: 4px; padding: 16px; text-align: center; }
.sc-base { background: rgba(0,217,126,0.06); border: 1px solid rgba(0,217,126,0.2); border-top: 2px solid var(--green); border-radius: 4px; padding: 16px; text-align: center; }
.sc-bull { background: rgba(245,166,35,0.06); border: 1px solid rgba(245,166,35,0.2); border-top: 2px solid var(--amber); border-radius: 4px; padding: 16px; text-align: center; }

/* ── Moat stars ── */
.moat-card { background: var(--bg2); border: 1px solid var(--border); border-radius: 3px; padding: 10px 14px; margin-bottom: 6px; }
.moat-card:hover { border-color: var(--border2); }

/* ── Header ── */
.pyk-header {
  background: var(--bg1); border-bottom: 1px solid var(--border);
  padding: 10px 20px; display: flex; align-items: center; justify-content: space-between;
}
.pyk-logo { font-family: var(--fm); font-size: 16px; font-weight: 700; letter-spacing: 4px; color: var(--green); }
.pyk-tagline { font-family: var(--fm); font-size: 8px; letter-spacing: 2px; color: var(--text3); margin-top: 2px; }
</style>
"""
st.markdown(MASTER_CSS, unsafe_allow_html=True)

# ── Load stock universe ──────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_stocks():
    for path in ["stocks_data.json", "data/stocks_data.json",
                 os.path.join(os.path.dirname(__file__), "stocks_data.json")]:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    st.error("stocks_data.json not found. Upload it to the same folder as app.py.")
    st.stop()

ALL_STOCKS = load_stocks()
TICKERS = [s['ticker'] for s in ALL_STOCKS]

# Sector mapping
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

SIG_CLR = {
    'STRONG BUY':'#00d97e','BUY':'#00d97e','Buy':'#00d97e','Strong Buy':'#00d97e',
    'HOLD':'#4f8ef7','Hold':'#4f8ef7','ACCUMULATE':'#22d3ee','Accumulate':'#22d3ee',
    'WATCH':'#f5a623','Watch':'#f5a623',
    'SELL':'#f04444','Sell':'#f04444','STRONG SELL':'#f04444',
}

SIG_CSS = {
    'STRONG BUY':'sig-sbuy','BUY':'sig-buy','Buy':'sig-buy','Strong Buy':'sig-sbuy',
    'HOLD':'sig-hold','Hold':'sig-hold','ACCUMULATE':'sig-hold','Accumulate':'sig-hold',
    'WATCH':'sig-watch','Watch':'sig-watch',
    'SELL':'sig-sell','Sell':'sig-sell',
}

# ── Session state ────────────────────────────────────────────────
for k, v in {
    'ticker': 'NVDA',
    'gemini_key': os.environ.get('GEMINI_API_KEY', ''),
    'ai_cache': {},
    'chat_hist': [],
    'main_view': 'stock',
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Gemini ───────────────────────────────────────────────────────
@st.cache_resource
def _gemini_model(key):
    if not key: return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        return genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"temperature":0.35,"max_output_tokens":2048}
        )
    except Exception:
        return None

def get_model():
    return _gemini_model(st.session_state.gemini_key)

# ── Live data (with full fallback to Excel data) ─────────────────
@st.cache_data(ttl=120, show_spinner=False)
def live_price(ticker):
    try:
        h = yf.Ticker(ticker).history(period="5d", timeout=8)
        if h.empty or len(h) < 2: return None, None
        p = float(h['Close'].iloc[-1])
        prev = float(h['Close'].iloc[-2])
        return p, (p - prev) / prev
    except Exception:
        return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def live_info(ticker):
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def live_history(ticker, period="5y"):
    try:
        h = yf.Ticker(ticker).history(period=period, timeout=12)
        if h.empty: return pd.DataFrame()
        h.index = pd.to_datetime(h.index).tz_localize(None) if h.index.tzinfo is None else pd.to_datetime(h.index).tz_convert(None)
        return h
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def live_financials(ticker):
    try:
        t = yf.Ticker(ticker)
        return {'income': t.income_stmt, 'cashflow': t.cash_flow, 'balance': t.balance_sheet}
    except Exception:
        return {'income': None, 'cashflow': None, 'balance': None}

# ── Format helpers ────────────────────────────────────────────────
def fn(v, prefix='$', suffix='', dec=1, na='—'):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))): return na
    try: f = float(v); return f"{prefix}{f:,.{dec}f}{suffix}"
    except: return na

def fp(v, mul=True, na='—'):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))): return na
    try:
        f = float(v) * (100 if mul else 1)
        s = '+' if f >= 0 else ''
        return f"{s}{f:.1f}%"
    except: return na

def fv(v, na='—'):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))): return na
    try: return f"{float(v):.2f}x"
    except: return na

def clr(v, mul=True):
    try: return '#00d97e' if float(v) * (100 if mul else 1) >= 0 else '#f04444'
    except: return '#6b7691'

def sig_badge(rec):
    rec = str(rec).strip()
    css = SIG_CSS.get(rec, SIG_CSS.get(rec.upper(), 'sig-watch'))
    return f'<span class="sig {css}">{rec.upper()}</span>'

# ── Chart theme ───────────────────────────────────────────────────
def chart_theme(fig, title='', h=380, bg='#040508'):
    fig.update_layout(
        paper_bgcolor=bg, plot_bgcolor='#08090d',
        font=dict(family="'IBM Plex Mono',monospace", color='#3a4158', size=9),
        title=dict(text=title, font=dict(color='#c8d0e0', size=12, family="'IBM Plex Mono',monospace"), x=0.01),
        height=h, margin=dict(l=8, r=8, t=38, b=8),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)',
                    font=dict(size=9, color='#6b7691'), orientation='h', y=1.08, x=0),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#12141a', bordercolor='#1e2230',
                        font=dict(family="'IBM Plex Mono',monospace", color='#c8d0e0', size=9)),
    )
    fig.update_xaxes(gridcolor='#0d0f14', zeroline=False, zerolinecolor='#1e2230',
                     tickfont=dict(size=9, color='#3a4158'), showline=True, linecolor='#1e2230')
    fig.update_yaxes(gridcolor='#0d0f14', zeroline=False, zerolinecolor='#1e2230',
                     tickfont=dict(size=9, color='#3a4158'), showline=False)
    return fig


# ══════════════════ CHART BUILDERS ══════════════════════════════

def chart_price(ticker, hist):
    if hist is None or hist.empty:
        return None
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.72, 0.28], vertical_spacing=0.03)
    # Price
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], name='Price',
        mode='lines', line=dict(color='#00d97e', width=1.5),
        fill='tozeroy', fillcolor='rgba(0,217,126,0.04)',
        hovertemplate='$%{y:.2f}<extra></extra>'
    ), row=1, col=1)
    if len(hist) >= 50:
        ma50 = hist['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(x=ma50.index, y=ma50, name='MA50',
            mode='lines', line=dict(color='#f5a623', width=1, dash='dot'),
            hovertemplate='MA50: $%{y:.2f}<extra></extra>'), row=1, col=1)
    if len(hist) >= 200:
        ma200 = hist['Close'].rolling(200).mean()
        fig.add_trace(go.Scatter(x=ma200.index, y=ma200, name='MA200',
            mode='lines', line=dict(color='#a78bfa', width=1, dash='dot'),
            hovertemplate='MA200: $%{y:.2f}<extra></extra>'), row=1, col=1)
    # Volume
    vc = ['rgba(0,217,126,0.35)' if c >= o else 'rgba(240,68,68,0.35)'
          for c, o in zip(hist['Close'], hist['Open'])]
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume',
        marker_color=vc, showlegend=False,
        hovertemplate='%{y:,.0f}<extra></extra>'), row=2, col=1)
    chart_theme(fig, f'Price & Volume — {ticker}', h=420)
    fig.update_yaxes(row=2, col=1, tickformat='.2s')
    return fig

def chart_rev_fcf(ticker, fin, s_data):
    """Revenue + EBITDA + FCF from yfinance AND Excel projection data."""
    inc = fin.get('income'); cf = fin.get('cashflow')
    years_live, revs, ebitdas, fcfs = [], [], [], []
    if inc is not None and not inc.empty:
        for col in sorted(inc.columns, reverse=True)[:5]:
            try:
                yr = str(col)[:4]
                rev = next((float(inc.loc[k, col]) / 1e6 for k in
                    ['Total Revenue','Revenue'] if k in inc.index and pd.notna(inc.loc[k, col])), None)
                ebitda = next((float(inc.loc[k, col]) / 1e6 for k in
                    ['EBITDA','Normalized EBITDA'] if k in inc.index and pd.notna(inc.loc[k, col])), None)
                fcf = None
                if cf is not None and not cf.empty and col in cf.columns:
                    fcf = next((float(cf.loc[k, col]) / 1e6 for k in ['Free Cash Flow']
                        if k in cf.index and pd.notna(cf.loc[k, col])), None)
                if rev:
                    years_live.append(yr); revs.append(rev)
                    ebitdas.append(ebitda); fcfs.append(fcf)
            except: pass
    years_live = list(reversed(years_live)); revs = list(reversed(revs))
    ebitdas = list(reversed(ebitdas)); fcfs = list(reversed(fcfs))

    # Append projections from Excel
    proj_years = ['2026E', '2027E', '2028E']
    proj_revs  = [s_data.get('rev_2026e'), s_data.get('rev_2027e'), s_data.get('rev_2028e')]
    proj_ebitda = [s_data.get('ebitda_2026e'), s_data.get('ebitda_2027e'), None]
    all_years = years_live + proj_years
    all_revs  = revs + [v for v in proj_revs]
    all_ebitda = ebitdas + proj_ebitda
    all_fcf    = fcfs + [None, None, None]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Revenue bars (actual = solid, projected = lighter)
    for i, (yr, rv) in enumerate(zip(all_years, all_revs)):
        if rv is None: continue
        is_proj = yr.endswith('E')
        fig.add_trace(go.Bar(
            x=[yr], y=[float(rv)], name='Revenue' if i == 0 else '',
            showlegend=i == 0,
            marker_color='rgba(0,217,126,0.65)' if not is_proj else 'rgba(0,217,126,0.3)',
            marker_line_color='#00d97e' if not is_proj else 'rgba(0,217,126,0.5)',
            marker_line_width=1,
            hovertemplate=f'{yr}: ${rv:,.0f}M<extra>Revenue</extra>'
        ), secondary_y=False)
    # EBITDA line
    eb_x = [y for y,v in zip(all_years, all_ebitda) if v]
    eb_y = [float(v) for v in all_ebitda if v]
    if eb_x:
        fig.add_trace(go.Scatter(x=eb_x, y=eb_y, name='EBITDA',
            mode='lines+markers', line=dict(color='#f5a623', width=2),
            marker=dict(size=5, color='#f5a623'),
            hovertemplate='%{x}: $%{y:,.0f}M<extra>EBITDA</extra>'),
            secondary_y=True)
    # FCF line
    fcf_x = [y for y,v in zip(all_years, all_fcf) if v is not None]
    fcf_y = [float(v) for v in all_fcf if v is not None]
    if fcf_x:
        fig.add_trace(go.Scatter(x=fcf_x, y=fcf_y, name='FCF',
            mode='lines+markers', line=dict(color='#22d3ee', width=2, dash='dot'),
            marker=dict(size=5, color='#22d3ee'),
            hovertemplate='%{x}: $%{y:,.0f}M<extra>FCF</extra>'),
            secondary_y=True)

    chart_theme(fig, f'Revenue · EBITDA · FCF — {ticker}', h=300)
    fig.update_yaxes(title_text='Revenue ($M)', secondary_y=False,
        title_font=dict(size=8, color='#00d97e'), tickformat=',')
    fig.update_yaxes(title_text='EBITDA / FCF ($M)', secondary_y=True,
        title_font=dict(size=8, color='#f5a623'), showgrid=False, tickformat=',')
    return fig

def chart_eps(ticker, s_data, fin):
    periods = ['3Y Ago','Last Yr','TTM','2026E','2027E','2028E']
    vals = [
        s_data.get('eps_3y_ago'), s_data.get('eps_ly'), s_data.get('eps_ttm'),
        s_data.get('eps_2026e'), s_data.get('eps_2027e'), s_data.get('eps_2028e')
    ]
    clean = [(p, float(v)) for p, v in zip(periods, vals) if v and str(v) != 'nan']
    if not clean: return None
    xs = [p for p,v in clean]; ys = [v for p,v in clean]
    is_proj = [p.endswith(('E','TTM')) for p in xs]
    colors = ['rgba(0,217,126,0.7)' if y >= 0 else 'rgba(240,68,68,0.7)' for y in ys]
    colors_proj = ['rgba(0,217,126,0.35)' if y >= 0 else 'rgba(240,68,68,0.35)' for y in ys]
    fig = go.Figure(go.Bar(
        x=xs, y=ys,
        marker_color=[cp if ip else c for c,cp,ip in zip(colors,colors_proj,is_proj)],
        marker_line_color=['#00d97e' if y >= 0 else '#f04444' for y in ys],
        marker_line_width=1,
        text=[f"${v:.2f}" for v in ys], textposition='outside',
        textfont=dict(size=9, color='#6b7691'),
        hovertemplate='%{x}: $%{y:.2f}<extra>EPS</extra>',
        name='EPS'
    ))
    chart_theme(fig, f'EPS Trajectory — {ticker}', h=240)
    return fig

def chart_gaps_gape(ticker, s_data):
    """P/S (GAPS) & P/E (GAPE) history + projections."""
    periods = ['3Y CAGR','TTM','2025E','2026E']
    gaps = [s_data.get('gaps_3y_cagr'), s_data.get('gaps_ttm'), s_data.get('gaps_2025'), s_data.get('gaps_2026')]
    gape = [s_data.get('gape_3y_cagr'), s_data.get('gape_ttm'), s_data.get('gape_2025'), s_data.get('gape_2026')]
    def clean(lst): return [float(v) if v and str(v) not in ('nan','None') else None for v in lst]
    gaps_c = clean(gaps); gape_c = clean(gape)
    if not any(gaps_c) and not any(gape_c): return None
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if any(gaps_c):
        fig.add_trace(go.Bar(x=periods, y=gaps_c, name='P/S (GAPS)',
            marker_color='rgba(34,211,238,0.5)', marker_line_color='#22d3ee', marker_line_width=1,
            hovertemplate='%{x}: %{y:.1f}x<extra>P/S GAPS</extra>'), secondary_y=False)
    if any(gape_c):
        fig.add_trace(go.Scatter(x=periods, y=gape_c, name='P/E (GAPE)',
            mode='lines+markers', line=dict(color='#f5a623', width=2),
            marker=dict(size=6, color='#f5a623'),
            hovertemplate='%{x}: %{y:.1f}x<extra>P/E GAPE</extra>'), secondary_y=True)
    # Current lines
    if s_data.get('ps'): fig.add_hline(y=s_data['ps'], line=dict(color='rgba(34,211,238,0.3)', dash='dot', width=1), row=1, col=1, secondary_y=False)
    if s_data.get('pe'): fig.add_hline(y=s_data['pe'], line=dict(color='rgba(245,166,35,0.3)', dash='dot', width=1), row=1, col=1, secondary_y=True)
    chart_theme(fig, f'Valuation Multiple Trajectory — {ticker}', h=250)
    fig.update_yaxes(title_text='P/S Multiple', secondary_y=False, title_font=dict(size=8, color='#22d3ee'))
    fig.update_yaxes(title_text='P/E Multiple', secondary_y=True, title_font=dict(size=8, color='#f5a623'), showgrid=False)
    return fig

def chart_fcf_net_debt(ticker, s_data):
    """FCF and Net Debt 4-year history bar chart."""
    fcf_vals = [s_data.get('fcf_y3'), s_data.get('fcf_y2'), s_data.get('fcf_y1'), s_data.get('fcf_ttm')]
    nd_vals  = [s_data.get('net_debt_y3'), s_data.get('net_debt_y2'), s_data.get('net_debt_y1'), s_data.get('net_debt_ttm')]
    labels = ['Year -3','Year -2','Year -1','TTM']
    def cl(lst): return [float(v) if v and str(v) not in ('nan','None','inf','-inf') else None for v in lst]
    fcf_c = cl(fcf_vals); nd_c = cl(nd_vals)
    if not any(fcf_c) and not any(nd_c): return None
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if any(fcf_c):
        fc = ['rgba(0,217,126,0.7)' if (v or 0)>=0 else 'rgba(240,68,68,0.7)' for v in fcf_c]
        fig.add_trace(go.Bar(x=labels, y=fcf_c, name='FCF ($M)',
            marker_color=fc, marker_line_color=['#00d97e' if (v or 0)>=0 else '#f04444' for v in fcf_c],
            marker_line_width=1, hovertemplate='%{x}: $%{y:,.0f}M<extra>FCF</extra>'), secondary_y=False)
    if any(nd_c):
        nc = ['rgba(240,68,68,0.6)' if (v or 0)>=0 else 'rgba(0,217,126,0.6)' for v in nd_c]
        fig.add_trace(go.Bar(x=labels, y=nd_c, name='Net Debt ($M)',
            marker_color=nc, marker_line_width=1, hovertemplate='%{x}: $%{y:,.0f}M<extra>Net Debt</extra>'), secondary_y=True)
    chart_theme(fig, f'Free Cash Flow & Net Debt — {ticker}', h=240)
    fig.update_layout(barmode='group')
    return fig

def chart_portfolio_map(stocks):
    rows = []
    for s in stocks:
        try:
            pe_v = float(s['pe']) if s.get('pe') else None
            rg = float(s.get('rev_growth_ly', 0) or 0) * 100
            ps_v = float(s['ps']) if s.get('ps') else 5
            mc = float(s.get('mcap_b', 10) or 10)
            rec = str(s.get('recommendation', 'Watch')).strip()
            if pe_v and 0 < pe_v < 350:
                rows.append({'Ticker': s['ticker'], 'PE': pe_v, 'Rev Grw%': rg,
                             'PS': ps_v, 'MCap': mc, 'Rec': rec,
                             'Sector': SECTORS.get(s['ticker'], 'Other')})
        except: pass
    if not rows: return None
    df = pd.DataFrame(rows)
    color_map = {'Buy':'#00d97e','Strong Buy':'#00d97e','Hold':'#4f8ef7',
                 'Accumulate':'#22d3ee','Watch':'#f5a623','Sell':'#f04444'}
    fig = px.scatter(df, x='Rev Grw%', y='PE', text='Ticker', size='MCap',
        color='Rec', color_discrete_map=color_map, size_max=48,
        hover_data={'Ticker':True,'Rec':True,'Sector':True,'PS':':.2f','MCap':':.0f'})
    fig.update_traces(textposition='top center', textfont=dict(size=8, color='#6b7691'))
    chart_theme(fig, '📊  Universe Map — PE vs Revenue Growth  (bubble = Market Cap)', h=520)
    fig.update_xaxes(title_text='Revenue Growth % (Last Year)', title_font=dict(size=9, color='#6b7691'))
    fig.update_yaxes(title_text='PE Multiple (TTM)', title_font=dict(size=9, color='#6b7691'))
    fig.add_hline(y=30, line=dict(color='rgba(255,255,255,0.06)', dash='dot', width=1))
    fig.add_vline(x=20, line=dict(color='rgba(255,255,255,0.06)', dash='dot', width=1))
    return fig


# ══════════════════ AI FUNCTIONS ═════════════════════════════════

def ai_analyze(model, s, price, chg, info):
    if not model: return None
    key = f"ai_{s['ticker']}"
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    def sp(v, mul=True):
        if v is None or (isinstance(v,float) and np.isnan(v)): return 'N/A'
        try: return f"{float(v)*(100 if mul else 1):.1f}%"
        except: return 'N/A'

    prompt = f"""You are a Citadel Global Equities senior analyst.
Provide deep institutional analysis for {s['ticker']} ({s['name']}).

PORTFOLIO DATA (from Pyk-Inv-List, Q1 2026):
Price: ${price:.2f} | 24H: {(chg or 0)*100:+.2f}% | PE: {s.get('pe')} | PS: {s.get('ps')}
MCap: ${s.get('mcap_b')}B | Category: {s.get('mcap_cat')} | Sector: {SECTORS.get(s['ticker'],'Unknown')}
ATH: ${s.get('high')} | ATH Retrace: {sp(s.get('ath_retrace'))}
Revenue LY: ${s.get('rev_ly'):,.0f}M | Rev Growth LY: {sp(s.get('rev_growth_ly'))} | 3Y CAGR: {sp(s.get('rev_3y_cagr'))}
Rev 2026E: ${s.get('rev_2026e'):,.0f}M (+{sp(s.get('rev_growth_2026'))} | 2027E: ${s.get('rev_2027e'):,.0f}M
EBITDA LY: ${s.get('ebitda_ly'):,.0f}M | EBITDA 3Y CAGR: {sp(s.get('ebitda_3y_cagr'))} | 2026E: ${s.get('ebitda_2026e'):,.0f}M
EPS LY: ${s.get('eps_ly')} | EPS 3Y CAGR: {sp(s.get('eps_3y_cagr'))} | 2026E: ${s.get('eps_2026e')} | 2027E: ${s.get('eps_2027e')}
FCF TTM: ${s.get('fcf_ttm'):,.0f}M | Net Debt TTM: ${s.get('net_debt_ttm'):,.0f}M
Price Follows: {s.get('price_follows')} | Score: {s.get('points')}/10 | Rec: {s.get('recommendation')}
LIVE: MCap ${(info.get('marketCap',0) or 0)/1e9:.1f}B | Beta {info.get('beta')} | Short {(info.get('shortPercentOfFloat',0) or 0)*100:.1f}%

Return ONLY valid JSON, no markdown:
{{"thesis":"2-3 sentence institutional thesis","moat_summary":"1 sentence moat","moat_layers":[{{"layer":"name","stars":1-5,"verdict":"UNASSAILABLE|FORTRESS|STRUCTURAL|BUILDING|NARROW","detail":"1 line"}}],"why_now":"current catalyst for entry","bull_case":["pt1","pt2","pt3"],"bear_case":["risk1","risk2","risk3"],"signal":"STRONG BUY|BUY|ACCUMULATE|HOLD|WATCH|REDUCE|SELL","conviction":1-5,"risk_score":0-100,"antigravity_score":0-100,"antigravity_reason":"1 line why stock defies or follows gravity","entry_price":"$X","target_3y":"$X","return_3y":"+X%","pa":"+X% p.a.","scenarios":{{"bear":{{"price":0,"return":"-X%","trigger":"brief"}},"base":{{"price":0,"return":"+X%","trigger":"brief"}},"bull":{{"price":0,"return":"+X%","trigger":"brief"}}}},"catalysts":[{{"horizon":"NEAR|MID|LONG","text":"catalyst","timing":"Q1 2026 etc","impact":"HIGH|MEDIUM|LOW|CONFIRMED"}}],"risks":[{{"sev":"🔴|🟡|🟢","risk":"name","prob":"HIGH|LOW","imp":"HIGH|LOW","detail":"1 line"}}],"exit_trigger":"what kills the thesis","key_edge":"single best reason to own it","watch_item":"main Q1 2026 watch","grade":"A+|A|A-|B+|B|B-|C|D|F","verdict":"1 sentence buy/sell verdict"}}"""

    try:
        import google.generativeai as genai
        r = model.generate_content(prompt)
        text = re.sub(r'```(?:json)?', '', r.text).strip().strip('`')
        result = json.loads(text)
        st.session_state.ai_cache[key] = result
        return result
    except Exception as e:
        return {"error": str(e)}

def ai_chat(model, q, ctx):
    if not model: return "⚠️  Add Gemini API key in the sidebar to use AI chat."
    try:
        import google.generativeai as genai
        sys_ctx = f"You are PYKUPZ AI — elite hedge fund analyst. 78-stock universe. Context: {ctx[:400]}. Be concise, data-driven, terminal-style. Max 200 words."
        msgs = [{"role":"user","parts":[sys_ctx]}]
        for h in st.session_state.chat_hist[-6:]:
            msgs.append({"role":h["role"],"parts":[h["content"]]})
        msgs.append({"role":"user","parts":[q]})
        r = model.generate_content(msgs)
        return r.text
    except Exception as e:
        return f"⚠️  Error: {e}"


# ══════════════════ UI COMPONENTS ════════════════════════════════

def card(val, label, accent='green', size=19):
    return f"""<div class="pyk-card {accent}">
<div class="pyk-val" style="font-size:{size}px">{val}</div>
<div class="pyk-lbl">{label}</div></div>"""

def sh(text, accent=''):
    cls = f'section-header {accent}'.strip()
    return f'<div class="{cls}">{text}</div>'

def data_row(key, val, val_color=None):
    vc = f' style="color:{val_color}"' if val_color else ''
    return f'<div class="data-row"><span class="data-key">{key}</span><span class="data-val"{vc}>{val}</span></div>'

# ── Sidebar ───────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="padding:14px 14px 8px;border-bottom:1px solid #1e2230">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:14px;font-weight:700;letter-spacing:3px;color:#00d97e">⚡ PYKUPZ</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158;margin-top:2px">INSTITUTIONAL TERMINAL · Q1 2026</div>
        </div>""", unsafe_allow_html=True)

        # Gemini key
        st.markdown('<div style="padding:10px 14px 4px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#4f8ef7">🤖 GEMINI AI</div></div>', unsafe_allow_html=True)
        key_in = st.text_input("##key", value=st.session_state.gemini_key,
            type="password", placeholder="AIza... (aistudio.google.com)",
            label_visibility="collapsed")
        if key_in != st.session_state.gemini_key:
            st.session_state.gemini_key = key_in
            st.session_state.ai_cache = {}
            st.cache_resource.clear()
        st.markdown(
            f'<div style="padding:0 14px 8px;font-family:IBM Plex Mono,monospace;font-size:9px;color:{"#00d97e" if key_in else "#f04444"}">{"● CONNECTED" if key_in else "● NO KEY"}</div>',
            unsafe_allow_html=True)

        # Nav
        st.markdown('<div style="padding:8px 14px 4px;border-top:1px solid #0d0f14"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#3a4158">NAVIGATION</div></div>', unsafe_allow_html=True)
        nav_items = [('📊  PORTFOLIO OVERVIEW','portfolio'), ('🚀  ANTIGRAVITY SCANNER','scanner'), ('💬  AI CHAT','chat')]
        for lbl, view in nav_items:
            active = st.session_state.main_view == view
            if st.button(lbl, key=f"nav_{view}", use_container_width=True):
                st.session_state.main_view = view
                st.rerun()

        # Search
        st.markdown('<div style="padding:8px 14px 4px;border-top:1px solid #0d0f14"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:2px;color:#3a4158">STOCK UNIVERSE · 78 STOCKS</div></div>', unsafe_allow_html=True)
        srch = st.text_input("##search", placeholder="Search ticker or name...", label_visibility="collapsed")
        rf = st.selectbox("##recf", ["All","Buy","Watch","Hold","Sell"], label_visibility="collapsed")
        filtered = ALL_STOCKS
        if srch:
            s2 = srch.upper()
            filtered = [x for x in filtered if s2 in x['ticker'].upper() or s2 in x['name'].upper()]
        if rf != "All":
            filtered = [x for x in filtered if rf.lower() in str(x.get('recommendation','')).lower()]

        st.markdown(f'<div style="padding:0 14px 2px;font-family:IBM Plex Mono,monospace;font-size:8px;color:#3a4158">{len(filtered)} stocks</div>', unsafe_allow_html=True)

        # Stock list
        for s in filtered:
            t = s['ticker']
            rec = str(s.get('recommendation','')).strip()
            pts = s.get('points') or s.get('reconcile') or 0
            active = t == st.session_state.ticker
            btn_label = f"**{t}**  ·  {s['name'][:18]}"
            if st.button(btn_label, key=f"sb_{t}", use_container_width=True):
                st.session_state.ticker = t
                st.session_state.main_view = 'stock'
                st.rerun()

        st.markdown(f'<div style="padding:10px 14px;border-top:1px solid #0d0f14;font-family:IBM Plex Mono,monospace;font-size:8px;color:#3a4158">AI cache: {len(st.session_state.ai_cache)} · {datetime.now().strftime("%H:%M")}</div>', unsafe_allow_html=True)

# ── Stock tear sheet ──────────────────────────────────────────────
def render_stock(ticker):
    s = next((x for x in ALL_STOCKS if x['ticker']==ticker), None)
    if not s:
        st.error(f"Stock {ticker} not found.")
        return

    # Fetch live
    price_live, chg_live = live_price(ticker)
    price = price_live or float(s.get('price') or 0)
    chg   = chg_live or 0
    info  = live_info(ticker)

    # AI analysis (if model available)
    model = get_model()
    ai = None
    if model:
        key = f"ai_{ticker}"
        if key not in st.session_state.ai_cache:
            with st.spinner(f"🤖  Analysing {ticker} with Gemini..."):
                ai = ai_analyze(model, s, price, chg, info)
        else:
            ai = st.session_state.ai_cache[key]

    # ─ Stock header ─
    color = '#00d97e' if chg >= 0 else '#f04444'
    arr   = '▲' if chg >= 0 else '▼'
    rec   = str(s.get('recommendation','')).strip()
    ath_r = s.get('ath_retrace')
    ath_txt = f"{float(ath_r)*100:.1f}% from ATH" if ath_r else ''

    st.markdown(f"""
    <div class="pyk-header">
      <div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{color};letter-spacing:2px">{ticker}</span>
          <span style="font-family:'IBM Plex Sans',sans-serif;font-size:13px;color:#6b7691;font-weight:400">{s['name']}</span>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:9px;background:#1a1d26;border:1px solid #2a2f40;border-radius:2px;padding:1px 7px;color:#6b7691">{SECTORS.get(ticker,'—')}</span>
          {f'<span class="sig {SIG_CSS.get(rec, "sig-watch")}">{rec.upper()}</span>' if rec else ''}
        </div>
        <div style="display:flex;align-items:baseline;gap:14px;margin-top:6px">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:24px;font-weight:600;color:#f0f4ff">${price:,.2f}</span>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:{color}">{arr} {abs(chg*100):.2f}%</span>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#3a4158">{ath_txt}</span>
        </div>
      </div>
      <div style="text-align:right">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:700;color:#f0f4ff">{s.get('points','—')}<span style="font-size:10px;color:#3a4158">/10</span></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158">PYKUPZ SCORE</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ─ Key metric strip ─
    metrics = [
        (fv(s.get('pe')), 'PE TTM', 'amber'),
        (fv(s.get('ps')), 'P/S', ''),
        (fn(s.get('mcap_b'), suffix='B'), 'Market Cap', 'blue'),
        (fp(s.get('rev_growth_ly')), 'Rev Growth LY', 'green' if (s.get('rev_growth_ly') or 0)>0.15 else ''),
        (fp(s.get('rev_3y_cagr')), 'Rev 3Y CAGR', 'green'),
        (fp(s.get('eps_3y_cagr')), 'EPS 3Y CAGR', 'green'),
        (fn(s.get('fcf_ttm'), suffix='M', dec=0), 'FCF TTM', 'green' if (s.get('fcf_ttm') or 0) > 0 else 'red'),
        (fn(s.get('eps_2026e'), prefix='$', suffix='', dec=2), 'EPS 2026E', 'cyan'),
    ]
    cols = st.columns(8)
    for col, (val, lbl, acc) in zip(cols, metrics):
        col.markdown(card(val, lbl, acc, 16), unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ─ TABS ─
    tab_list = ["📋  Overview","📐  Valuation","📈  Growth","🏰  Moat","🎯  Scenarios",
                "⚠️  Risk","💼  Decision","📉  Charts"]
    tabs = st.tabs(tab_list)

    # ══ OVERVIEW TAB ══
    with tabs[0]:
        if ai and 'error' not in ai:
            c_l, c_r = st.columns([2, 1])
            with c_l:
                sig = ai.get('signal','—')
                sig_clr = SIG_CLR.get(sig, '#f5a623')
                st.markdown(f"""
                <div class="ai-panel">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                    <span class="ai-badge">GEMINI · INSTITUTIONAL ANALYSIS</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a4158">{ticker} · {SECTORS.get(ticker,'')}</span>
                  </div>
                  <div style="font-family:'IBM Plex Sans',sans-serif;font-size:12px;line-height:1.75;color:#c8d0e0;margin-bottom:10px">{ai.get('thesis','—')}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#f5a623;margin-bottom:10px">{ai.get('why_now','')}</div>
                  <div style="padding:8px 12px;background:#08090d;border-left:2px solid #4f8ef7;border-radius:0 2px 2px 0">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#3a4158;letter-spacing:2px;margin-bottom:3px">MOAT IN ONE LINE</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4f8ef7;font-style:italic">"{ai.get('moat_summary','—')}"</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                with b1:
                    st.markdown(sh('🟢  Bull Case', 'green'), unsafe_allow_html=True)
                    for pt in ai.get('bull_case',[]):
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;padding:4px 0;border-bottom:1px solid #0d0f14;color:#6b7691">✦ {pt}</div>', unsafe_allow_html=True)
                with b2:
                    st.markdown(sh('🔴  Bear Case'), unsafe_allow_html=True)
                    for pt in ai.get('bear_case',[]):
                        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;padding:4px 0;border-bottom:1px solid #0d0f14;color:#6b7691">⚑ {pt}</div>', unsafe_allow_html=True)

            with c_r:
                grade = ai.get('grade','—')
                conv  = int(ai.get('conviction',3))
                risk  = ai.get('risk_score',50)
                ag    = ai.get('antigravity_score',50)
                ag_c  = '#00d97e' if ag>=70 else '#f5a623' if ag>=40 else '#f04444'
                st.markdown(f"""
                <div class="pyk-card" style="text-align:center;border-color:{sig_clr}44;border-top:2px solid {sig_clr};padding:16px">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158">AI SIGNAL</div>
                  <div style="font-family:'IBM Plex Sans',sans-serif;font-size:17px;font-weight:700;color:{sig_clr};margin:5px 0">{sig}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158;margin-top:10px">GRADE</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:32px;font-weight:700;color:#22d3ee;line-height:1.1">{grade}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158;margin-top:10px">CONVICTION</div>
                  <div style="color:#f5a623;font-size:14px;letter-spacing:2px">{"★"*conv}{"☆"*(5-conv)}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158;margin-top:10px">RISK SCORE</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;color:#f04444">{risk}<span style="font-size:10px">/100</span></div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158;margin-top:10px">ANTIGRAVITY</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;color:{ag_c};font-weight:700">{ag}<span style="font-size:10px;color:#3a4158">/100</span></div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#3a4158;margin-top:3px;line-height:1.4">{ai.get('antigravity_reason','')[:70]}</div>
                </div>
                <div class="pyk-card" style="margin-top:6px">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158">3Y BASE TARGET</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:700;color:#00d97e">{ai.get('target_3y','—')}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#00d97e">{ai.get('return_3y','—')}  ·  {ai.get('pa','—')}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#3a4158;margin-top:4px">ENTRY</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#c8d0e0">{ai.get('entry_price','—')}</div>
                </div>""", unsafe_allow_html=True)

            for section, icon, color_key in [
                ('key_edge','⚡ KEY EDGE','#00d97e'),
                ('watch_item','👁  WATCH ITEM','#f5a623'),
                ('verdict','📌  VERDICT','#4f8ef7')
            ]:
                txt = ai.get(section,'')
                if txt:
                    st.markdown(f"""
                    <div style="background:#08090d;border:1px solid #1e2230;border-left:2px solid {color_key};border-radius:3px;padding:10px 14px;margin-top:5px">
                      <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:{color_key};margin-bottom:4px">{icon}</div>
                      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#6b7691;line-height:1.6">{txt}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            # No AI — raw Excel data display
            st.markdown('<div style="padding:12px 0">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(sh('📋  Raw Portfolio Data'), unsafe_allow_html=True)
                rows_data = [
                    ('Price', f"${price:,.2f}"), ('ATH', fn(s.get('high'), prefix='$', suffix='')),
                    ('ATH Retrace', fp(s.get('ath_retrace'))),
                    ('PE (TTM)', fv(s.get('pe'))), ('P/S', fv(s.get('ps'))),
                    ('Market Cap', fn(s.get('mcap_b'), suffix='B')),
                    ('Price Follows', s.get('price_follows','—')),
                    ('Score', f"{s.get('points','—')}/10"),
                ]
                st.markdown(''.join(data_row(k,v) for k,v in rows_data), unsafe_allow_html=True)
            with c2:
                st.markdown(sh('📊  Growth Metrics'), unsafe_allow_html=True)
                rows_g = [
                    ('Revenue LY', fn(s.get('rev_ly'), suffix='M', dec=0)),
                    ('Rev Growth LY', fp(s.get('rev_growth_ly'))),
                    ('Rev 3Y CAGR', fp(s.get('rev_3y_cagr'))),
                    ('Rev 2026E', fn(s.get('rev_2026e'), suffix='M', dec=0)),
                    ('EBITDA LY', fn(s.get('ebitda_ly'), suffix='M', dec=0)),
                    ('EPS LY', fn(s.get('eps_ly'), prefix='$', suffix='', dec=2)),
                    ('EPS 2026E', fn(s.get('eps_2026e'), prefix='$', suffix='', dec=2)),
                    ('FCF TTM', fn(s.get('fcf_ttm'), suffix='M', dec=0)),
                ]
                st.markdown(''.join(data_row(k,v) for k,v in rows_g), unsafe_allow_html=True)
            st.info("💡  Add your Gemini API key in the sidebar to unlock AI thesis, moat analysis, scenarios, risk matrix, and trade decision for all 78 stocks.")

    # ══ VALUATION TAB ══
    with tabs[1]:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(sh('📐  Valuation Dashboard'), unsafe_allow_html=True)
            fpe = info.get('forwardPE'); pb = info.get('priceToBook'); peg = info.get('trailingPegRatio')
            val_items = [
                ('PE (TTM)', fv(s.get('pe')), '#f5a623'),
                ('Forward PE', fv(fpe), '#f5a623'),
                ('P/S', fv(s.get('ps')), '#22d3ee'),
                ('P/B', fv(pb), None),
                ('PEG Ratio', f"{float(peg):.2f}" if peg else '—', None),
                ('Market Cap', fn(s.get('mcap_b'), suffix='B'), '#4f8ef7'),
                ('ATH', fn(s.get('high'), prefix='$', suffix='', dec=2), None),
                ('ATH Retrace', fp(s.get('ath_retrace')), '#f04444' if (s.get('ath_retrace') or 0)<-0.2 else None),
                ('GAPS (P/S model)', fv(s.get('gaps')), '#22d3ee'),
                ('GAPE (P/E model)', fv(s.get('gape')), '#f5a623'),
                ('Score /10', f"{s.get('points','—')}", '#00d97e'),
                ('Hypothesis Price', s.get('hypothesis_price','—'), '#00d97e'),
            ]
            st.markdown(''.join(data_row(k, v, vc) for k,v,vc in val_items), unsafe_allow_html=True)

        with c2:
            fig_gg = chart_gaps_gape(ticker, s)
            if fig_gg: st.plotly_chart(fig_gg, use_container_width=True)
            # PE/PS bar
            mult_data = {'Multiple': ['PE (TTM)', 'Fwd PE', 'P/S', 'GAPS (P/S)', 'GAPE (P/E)'],
                         'Value': [s.get('pe'), fpe, s.get('ps'), s.get('gaps'), s.get('gape')]}
            mdf = [(k, float(v)) for k,v in zip(mult_data['Multiple'], mult_data['Value'])
                   if v and str(v) not in ('nan','None') and float(v) > 0]
            if mdf:
                clrs = ['#f5a623','#f5a623','#22d3ee','#22d3ee','#f5a623']
                fig_m = go.Figure(go.Bar(
                    x=[k for k,v in mdf], y=[v for k,v in mdf],
                    marker_color=clrs[:len(mdf)], marker_line_width=0,
                    text=[f"{v:.1f}x" for k,v in mdf], textposition='outside',
                    textfont=dict(size=9, color='#6b7691')
                ))
                chart_theme(fig_m, f'Valuation Multiples — {ticker}', h=220)
                st.plotly_chart(fig_m, use_container_width=True)

    # ══ GROWTH TAB ══
    with tabs[2]:
        # Growth metrics strip
        grow_metrics = [
            (fp(s.get('rev_growth_ly')), 'Rev Growth LY', 'green' if (s.get('rev_growth_ly') or 0)>0.2 else ''),
            (fp(s.get('rev_3y_cagr')), 'Rev 3Y CAGR', 'green'),
            (fn(s.get('rev_2026e'), suffix='M', dec=0), 'Rev 2026E', 'cyan'),
            (fp(s.get('ebitda_3y_cagr')), 'EBITDA 3Y CAGR', 'amber'),
            (fn(s.get('ebitda_2026e'), suffix='M', dec=0), 'EBITDA 2026E', ''),
            (fp(s.get('eps_3y_cagr')), 'EPS 3Y CAGR', 'green'),
            (fn(s.get('eps_2026e'), prefix='$', suffix='', dec=2), 'EPS 2026E', 'cyan'),
            (fn(s.get('eps_2027e'), prefix='$', suffix='', dec=2), 'EPS 2027E', ''),
        ]
        cols = st.columns(8)
        for col, (val, lbl, acc) in zip(cols, grow_metrics):
            col.markdown(card(val, lbl, acc, 14), unsafe_allow_html=True)

        fin = live_financials(ticker)
        c1, c2 = st.columns(2)
        with c1:
            fig_rf = chart_rev_fcf(ticker, fin, s)
            if fig_rf: st.plotly_chart(fig_rf, use_container_width=True)
        with c2:
            fig_eps = chart_eps(ticker, s, fin)
            if fig_eps: st.plotly_chart(fig_eps, use_container_width=True)
        fig_fd = chart_fcf_net_debt(ticker, s)
        if fig_fd: st.plotly_chart(fig_fd, use_container_width=True)

        # Score breakdown
        st.markdown(sh('🎯  Pykupz Score Breakdown'), unsafe_allow_html=True)
        score_cols = st.columns(6)
        score_items = [
            ('Rev Growth', s.get('rev_score'), '#00d97e'),
            ('EPS', s.get('eps_score'), '#00d97e'),
            ('EBITDA', s.get('ebitda_score'), '#f5a623'),
            ('Cashflow', s.get('cashflow_score'), '#22d3ee'),
            ('Net Debt', s.get('net_debt_score'), '#4f8ef7'),
            ('Factor Adj', s.get('factor_adj'), '#a78bfa'),
        ]
        for col, (lbl, val, acc) in zip(score_cols, score_items):
            v_txt = f"{float(val):.0f}/10" if val and str(val) not in ('nan','None') else '—'
            col.markdown(card(v_txt, lbl, '', 15), unsafe_allow_html=True)

    # ══ MOAT TAB ══
    with tabs[3]:
        if ai and 'error' not in ai and ai.get('moat_layers'):
            st.markdown(f"""
            <div style="background:#08090d;border:1px solid rgba(79,142,247,0.25);border-radius:4px;padding:12px 16px;margin-bottom:12px">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#4f8ef7;margin-bottom:5px">MOAT SUMMARY</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#4f8ef7;font-style:italic">"{ai.get('moat_summary','—')}"</div>
            </div>""", unsafe_allow_html=True)
            for m in ai.get('moat_layers', []):
                n = int(m.get('stars', 3))
                v = m.get('verdict','—')
                vcl = '#00d97e' if 'UNASS' in v else '#22d3ee' if 'FORT' in v else '#f5a623' if 'STRUCT' in v else '#6b7691'
                st.markdown(f"""
                <div class="moat-card">
                  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#c8d0e0;font-weight:600;flex:1">{m.get('layer','—')}</div>
                    <div style="color:#f5a623;font-size:12px;letter-spacing:2px;margin:0 10px">{"★"*n}{"☆"*(5-n)}</div>
                    <span style="background:{vcl}18;border:1px solid {vcl}44;color:{vcl};font-family:'IBM Plex Mono',monospace;font-size:8px;padding:1px 7px;border-radius:2px">{v}</span>
                  </div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a4158;font-style:italic">{m.get('detail','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(sh('🏰  Moat Indicators'), unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#6b7691;line-height:2">
              • Sector: <span style="color:#c8d0e0">{SECTORS.get(ticker,'Unknown')}</span><br>
              • Price Driver: <span style="color:#c8d0e0">{s.get('price_follows','—')}</span><br>
              • Rev 3Y CAGR: <span style="color:#00d97e">{fp(s.get('rev_3y_cagr'))}</span><br>
              • FCF TTM: <span style="color:#22d3ee">{fn(s.get('fcf_ttm'), suffix='M', dec=0)}</span><br>
              • Net Debt TTM: <span style="color:{'#f04444' if (s.get('net_debt_ttm') or 0)>0 else '#00d97e'}">{fn(s.get('net_debt_ttm'), suffix='M', dec=0)}</span>
            </div>""", unsafe_allow_html=True)
            st.info("🤖  Add Gemini key to generate detailed moat architecture with ★★★★★ ratings.")

    # ══ SCENARIOS TAB ══
    with tabs[4]:
        if ai and 'error' not in ai and ai.get('scenarios'):
            sc = ai['scenarios']
            c1, c2, c3 = st.columns(3)
            for col, key, lbl, css in [(c1,'bear','🐻  BEAR','.sc-bear'),(c2,'base','📊  BASE','.sc-base'),(c3,'bull','🐂  BULL','.sc-bull')]:
                d = sc.get(key, {}); p = d.get('price',0); r = d.get('return','—'); t = d.get('trigger','—')
                div_cls = css.replace('.','')
                with col:
                    st.markdown(f"""
                    <div class="{div_cls}">
                      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:600;margin-bottom:8px">{lbl}</div>
                      <div style="font-family:'IBM Plex Sans',sans-serif;font-size:26px;font-weight:700;margin-bottom:4px">${float(p):,.0f}</div>
                      <div style="font-family:'IBM Plex Mono',monospace;font-size:14px;margin-bottom:14px">{r}</div>
                      <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#6b7691;text-align:left;line-height:1.6">{t}</div>
                    </div>""", unsafe_allow_html=True)

            if ai.get('catalysts'):
                st.markdown(sh('⚡  Catalyst Timeline'), unsafe_allow_html=True)
                for c in ai.get('catalysts',[]):
                    h_str = c.get('horizon','MID')
                    tl_cls = {'NEAR':'tl-near','MID':'tl-mid','LONG':'tl-long'}.get(h_str,'tl-long')
                    imp = c.get('impact','MEDIUM')
                    ic = '#00d97e' if imp=='CONFIRMED' else '#f04444' if imp=='HIGH' else '#f5a623' if imp=='MEDIUM' else '#3a4158'
                    st.markdown(f"""
                    <div class="tl-item {tl_cls}">
                      <div style="display:flex;align-items:center;justify-content:space-between">
                        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#c8d0e0;flex:1">{c.get('text','')}</span>
                        <span style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#3a4158;margin:0 10px">{c.get('timing','')}</span>
                        <span style="background:{ic}15;border:1px solid {ic}40;color:{ic};font-family:'IBM Plex Mono',monospace;font-size:7px;padding:1px 5px;border-radius:2px">{imp}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
        else:
            hyp = s.get('hypothesis_price','')
            st.markdown(sh('🎯  Hypothesis Price Range'), unsafe_allow_html=True)
            if hyp:
                st.markdown(f'<div style="background:#08090d;border:1px solid rgba(0,217,126,0.2);border-radius:3px;padding:12px 16px;font-family:IBM Plex Mono,monospace;font-size:10px;color:#00d97e;line-height:1.7">{hyp}</div>', unsafe_allow_html=True)
            st.info("🤖  Add Gemini key to generate Bear/Base/Bull scenarios and catalyst timeline.")

    # ══ RISK TAB ══
    with tabs[5]:
        if ai and 'error' not in ai and ai.get('risks'):
            qs = [('HIGH PROB / HIGH IMPACT','HIGH','HIGH','rq-hihi','#f04444'),
                  ('HIGH PROB / LOW IMPACT','HIGH','LOW','rq-hilo','#f5a623'),
                  ('LOW PROB / HIGH IMPACT','LOW','HIGH','rq-lohi','#f5a623'),
                  ('LOW PROB / LOW IMPACT','LOW','LOW','rq-lolo','#00d97e')]
            cols = st.columns(2)
            for i, (lbl, prob, imp, css, bc) in enumerate(qs):
                items = [r for r in ai['risks'] if r.get('prob')==prob and r.get('imp')==imp]
                with cols[i%2]:
                    html = f'<div class="{css}" style="margin-bottom:8px"><div style="font-family:IBM Plex Mono,monospace;font-size:8px;letter-spacing:1px;color:{bc};margin-bottom:8px">{lbl}</div>'
                    if items:
                        for r in items:
                            sc2 = r.get('sev','🟡')
                            rc = '#f04444' if sc2=='🔴' else '#f5a623' if sc2=='🟡' else '#00d97e'
                            html += f'<div style="background:#08090d;border-radius:2px;padding:6px 8px;margin-bottom:4px;border-left:2px solid {rc}"><div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#c8d0e0">{sc2} {r.get("risk","")}</div><div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#3a4158;margin-top:2px">{r.get("detail","")}</div></div>'
                    else:
                        html += '<div style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#1e2230;font-style:italic">No items in this quadrant</div>'
                    html += '</div>'
                    st.markdown(html, unsafe_allow_html=True)
            # Beta + short
            beta = info.get('beta'); short = (info.get('shortPercentOfFloat') or 0)*100
            if beta or short:
                st.markdown(sh('📊  Market Risk Indicators'), unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                if beta: rc1.markdown(card(f"{float(beta):.2f}", "Beta (Market Sensitivity)", 'amber', 18), unsafe_allow_html=True)
                if short: rc2.markdown(card(f"{short:.1f}%", "Short Interest (Float)", 'red' if short > 15 else '', 18), unsafe_allow_html=True)
        else:
            st.info("🤖  Add Gemini key to generate Risk Matrix (Probability × Impact).")

    # ══ DECISION TAB ══
    with tabs[6]:
        if ai and 'error' not in ai:
            sig = ai.get('signal','—'); sig_clr2 = SIG_CLR.get(sig,'#f5a623')
            conv2 = int(ai.get('conviction',3)); grade2 = ai.get('grade','—')
            c_d, c_e = st.columns([1, 1])
            with c_d:
                st.markdown(f"""
                <div style="background:#08090d;border:2px solid {sig_clr2}55;border-radius:5px;padding:18px">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:#3a4158;margin-bottom:6px">INVESTMENT DECISION</div>
                  {"".join([f'<div style="display:flex;justify-content:space-between;border-bottom:1px solid #0d0f14;padding:7px 0"><span style="font-family:IBM Plex Mono,monospace;font-size:8px;color:#3a4158;letter-spacing:1px">{k}</span><span style="font-family:IBM Plex Mono,monospace;font-size:{sz}px;color:{vc};font-weight:{wt}">{v}</span></div>'
                  for k,v,vc,sz,wt in [
                    ('SIGNAL', sig, sig_clr2, 14, 700),
                    ('GRADE', grade2, '#22d3ee', 18, 700),
                    ('CONVICTION', '★'*conv2+'☆'*(5-conv2), '#f5a623', 14, 400),
                    ('ENTRY PRICE', ai.get('entry_price','—'), sig_clr2, 13, 600),
                    ('3Y TARGET', ai.get('target_3y','—'), '#00d97e', 13, 600),
                    ('3Y RETURN', ai.get('return_3y','—'), '#00d97e', 13, 600),
                    ('P.A. RETURN', ai.get('pa','—'), '#00d97e', 11, 400),
                    ('RISK SCORE', f"{ai.get('risk_score',50)}/100", '#f04444', 11, 400),
                    ('ANTIGRAVITY', f"{ai.get('antigravity_score',50)}/100", '#a78bfa', 11, 400),
                  ]])}
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:{sig_clr2};margin-top:8px">VERDICT</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:{sig_clr2};line-height:1.6;margin-top:4px">{ai.get('verdict','—')}</div>
                </div>""", unsafe_allow_html=True)
            with c_e:
                for section, icon, bc2 in [
                    ('key_edge','⚡ KEY EDGE','#00d97e'),
                    ('exit_trigger','🚪 EXIT TRIGGER','#f04444'),
                    ('watch_item','👁  WATCH ITEM','#f5a623'),
                ]:
                    txt = ai.get(section,'')
                    if txt:
                        st.markdown(f"""
                        <div style="background:#08090d;border:1px solid {bc2}22;border-left:2px solid {bc2};border-radius:3px;padding:10px 14px;margin-bottom:6px">
                          <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:2px;color:{bc2};margin-bottom:4px">{icon}</div>
                          <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#6b7691;line-height:1.6">{txt}</div>
                        </div>""", unsafe_allow_html=True)
        else:
            st.markdown(sh('💼  Decision Summary'), unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(card(rec or '—', 'Recommendation (Excel)', 'green', 16), unsafe_allow_html=True)
            pts_v = s.get('points') or s.get('reconcile')
            c2.markdown(card(f"{float(pts_v):.1f}/10" if pts_v else '—', 'Pykupz Score', 'cyan', 16), unsafe_allow_html=True)
            c3.markdown(card(s.get('hypothesis_price','—') or '—', 'Hypothesis Price', '', 12), unsafe_allow_html=True)
            st.info("🤖  Add Gemini key for full decision box: entry, target, exit trigger, key edge, grade A+→F.")

    # ══ CHARTS TAB ══
    with tabs[7]:
        hist5 = live_history(ticker, "5y")
        fig_p = chart_price(ticker, hist5)
        if fig_p: st.plotly_chart(fig_p, use_container_width=True)
        else: st.info(f"Price chart unavailable for {ticker}")
        hist1 = live_history(ticker, "1y")
        if not hist1.empty:
            fig1 = chart_price(ticker, hist1)
            if fig1:
                fig1.update_layout(title=dict(text=f'Price & Volume — {ticker}  (1 Year)'))
                st.plotly_chart(fig1, use_container_width=True)
        if model and ai and 'error' not in ai:
            if st.button(f"🔄  Re-analyse {ticker} with Gemini"):
                del st.session_state.ai_cache[f"ai_{ticker}"]
                st.rerun()


# ══════════════════ PORTFOLIO OVERVIEW ═══════════════════════════

def render_portfolio():
    st.markdown("""
    <div class="pyk-header">
      <div>
        <div class="pyk-logo">⚡  PYKUPZ  ·  78-STOCK UNIVERSE</div>
        <div class="pyk-tagline">CITADEL GLOBAL EQUITIES  ·  FUNDAMENTAL RESEARCH  ·  Q1 2026  ·  CONFIDENTIAL</div>
      </div>
      <div style="text-align:right;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a4158">
        {dt}<br>MARCH 2026
      </div>
    </div>""".format(dt=datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)

    # Summary metrics
    total = len(ALL_STOCKS)
    buys  = sum(1 for s in ALL_STOCKS if 'buy' in str(s.get('recommendation','')).lower())
    watch = sum(1 for s in ALL_STOCKS if 'watch' in str(s.get('recommendation','')).lower())
    avg_pe = np.nanmean([float(s['pe']) for s in ALL_STOCKS if s.get('pe') and str(s.get('pe')) not in ('nan','None') and 0 < float(str(s['pe']).replace('Negative','')) < 500 if str(s.get('pe')) not in ('Negative',)])

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(card(total, 'Total Stocks', 'blue', 22), unsafe_allow_html=True)
    c2.markdown(card(buys, 'Buy Signals', 'green', 22), unsafe_allow_html=True)
    c3.markdown(card(watch, 'Watch', 'amber', 22), unsafe_allow_html=True)
    c4.markdown(card(len(st.session_state.ai_cache), 'AI Analyses', 'cyan', 22), unsafe_allow_html=True)
    c5.markdown(card(f"{avg_pe:.0f}x", 'Avg PE (Universe)', 'amber', 22), unsafe_allow_html=True)
    c6.markdown(card('Q1 2026', 'Research Date', '', 22), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Universe Map
    fig_map = chart_portfolio_map(ALL_STOCKS)
    if fig_map: st.plotly_chart(fig_map, use_container_width=True)

    # Master table
    st.markdown(sh('📋  Master Stock Table — All 78 Stocks'), unsafe_allow_html=True)
    rows = []
    for s in ALL_STOCKS:
        ai_s = st.session_state.ai_cache.get(f"ai_{s['ticker']}", {})
        pe_v = s.get('pe')
        try: pe_str = f"{float(pe_v):.1f}x" if pe_v and str(pe_v) not in ('nan','None','Negative') else '—'
        except: pe_str = '—'
        rows.append({
            '#': s.get('sr',''), 'Ticker': s['ticker'], 'Name': s['name'][:28],
            'Sector': SECTORS.get(s['ticker'],'—'),
            'PE': pe_str, 'PS': fv(s.get('ps')),
            'MCap ($B)': fn(s.get('mcap_b'), prefix='', suffix='', dec=1),
            'Price': fn(s.get('price'), suffix='', dec=2),
            'Rev Grw%': fp(s.get('rev_growth_ly')),
            'EPS CAGR': fp(s.get('eps_3y_cagr')),
            'FCF TTM ($M)': fn(s.get('fcf_ttm'), prefix='', suffix='', dec=0),
            'Score /10': f"{float(s.get('points',0)):.1f}" if s.get('points') else '—',
            'Rec (Excel)': str(s.get('recommendation','')).strip(),
            'AI Signal': ai_s.get('signal','—') if ai_s and 'error' not in ai_s else '—',
            'Grade': ai_s.get('grade','—') if ai_s and 'error' not in ai_s else '—',
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=580,
        column_config={
            '#': st.column_config.NumberColumn(width='small'),
            'Ticker': st.column_config.TextColumn(width='small'),
            'Score /10': st.column_config.TextColumn(width='small'),
        }
    )

    # Sector breakdown
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown(sh('🏭  Sector Breakdown'), unsafe_allow_html=True)
        sec_cnt = {}
        for s in ALL_STOCKS:
            sec = SECTORS.get(s['ticker'],'Other')
            sec_cnt[sec] = sec_cnt.get(sec,0) + 1
        sec_df = pd.DataFrame(list(sec_cnt.items()), columns=['Sector','Count']).sort_values('Count', ascending=True)
        fig_sec = go.Figure(go.Bar(
            x=sec_df['Count'], y=sec_df['Sector'], orientation='h',
            marker=dict(color=sec_df['Count'], colorscale=[[0,'#1a1d26'],[0.5,'#22d3ee'],[1,'#00d97e']]),
            text=sec_df['Count'], textposition='outside', textfont=dict(size=8, color='#6b7691')
        ))
        chart_theme(fig_sec, 'Stocks by Sector', h=380)
        st.plotly_chart(fig_sec, use_container_width=True)
    with c_s2:
        st.markdown(sh('📊  MCap Distribution'), unsafe_allow_html=True)
        mc_cnt = {}
        for s in ALL_STOCKS:
            mc_cnt[str(s.get('mcap_cat','Unknown')).strip() or 'Unknown'] = mc_cnt.get(str(s.get('mcap_cat','Unknown')).strip() or 'Unknown',0) + 1
        mc_df = pd.DataFrame(list(mc_cnt.items()), columns=['Category','Count'])
        fig_pie = go.Figure(go.Pie(
            labels=mc_df['Category'], values=mc_df['Count'], hole=0.45,
            marker_colors=['#00d97e','#22d3ee','#4f8ef7','#a78bfa','#f5a623','#f04444','#6b7691'],
            textfont=dict(family="'IBM Plex Mono',monospace", size=9, color='#c8d0e0'),
            hovertemplate='%{label}: %{value} stocks<extra></extra>'
        ))
        chart_theme(fig_pie, 'MCap Category Distribution', h=380)
        st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════ SCANNER ══════════════════════════════════════

def render_scanner():
    st.markdown("""
    <div class="pyk-header">
      <div>
        <div class="pyk-logo">🚀  ANTIGRAVITY SCANNER</div>
        <div class="pyk-tagline">AI IDENTIFIES STOCKS DEFYING MARKET GRAVITY  ·  Q1 2026</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    model = get_model()
    if not model:
        st.info("🤖  Add your Gemini API key in the sidebar to run the Antigravity Scanner.")
        return

    c1,c2,c3 = st.columns([2,1,1])
    with c1: n = st.slider("Stocks to scan", 5, 20, 10, label_visibility="visible")
    with c2: run = st.button("🚀  RUN SCAN", use_container_width=True)

    if run:
        sorted_s = sorted([s for s in ALL_STOCKS if s.get('points')],
                          key=lambda x: float(x.get('points',0)), reverse=True)[:n]
        prog = st.progress(0, text="Scanning...")
        for i, s in enumerate(sorted_s):
            t = s['ticker']
            if f"ai_{t}" not in st.session_state.ai_cache:
                p, ch = live_price(t); inf = live_info(t)
                ai_analyze(model, s, p or float(s.get('price',0)), ch or 0, inf)
            prog.progress((i+1)/len(sorted_s), text=f"Scanning {t}... {i+1}/{len(sorted_s)}")
        prog.empty()
        st.rerun()

    cached = [(k.replace('ai_',''), v) for k,v in st.session_state.ai_cache.items() if 'error' not in v]
    if cached:
        cached.sort(key=lambda x: x[1].get('antigravity_score',0), reverse=True)
        st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:8px;color:#3a4158;padding:4px 0'>{len(cached)} stocks analysed</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (t, ai_r) in enumerate(cached[:12]):
            s_d = next((s for s in ALL_STOCKS if s['ticker']==t), {})
            ag = ai_r.get('antigravity_score',0)
            sig = ai_r.get('signal','—'); grade = ai_r.get('grade','—')
            sig_c = SIG_CLR.get(sig,'#f5a623')
            ag_c = '#00d97e' if ag>=70 else '#f5a623' if ag>=40 else '#f04444'
            with cols[i%3]:
                st.markdown(f"""
                <div style="background:#08090d;border:1px solid {ag_c}33;border-top:2px solid {ag_c};border-radius:4px;padding:14px;margin-bottom:8px">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:16px;font-weight:700;color:{ag_c}">{t}</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a4158">{SECTORS.get(t,'')[:18]}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                    <div><div style="font-family:'IBM Plex Mono',monospace;font-size:28px;color:{ag_c};line-height:1;font-weight:700">{ag}</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:7px;color:#3a4158;letter-spacing:1px">ANTIGRAVITY</div></div>
                    <div style="text-align:right">
                      <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:{sig_c}">{sig}</div>
                      <div style="font-family:'IBM Plex Sans',sans-serif;font-size:22px;font-weight:700;color:#22d3ee">{grade}</div>
                    </div>
                  </div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#3a4158;line-height:1.5">{ai_r.get('antigravity_reason','')[:90]}</div>
                  <div style="margin-top:6px">
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#00d97e">{ai_r.get('target_3y','—')}</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#3a4158"> target · </span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:8px;color:#00d97e">{ai_r.get('return_3y','—')}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Open {t}", key=f"scan_open_{t}", use_container_width=True):
                    st.session_state.ticker = t
                    st.session_state.main_view = 'stock'
                    st.rerun()

# ══════════════════ CHAT ═════════════════════════════════════════

def render_chat():
    st.markdown("""
    <div class="pyk-header">
      <div>
        <div class="pyk-logo">💬  GEMINI AI CHAT</div>
        <div class="pyk-tagline">ASK ANYTHING ABOUT THE 78-STOCK UNIVERSE</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    model = get_model()
    for h in st.session_state.chat_hist[-12:]:
        ic = "🤖" if h['role']=='model' else "👤"
        bg = '#08090d' if h['role']=='model' else '#0d0f14'
        bc = 'rgba(79,142,247,0.25)' if h['role']=='model' else '#1e2230'
        st.markdown(f"""<div style="background:{bg};border:1px solid {bc};border-radius:4px;padding:10px 14px;margin-bottom:6px;font-family:'IBM Plex Mono',monospace;font-size:10px;line-height:1.7;color:#c8d0e0">{ic}  {h['content']}</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([5,1])
    with c1:
        q = st.text_input("##chatq",
            placeholder="e.g. Compare NVDA vs AMD · Is MELI cheap? · Which stocks have best FCF yield? · Explain CRM moat",
            label_visibility="collapsed")
    with c2:
        clear = st.button("Clear", use_container_width=True)
    if clear:
        st.session_state.chat_hist = []
        st.rerun()
    if q:
        ctx = f"Selected: {st.session_state.ticker}. Analysed: {list(st.session_state.ai_cache.keys())[:6]}. Universe: 78 stocks Q1 2026."
        with st.spinner("🤖"):
            reply = ai_chat(model, q, ctx)
        st.session_state.chat_hist.append({'role':'user','content':q})
        st.session_state.chat_hist.append({'role':'model','content':reply})
        st.rerun()

# ══════════════════ TICKER TAPE ══════════════════════════════════

def render_tape():
    """Top ticker tape showing all stocks."""
    items = []
    for s in ALL_STOCKS[:30]:
        price = s.get('price', 0)
        chg = s.get('ath_retrace', 0) or 0
        cls = 'tick-up' if chg >= 0 else 'tick-dn'
        arr = '▲' if chg >= 0 else '▼'
        items.append(f'<span class="tick-item {cls}">{s["ticker"]}  ${float(price):,.2f}</span>')
    tape = ''.join(items) * 2
    st.markdown(f'<div class="ticker-tape"><div class="ticker-inner">{tape}</div></div>', unsafe_allow_html=True)

# ══════════════════ MAIN ═════════════════════════════════════════

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
