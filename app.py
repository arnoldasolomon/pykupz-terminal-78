"""
PYKUPZ LIVE TERMINAL v5 — 78-Stock Universe
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full institutional-grade research terminal for all 78 stocks from Pyk-Inv-List.
Powered by live yfinance data + Gemini AI analysis.

GitHub: Upload this file + requirements.txt + stocks_data.json
Streamlit Cloud: Set GEMINI_API_KEY in Secrets
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import json, os, re, time
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PYKUPZ TERMINAL — 78 Stocks",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DARK THEME CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
:root{
  --bg:#000;--bg1:#080808;--bg2:#0f0f0f;--bg3:#161616;
  --bd:#252525;--bd2:#333;
  --green:#00FF41;--red:#FF3030;--amber:#FFB800;
  --cyan:#00e5ff;--pu:#b06bff;--pk:#ff6b9d;
  --white:#e8e8e8;--gray:#666;
  --fm:'JetBrains Mono',monospace;--fs:'Space Grotesk',sans-serif;
}
html,body,[class*="css"]{background:#000!important;color:#e8e8e8!important}
.main{background:#000!important}
.block-container{padding:0.5rem 1rem 2rem!important;max-width:100%!important;background:#000!important}

/* Sidebar */
section[data-testid="stSidebar"]{background:#080808!important;border-right:1px solid #252525!important}
section[data-testid="stSidebar"] *{color:#e8e8e8!important}

/* Metric cards */
div[data-testid="metric-container"]{background:#0f0f0f!important;border:1px solid #252525!important;border-radius:4px!important;padding:8px 12px!important}
div[data-testid="metric-container"] label{color:#666!important;font-family:'JetBrains Mono',monospace!important;font-size:10px!important;letter-spacing:1px!important}
div[data-testid="metric-container"] div{color:#e8e8e8!important;font-family:'JetBrains Mono',monospace!important}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:#080808!important;border-bottom:1px solid #252525!important}
.stTabs [data-baseweb="tab"]{color:#666!important;font-family:'JetBrains Mono',monospace!important;font-size:10px!important;letter-spacing:1px!important}
.stTabs [aria-selected="true"]{color:#00FF41!important;border-bottom:2px solid #00FF41!important}

/* Dataframe */
.stDataFrame{background:#0f0f0f!important}
iframe[title="st.iframe"]{background:#000!important}

/* Selectbox, text input */
.stSelectbox>div>div,.stTextInput input,.stTextArea textarea,.stMultiSelect>div{
  background:#0f0f0f!important;border-color:#252525!important;color:#e8e8e8!important;
  font-family:'JetBrains Mono',monospace!important;font-size:11px!important}

/* Buttons */
.stButton button{background:transparent!important;border:1px solid #00FF41!important;
  color:#00FF41!important;font-family:'JetBrains Mono',monospace!important;
  font-size:10px!important;letter-spacing:1px!important}
.stButton button:hover{background:rgba(0,255,65,0.1)!important}

/* Expander */
details{background:#0f0f0f!important;border:1px solid #252525!important;border-radius:3px!important}
.streamlit-expanderHeader{color:#00FF41!important;font-family:'JetBrains Mono',monospace!important;font-size:11px!important}

/* Scrollbar */
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:#000}
::-webkit-scrollbar-thumb{background:#333;border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:#00FF41}

/* Progress bar */
.stProgress .st-bo{background:#00FF41!important}

/* Custom components */
.pyk-header{background:#080808;border-bottom:2px solid #00FF41;padding:10px 16px;margin-bottom:12px}
.pyk-logo{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;letter-spacing:3px;color:#00FF41}
.pyk-sub{font-family:'JetBrains Mono',monospace;font-size:8px;color:#444;letter-spacing:2px;margin-top:2px}
.pyk-clock{font-family:'JetBrains Mono',monospace;font-size:16px;color:#00FF41;text-align:right}
.metric-card{background:#0f0f0f;border:1px solid #252525;border-radius:3px;padding:10px 14px;margin:3px 0}
.metric-card.green{border-top:2px solid #00FF41}
.metric-card.red{border-top:2px solid #FF3030}
.metric-card.amber{border-top:2px solid #FFB800}
.metric-card.cyan{border-top:2px solid #00e5ff}
.metric-card.pu{border-top:2px solid #b06bff}
.metric-val{font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:600;color:#e8e8e8}
.metric-lbl{font-family:'JetBrains Mono',monospace;font-size:8px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-top:2px}
.sh{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:3px;color:#00FF41;
  border-bottom:1px solid #252525;padding-bottom:4px;margin:10px 0 8px;text-transform:uppercase}
.tag{display:inline-block;border-radius:2px;padding:1px 6px;font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.5px;margin:1px}
.tag-buy{background:rgba(0,255,65,0.15);border:1px solid rgba(0,255,65,0.4);color:#00FF41}
.tag-sell{background:rgba(255,48,48,0.15);border:1px solid rgba(255,48,48,0.4);color:#FF3030}
.tag-watch{background:rgba(255,184,0,0.15);border:1px solid rgba(255,184,0,0.4);color:#FFB800}
.tag-hold{background:rgba(0,229,255,0.15);border:1px solid rgba(0,229,255,0.4);color:#00e5ff}
.stock-row{display:flex;align-items:center;padding:5px 8px;border-bottom:1px solid #1a1a1a;cursor:pointer;transition:background 0.1s}
.stock-row:hover{background:#161616}
.gem-panel{background:linear-gradient(135deg,#020810,#0a0f20);border:1px solid rgba(66,133,244,0.35);
  border-radius:6px;padding:14px;margin:6px 0;position:relative}
.gem-panel::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#4285f4,#34a853,#fbbc04,#ea4335);border-radius:6px 6px 0 0}
.gem-title{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;
  background:linear-gradient(90deg,#4285f4,#34a853);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px}
.risk-hi-hi{background:rgba(255,48,48,0.08);border:1px solid rgba(255,48,48,0.25);border-radius:3px;padding:10px}
.risk-hi-lo{background:rgba(255,184,0,0.06);border:1px solid rgba(255,184,0,0.25);border-radius:3px;padding:10px}
.risk-lo-hi{background:rgba(255,184,0,0.06);border:1px solid rgba(255,184,0,0.25);border-radius:3px;padding:10px}
.risk-lo-lo{background:rgba(0,255,65,0.04);border:1px solid rgba(0,255,65,0.2);border-radius:3px;padding:10px}
.timeline-item{border-left:3px solid #252525;padding:6px 12px;margin-bottom:6px}
.timeline-near{border-left-color:#00FF41}
.timeline-mid{border-left-color:#FFB800}
.timeline-long{border-left-color:#666}
.scenario-bear{background:#FF303010;border:1px solid #FF303033;border-top:2px solid #FF3030;border-radius:4px;padding:14px;text-align:center}
.scenario-base{background:var(--color,#00FF4110);border:1px solid rgba(0,255,65,0.2);border-top:2px solid #00FF41;border-radius:4px;padding:14px;text-align:center}
.scenario-bull{background:#FFB80010;border:1px solid #FFB80033;border-top:2px solid #FFB800;border-radius:4px;padding:14px;text-align:center}
.stAlert{background:#0f0f0f!important;border-color:#252525!important}
</style>
""", unsafe_allow_html=True)

# ─── LOAD STOCK UNIVERSE ─────────────────────────────────────────────────────
@st.cache_data
def load_universe():
    # Try loading from stocks_data.json (deployed with app)
    for path in ["stocks_data.json", "data/stocks_data.json"]:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    # Fallback: embedded minimal universe
    return []

STOCKS = load_universe()
TICKERS = [s['ticker'] for s in STOCKS]

# Sector mapping (enriched)
SECTOR_MAP = {
    'NVDA':'Semiconductors','ANET':'AI Networking','PLTR':'AI/Software','HUBS':'CRM/SaaS',
    'HIMS':'Digital Health','LLY':'Pharmaceuticals','PMRTY':'Consumer/Toys','CRWD':'Cybersecurity',
    'DKNG':'Online Gaming','APP':'AdTech','AFRM':'FinTech/BNPL','ONON':'Sportswear',
    'SHOP':'E-Commerce','NU':'Digital Banking','NFLX':'Streaming','AVGO':'Semiconductors',
    'SPOT':'Audio Streaming','META':'Social Media','MU':'Memory Chips','FTNT':'Cybersecurity',
    'SOFI':'Digital Banking','ALAB':'AI Chips','AMD':'Semiconductors','RDDT':'Social Media',
    'TTD':'AdTech','AMZN':'E-Commerce/Cloud','ROKU':'Streaming','MELI':'LatAm E-Commerce',
    'PANW':'Cybersecurity','XYZ':'FinTech','TSM':'Semiconductor Foundry','GOOG':'Internet/Cloud',
    'MSFT':'Software/Cloud','JD':'China E-Commerce','VEEV':'Pharma SaaS','ASML':'Semiconductor Equipment',
    'IREN':'Bitcoin Mining','BKNG':'Online Travel','UBER':'Ride-Hailing','HOOD':'FinTech/Brokerage',
    'BABA':'China E-Commerce','ARGX':'Biotech','NET':'Cloud Security','DUOL':'EdTech',
    'ELF':'Beauty/Consumer','AXP':'Financial Services','ISRG':'Robotic Surgery','DOCS':'Healthcare IT',
    'RYCEY':'Aerospace/Defence','ETSY':'E-Commerce','UPWK':'Freelance Platform','BRK.B':'Conglomerate',
    'CRWV':'AI Infrastructure','COIN':'Crypto Exchange','IBKR':'Online Brokerage','BYDDY':'EV/Battery',
    'UPST':'AI Lending','CRM':'Enterprise Software','NVO':'Pharmaceuticals','WPLCF':'FinTech/Payments',
    'KNSL':'Insurance','ETOR':'Social Trading','MGNI':'AdTech','AAPL':'Consumer Tech',
    'PDD':'China E-Commerce','BIDU':'China Internet','TCEHY':'China Internet','MAR':'Hospitality',
    'ON':'Semiconductors','DOCU':'eSignature/SaaS','TSLA':'EV/Energy','ENPH':'Solar Energy',
    'Peri':'AdTech','TCOM':'Online Travel','FUBO':'Streaming','GCT':'B2B Marketplace',
    'LC':'FinTech/Lending','NBIS':'AI Infrastructure',
}

# Signal colors
SIG_COLOR = {
    'Buy':'#00FF41','Strong Buy':'#00cc33','STRONG BUY':'#00cc33','BUY':'#00FF41',
    'Watch':'#FFB800','WATCH':'#FFB800','Hold':'#00e5ff','HOLD':'#00e5ff',
    'Sell':'#FF3030','SELL':'#FF3030','Accumulate':'#b06bff',
}

# ─── SESSION STATE ────────────────────────────────────────────────────────────
for k, v in {
    'selected_ticker': 'NVDA',
    'gemini_key': '',
    'ai_cache': {},
    'price_cache': {},
    'chat_history': [],
    'tab_view': 'overview',
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── GEMINI SETUP ─────────────────────────────────────────────────────────────
def get_gemini_model(api_key):
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"temperature": 0.35, "max_output_tokens": 2048}
        )
    except Exception:
        return None

# ─── LIVE DATA FETCHERS ───────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(ticker):
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}

@st.cache_data(ttl=60, show_spinner=False)
def fetch_price(ticker):
    try:
        h = yf.Ticker(ticker).history(period="5d")
        if h.empty or len(h) < 2:
            return None, None, None
        p = float(h['Close'].iloc[-1])
        prev = float(h['Close'].iloc[-2])
        vol = float(h['Volume'].iloc[-1]) if 'Volume' in h else None
        return p, (p - prev) / prev, vol
    except Exception:
        return None, None, None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_history(ticker, period="5y"):
    try:
        h = yf.Ticker(ticker).history(period=period)
        if h.empty:
            return pd.DataFrame()
        h.index = pd.to_datetime(h.index).tz_localize(None) if h.index.tzinfo is None else pd.to_datetime(h.index).tz_convert(None)
        return h
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_financials(ticker):
    try:
        t = yf.Ticker(ticker)
        return {
            'income': t.income_stmt,
            'cashflow': t.cash_flow,
            'balance': t.balance_sheet,
            'earnings_hist': t.earnings_history,
        }
    except Exception:
        return {'income': None, 'cashflow': None, 'balance': None, 'earnings_hist': None}

# ─── CHART BUILDERS ───────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor='#000', plot_bgcolor='#080808',
    font=dict(family="'JetBrains Mono', monospace", color='#666', size=10),
    margin=dict(l=8, r=8, t=36, b=8),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#252525',
                orientation='h', y=1.08, x=0, font=dict(size=9)),
    hovermode='x unified',
)
GRID = dict(gridcolor='#1a1a1a', zeroline=False, zerolinecolor='#333')

def price_chart(ticker, hist, info):
    if hist.empty:
        return go.Figure()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.04)
    color = '#00FF41'
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], name='Price',
        mode='lines', line=dict(color=color, width=1.5),
        fill='tozeroy', fillcolor='rgba(0,255,65,0.06)'
    ), row=1, col=1)
    # MA50, MA200
    if len(hist) >= 50:
        ma50 = hist['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(x=ma50.index, y=ma50, name='MA50',
            mode='lines', line=dict(color='#FFB800', width=1, dash='dot')), row=1, col=1)
    if len(hist) >= 200:
        ma200 = hist['Close'].rolling(200).mean()
        fig.add_trace(go.Scatter(x=ma200.index, y=ma200, name='MA200',
            mode='lines', line=dict(color='#b06bff', width=1, dash='dash')), row=1, col=1)
    # Volume
    vol_colors = ['rgba(0,255,65,0.4)' if c >= o else 'rgba(255,48,48,0.4)'
                  for c, o in zip(hist['Close'], hist['Open'])]
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume',
        marker_color=vol_colors, showlegend=False), row=2, col=1)
    fig.update_layout(**CHART_LAYOUT,
        title=dict(text=f"📈 {ticker} — Price & Volume", font=dict(color=color, size=13)),
        height=420)
    for r in [1, 2]:
        fig.update_xaxes(**GRID, row=r, col=1)
        fig.update_yaxes(**GRID, row=r, col=1)
    return fig

def revenue_fcf_chart(ticker, fin_data):
    inc = fin_data.get('income')
    cf = fin_data.get('cashflow')
    if inc is None or inc.empty:
        return None
    years, revs, ebitda_list, fcf_list = [], [], [], []
    for col in sorted(inc.columns, reverse=True)[:5]:
        try:
            yr = str(col)[:4]
            rev = None
            for k in ['Total Revenue', 'Revenue']:
                if k in inc.index:
                    v = inc.loc[k, col]
                    if pd.notna(v): rev = float(v) / 1e9; break
            ebitda = None
            for k in ['EBITDA', 'Normalized EBITDA']:
                if k in inc.index:
                    v = inc.loc[k, col]
                    if pd.notna(v): ebitda = float(v) / 1e9; break
            fcf = None
            if cf is not None and not cf.empty and col in cf.columns:
                for k in ['Free Cash Flow']:
                    if k in cf.index:
                        v = cf.loc[k, col]
                        if pd.notna(v): fcf = float(v) / 1e9; break
            if rev is not None:
                years.append(yr); revs.append(rev)
                ebitda_list.append(ebitda); fcf_list.append(fcf)
        except Exception:
            continue
    if not years:
        return None
    years = list(reversed(years)); revs = list(reversed(revs))
    ebitda_list = list(reversed(ebitda_list)); fcf_list = list(reversed(fcf_list))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=years, y=revs, name='Revenue ($B)',
        marker_color='rgba(0,255,65,0.6)', marker_line_color='#00FF41',
        marker_line_width=1), secondary_y=False)
    if any(e is not None for e in ebitda_list):
        fig.add_trace(go.Scatter(x=years, y=ebitda_list, name='EBITDA ($B)',
            mode='lines+markers', line=dict(color='#FFB800', width=2),
            marker=dict(size=6, color='#FFB800')), secondary_y=True)
    if any(f is not None for f in fcf_list):
        fig.add_trace(go.Scatter(x=years, y=fcf_list, name='FCF ($B)',
            mode='lines+markers', line=dict(color='#00e5ff', width=2),
            marker=dict(size=6, color='#00e5ff')), secondary_y=True)
    fig.update_layout(**CHART_LAYOUT,
        title=dict(text=f"💰 {ticker} — Revenue · EBITDA · FCF", font=dict(color='#00FF41', size=12)),
        height=280, barmode='group')
    fig.update_xaxes(**GRID); fig.update_yaxes(**GRID, secondary_y=False); fig.update_yaxes(**GRID, secondary_y=True, showgrid=False)
    return fig

def eps_chart(ticker, fin_data):
    inc = fin_data.get('income')
    if inc is None or inc.empty:
        return None
    years, eps_list = [], []
    for col in sorted(inc.columns, reverse=True)[:5]:
        try:
            yr = str(col)[:4]
            for k in ['Diluted EPS', 'Basic EPS']:
                if k in inc.index:
                    v = inc.loc[k, col]
                    if pd.notna(v):
                        years.append(yr); eps_list.append(float(v)); break
        except Exception:
            continue
    if not years:
        return None
    years = list(reversed(years)); eps_list = list(reversed(eps_list))
    colors = ['rgba(0,255,65,0.7)' if e >= 0 else 'rgba(255,48,48,0.7)' for e in eps_list]
    fig = go.Figure(go.Bar(x=years, y=eps_list, name='EPS ($)',
        marker_color=colors, marker_line_color='#333', marker_line_width=0.5,
        text=[f"${e:.2f}" for e in eps_list], textposition='outside',
        textfont=dict(size=9, color='#666')))
    fig.update_layout(**CHART_LAYOUT,
        title=dict(text=f"📊 {ticker} — EPS History", font=dict(color='#FFB800', size=12)),
        height=240)
    fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
    return fig

def pe_ps_chart(ticker, info):
    """Simple current vs median PE/PS gauge."""
    pe = info.get('trailingPE'); ps = info.get('priceToSalesTrailing12Months')
    fpe = info.get('forwardPE')
    if not any([pe, ps, fpe]):
        return None
    labels, vals, colors = [], [], []
    if pe:
        try: labels.append('TTM PE'); vals.append(float(pe)); colors.append('#FFB800')
        except: pass
    if fpe:
        try: labels.append('Fwd PE'); vals.append(float(fpe)); colors.append('#00FF41')
        except: pass
    if ps:
        try: labels.append('P/S'); vals.append(float(ps)); colors.append('#00e5ff')
        except: pass
    if not labels:
        return None
    fig = go.Figure(go.Bar(x=labels, y=vals, marker_color=colors,
        text=[f"{v:.1f}x" for v in vals], textposition='outside',
        textfont=dict(size=10, color='#e8e8e8')))
    fig.update_layout(**CHART_LAYOUT,
        title=dict(text=f"📐 {ticker} — Valuation Multiples", font=dict(color='#00e5ff', size=12)),
        height=220)
    fig.update_xaxes(**GRID, tickfont=dict(size=10))
    fig.update_yaxes(**GRID)
    return fig

def portfolio_scatter(stocks_data):
    """PE vs Revenue Growth scatter for all stocks."""
    rows = []
    for s in stocks_data:
        try:
            pe = float(s.get('pe', 0)) if s.get('pe') else None
            revg = float(s.get('rev_growth_ly', 0)) if s.get('rev_growth_ly') else None
            ps = float(s.get('ps', 0)) if s.get('ps') else None
            if pe and revg and 0 < pe < 400:
                rows.append({'Ticker': s['ticker'], 'Name': s['name'][:25],
                             'PE': pe, 'PS': ps or 0, 'RevGrowth%': revg * 100,
                             'MCap': s.get('mcap_b', 0) or 0,
                             'Rec': s.get('recommendation', 'Watch')})
        except Exception:
            continue
    if not rows:
        return go.Figure()
    df = pd.DataFrame(rows)
    fig = px.scatter(df, x='RevGrowth%', y='PE', text='Ticker',
                     size='MCap', color='Rec', hover_data=['Name', 'PS'],
                     color_discrete_map={'Buy': '#00FF41', 'Strong Buy': '#00cc33',
                                         'Watch': '#FFB800', 'Hold': '#00e5ff',
                                         'Sell': '#FF3030', '': '#444'},
                     size_max=50)
    fig.update_traces(textposition='top center', textfont=dict(size=8, color='#888'))
    fig.update_layout(**CHART_LAYOUT,
        title=dict(text="🗺 Portfolio Map — PE vs Revenue Growth (bubble=MCap)", font=dict(color='#00FF41', size=12)),
        height=500, xaxis_title='Revenue Growth % (LY)', yaxis_title='PE Multiple')
    fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
    # Add quadrant lines
    fig.add_hline(y=40, line=dict(color='#333', dash='dot', width=1))
    fig.add_vline(x=20, line=dict(color='#333', dash='dot', width=1))
    return fig

# ─── AI ANALYSIS ──────────────────────────────────────────────────────────────
def ai_analyze_stock(model, ticker, name, stock_data, live_info, price, chg):
    """Full institutional AI analysis of a stock."""
    if model is None:
        return None
    cache_key = f"analysis_{ticker}"
    if cache_key in st.session_state.ai_cache:
        return st.session_state.ai_cache[cache_key]

    def safe_pct(v):
        if v is None or (isinstance(v, float) and np.isnan(v)): return 'N/A'
        try: return f"{float(v)*100:.1f}%"
        except: return str(v)

    prompt = f"""
You are a senior hedge fund analyst at Citadel Global Equities.
Provide a DEEP institutional-grade analysis for {ticker} ({name}).

LIVE DATA (from portfolio system):
- Current Price: ${price:.2f} | 24H Change: {(chg or 0)*100:+.2f}%
- PE (TTM): {stock_data.get('pe','N/A')} | PS: {stock_data.get('ps','N/A')}
- MCap: ${stock_data.get('mcap_b','N/A')}B | Category: {stock_data.get('mcap_cat','N/A')}
- ATH: ${stock_data.get('high','N/A')} | ATH Retrace: {safe_pct(stock_data.get('ath_retrace'))}
- Revenue LY: ${stock_data.get('rev_ly','N/A')} | Rev Growth LY: {safe_pct(stock_data.get('rev_growth_ly'))}
- Revenue 3Y CAGR: {safe_pct(stock_data.get('rev_3y_cagr'))}
- Rev 2026E: ${stock_data.get('rev_2026e','N/A')} | Growth: {safe_pct(stock_data.get('rev_growth_2026'))}
- EBITDA LY: ${stock_data.get('ebitda_ly','N/A')} | 3Y CAGR: {safe_pct(stock_data.get('ebitda_3y_cagr'))}
- EPS LY: ${stock_data.get('eps_ly','N/A')} | EPS 3Y CAGR: {safe_pct(stock_data.get('eps_3y_cagr'))}
- EPS 2026E: ${stock_data.get('eps_2026e','N/A')} | 2027E: ${stock_data.get('eps_2027e','N/A')}
- FCF Y1: ${stock_data.get('fcf_y1','N/A')} | TTM: ${stock_data.get('fcf_ttm','N/A')}
- Net Debt TTM: ${stock_data.get('net_debt_ttm','N/A')}
- Price Follows: {stock_data.get('price_follows','N/A')}
- Hypothesis Price: {stock_data.get('hypothesis_price','N/A')}
- Points/Score: {stock_data.get('points','N/A')} / 10
- Sector: {SECTOR_MAP.get(ticker,'Unknown')}

LIVE MARKET DATA:
- Market Cap: ${(live_info.get('marketCap',0) or 0)/1e9:.1f}B
- 52W High: ${live_info.get('fiftyTwoWeekHigh','N/A')} | Low: ${live_info.get('fiftyTwoWeekLow','N/A')}
- Beta: {live_info.get('beta','N/A')} | Short Float: {(live_info.get('shortPercentOfFloat',0) or 0)*100:.1f}%
- Revenue Growth (live): {(live_info.get('revenueGrowth',0) or 0)*100:.1f}%
- Earnings Growth (live): {(live_info.get('earningsGrowth',0) or 0)*100:.1f}%
- Free Cash Flow: ${(live_info.get('freeCashflow',0) or 0)/1e9:.2f}B

Return ONLY valid JSON (no markdown, no backticks):
{{
  "thesis": "2-3 sentence core investment thesis",
  "moat": "1-sentence moat description",
  "moat_layers": [
    {{"layer": "moat name", "stars": 1-5, "verdict": "UNASSAILABLE/FORTRESS/STRONG/BUILDING/WEAK", "detail": "brief explanation"}}
  ],
  "why_now": "Why buy/watch now - current catalysts",
  "bull_case": ["point 1", "point 2", "point 3"],
  "bear_case": ["risk 1", "risk 2", "risk 3"],
  "signal": "STRONG BUY|BUY|ACCUMULATE|HOLD|WATCH|REDUCE|SELL",
  "conviction": 1-5,
  "risk_score": 0-100,
  "antigravity_score": 0-100,
  "antigravity_reason": "one line - why this stock defies or follows gravity",
  "scenarios": {{
    "bear": {{"price": 0.0, "return_pct": "-X%", "trigger": "brief trigger"}},
    "base": {{"price": 0.0, "return_pct": "+X%", "trigger": "brief trigger"}},
    "bull": {{"price": 0.0, "return_pct": "+X%", "trigger": "brief trigger"}}
  }},
  "catalysts": [
    {{"horizon": "NEAR|MID|LONG", "text": "catalyst", "timing": "Q1 2026 etc", "impact": "HIGH|MEDIUM|LOW|CONFIRMED"}}
  ],
  "risks": [
    {{"sev": "🔴|🟡|🟢", "risk": "risk name", "prob": "HIGH|LOW", "imp": "HIGH|LOW", "detail": "brief"}}
  ],
  "entry": "ideal entry price",
  "target_3y": "3Y price target",
  "return_3y": "+X%",
  "pa": "+X% p.a.",
  "exit_trigger": "what would make you sell",
  "key_edge": "1-2 sentences on the single best reason to own this",
  "watch": "main item to watch in next quarter",
  "grade": "A+|A|A-|B+|B|B-|C+|C|D|F",
  "verdict": "One sentence buy/sell verdict with conviction stars"
}}
"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        text = re.sub(r'```(?:json)?', '', text).strip().rstrip('`').strip()
        result = json.loads(text)
        st.session_state.ai_cache[cache_key] = result
        return result
    except Exception as e:
        return {"error": str(e), "thesis": f"Analysis unavailable: {e}"}

def ai_chat(model, question, context):
    """Chat with Gemini about the portfolio."""
    if model is None:
        return "⚠️ Connect Gemini API key in sidebar to use AI chat."
    try:
        sys = f"""You are PYKUPZ AI — an elite hedge fund analyst for a 78-stock portfolio.
Context: {context[:600]}
Be concise, data-driven, actionable. Max 250 words. Use terminal-style bullet points."""
        msgs = [{"role": "user", "parts": [sys]}]
        for h in st.session_state.chat_history[-6:]:
            msgs.append({"role": h["role"], "parts": [h["content"]]})
        msgs.append({"role": "user", "parts": [question]})
        resp = model.generate_content(msgs)
        return resp.text
    except Exception as e:
        return f"⚠️ Error: {e}"

# ─── FORMAT HELPERS ───────────────────────────────────────────────────────────
def fmt_num(v, prefix='$', suffix='B', decimals=2):
    if v is None or (isinstance(v, float) and np.isnan(v)): return '—'
    try:
        f = float(v)
        return f"{prefix}{f:.{decimals}f}{suffix}"
    except:
        return str(v)

def fmt_pct(v, mul=True):
    if v is None or (isinstance(v, float) and np.isnan(v)): return '—'
    try:
        f = float(v) * (100 if mul else 1)
        sign = '+' if f >= 0 else ''
        return f"{sign}{f:.1f}%"
    except:
        return '—'

def color_pct(v, mul=True):
    try:
        f = float(v) * (100 if mul else 1)
        return '#00FF41' if f >= 0 else '#FF3030'
    except:
        return '#666'

def stars(n):
    try:
        n = int(n)
        return '★' * n + '☆' * (5 - n)
    except:
        return '—'

def rec_tag(rec):
    rec = str(rec).strip().upper()
    if 'STRONG BUY' in rec: cls = 'tag-buy'
    elif 'BUY' in rec: cls = 'tag-buy'
    elif 'SELL' in rec: cls = 'tag-sell'
    elif 'WATCH' in rec: cls = 'tag-watch'
    else: cls = 'tag-hold'
    return f'<span class="tag {cls}">{rec}</span>'

def mc(val, label, color_class='', size=18):
    """Metric card HTML."""
    return f"""<div class="metric-card {color_class}">
<div class="metric-val" style="font-size:{size}px">{val}</div>
<div class="metric-lbl">{label}</div></div>"""

def sh(text, color='#00FF41'):
    return f'<div class="sh" style="color:{color}">{text}</div>'

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""<div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;
        letter-spacing:2px;color:#00FF41;padding:4px 0 8px">⚡ PYKUPZ TERMINAL</div>""", unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:1px'>{len(STOCKS)} STOCKS · MARCH 2026</div>", unsafe_allow_html=True)
        st.markdown("---")

        # Gemini API Key
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#4285f4;letter-spacing:2px">🤖 GEMINI AI</div>', unsafe_allow_html=True)
        api_key = st.text_input("API Key", value=st.session_state.gemini_key,
            type="password", placeholder="AIza... (get free at aistudio.google.com)",
            label_visibility="collapsed")
        if api_key != st.session_state.gemini_key:
            st.session_state.gemini_key = api_key
            st.session_state.ai_cache = {}
        if api_key:
            st.markdown('<span style="color:#34a853;font-family:JetBrains Mono,monospace;font-size:9px">✅ GEMINI CONNECTED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#FF3030;font-family:JetBrains Mono,monospace;font-size:9px">⚠️ NO KEY — AI DISABLED</span>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#555;letter-spacing:2px">🔍 SEARCH & SELECT</div>', unsafe_allow_html=True)

        # Search
        search = st.text_input("Search", placeholder="Ticker or company name...", label_visibility="collapsed")

        # Filter by recommendation
        rec_filter = st.selectbox("Filter", ["All", "Buy", "Watch", "Hold", "Sell"], label_visibility="collapsed")

        # Build filtered list
        filtered = STOCKS
        if search:
            s = search.upper()
            filtered = [x for x in filtered if s in x['ticker'].upper() or s in x['name'].upper()]
        if rec_filter != "All":
            filtered = [x for x in filtered if rec_filter.lower() in str(x.get('recommendation', '')).lower()]

        st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:8px;color:#444'>{len(filtered)} stocks</div>", unsafe_allow_html=True)

        # Stock list
        for s in filtered:
            ticker = s['ticker']
            name = s['name'][:22]
            rec = str(s.get('recommendation', '')).strip()
            pts = s.get('points') or s.get('reconcile')
            score = f" · {pts:.0f}pts" if pts and not (isinstance(pts, float) and np.isnan(pts)) else ""
            sel = ticker == st.session_state.selected_ticker
            bg = '#161616' if sel else 'transparent'
            border = 'border-left:2px solid #00FF41;' if sel else 'border-left:2px solid transparent;'

            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"**{ticker}**  {name}{score}", key=f"btn_{ticker}",
                                 use_container_width=True):
                        st.session_state.selected_ticker = ticker
                        st.session_state.tab_view = 'overview'
                        st.rerun()

        st.markdown("---")
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#333">AI cache: {len(st.session_state.ai_cache)} analyses</div>', unsafe_allow_html=True)

# ─── OVERVIEW HEADER ─────────────────────────────────────────────────────────
def render_header(ticker, s, info, price, chg, vol):
    color = '#00FF41' if (chg or 0) >= 0 else '#FF3030'
    arr = '▲' if (chg or 0) >= 0 else '▼'
    ath = s.get('high')
    ath_txt = f"-{abs(float(s.get('ath_retrace',0))*100):.1f}% ATH" if s.get('ath_retrace') else ""
    rec = str(s.get('recommendation', '')).strip()

    st.markdown(f"""
    <div style="background:#080808;border-bottom:2px solid {color};padding:10px 16px;margin-bottom:12px">
      <div style="display:flex;align-items:flex-start;justify-content:space-between">
        <div>
          <div style="display:flex;align-items:center;gap:12px">
            <span style="font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700;color:{color};letter-spacing:2px">{ticker}</span>
            <span style="font-family:JetBrains Mono,monospace;font-size:12px;color:#666">{s['name']}</span>
            <span class="tag" style="background:{color}22;border:1px solid {color}44;color:{color}">{SECTOR_MAP.get(ticker,'Unknown')}</span>
            {rec_tag(rec) if rec else ''}
          </div>
          <div style="display:flex;gap:20px;margin-top:6px;align-items:center">
            <span style="font-family:JetBrains Mono,monospace;font-size:20px;color:#e8e8e8;font-weight:600">${price:.2f}</span>
            <span style="font-family:JetBrains Mono,monospace;font-size:13px;color:{color}">{arr}{abs((chg or 0)*100):.2f}%</span>
            <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#444">{ath_txt}</span>
          </div>
          <div style="display:flex;gap:16px;margin-top:4px">
            {''.join([f'<span style="font-family:JetBrains Mono,monospace;font-size:9px;color:#555">{k}: <span style="color:#888">{v}</span></span>'
              for k, v in [
                ('PE', f"{s.get('pe','—')}"), ('PS', f"{s.get('ps','—')}"),
                ('MCap', f"${s.get('mcap_b','—')}B"), ('ATH', f"${ath}" if ath else '—'),
                ('Score', f"{s.get('points','—')}/10"),
              ]])}
          </div>
        </div>
        <div style="text-align:right">
          <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#333">{datetime.now().strftime('%H:%M:%S')}</div>
          <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#333">PYKUPZ Q1 2026</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── OVERVIEW TAB ─────────────────────────────────────────────────────────────
def render_overview(ticker, s, info, price, chg, ai, model):
    # Metrics row
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    def mcol(col, val, lbl, cls=''):
        col.markdown(f'<div class="metric-card {cls}"><div class="metric-val" style="font-size:15px">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    mcol(c1, f"${price:.2f}", "LIVE PRICE", 'green' if (chg or 0)>=0 else 'red')
    mcol(c2, fmt_pct(chg, mul=False), "24H CHANGE", 'green' if (chg or 0)>=0 else 'red')
    pe_v = s.get('pe')
    mcol(c3, f"{pe_v:.1f}x" if pe_v else '—', "PE (TTM)", 'amber')
    ps_v = s.get('ps')
    mcol(c4, f"{ps_v:.1f}x" if ps_v else '—', "P/S", '')
    mcol(c5, f"${s.get('mcap_b','—')}B", "MARKET CAP", '')
    pts = s.get('points') or s.get('reconcile')
    mcol(c6, f"{pts:.1f}/10" if pts else '—', "PYKUPZ SCORE", 'cyan')

    st.markdown("<br>", unsafe_allow_html=True)

    if ai and 'error' not in ai:
        # AI thesis panel
        sig = ai.get('signal', 'HOLD')
        grade = ai.get('grade', '—')
        conviction = ai.get('conviction', 3)
        risk_score = ai.get('risk_score', 50)
        ag_score = ai.get('antigravity_score', 50)
        sig_color = SIG_COLOR.get(sig, '#FFB800')

        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown(f"""
            <div class="gem-panel">
              <div class="gem-title">🤖 AI INVESTMENT THESIS — {ticker}</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:11px;line-height:1.7;color:#e8e8e8">{ai.get('thesis','—')}</div>
              <div style="margin-top:8px;font-family:JetBrains Mono,monospace;font-size:9px;color:#FFB800">{ai.get('why_now','')}</div>
              <div style="margin-top:8px;padding:6px 10px;background:#161616;border-left:3px solid #4285f4;border-radius:1px">
                <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:2px;margin-bottom:3px">MOAT IN ONE LINE</div>
                <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4285f4;font-style:italic">"{ai.get('moat','—')}"</div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Bull / Bear
            b1, b2 = st.columns(2)
            with b1:
                st.markdown('<div class="sh" style="color:#00FF41;font-size:9px">🟢 BULL CASE</div>', unsafe_allow_html=True)
                for pt in ai.get('bull_case', []):
                    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:9px;padding:3px 0;border-bottom:1px solid #1a1a1a;color:#888">✅ {pt}</div>', unsafe_allow_html=True)
            with b2:
                st.markdown('<div class="sh" style="color:#FF3030;font-size:9px">🔴 BEAR CASE</div>', unsafe_allow_html=True)
                for pt in ai.get('bear_case', []):
                    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:9px;padding:3px 0;border-bottom:1px solid #1a1a1a;color:#888">⚠️ {pt}</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;padding:16px;border:1px solid {sig_color}44;border-top:2px solid {sig_color}">
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:2px">AI SIGNAL</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;color:{sig_color};font-weight:700;margin:4px 0">{sig}</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:2px;margin-top:8px">GRADE</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;color:#00e5ff;font-weight:700">{grade}</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;margin-top:8px">CONVICTION</div>
              <div style="color:#FFB800;font-size:14px">{'★'*conviction}{'☆'*(5-conviction)}</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;margin-top:8px">RISK SCORE</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:16px;color:#FF3030">{risk_score}/100</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;margin-top:8px">ANTIGRAVITY</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:20px;color:#b06bff">{ag_score}</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444">/100</div>
            </div>
            <div style="margin-top:6px;font-family:JetBrains Mono,monospace;font-size:8px;color:#555;line-height:1.5">{ai.get('antigravity_reason','')}</div>
            """, unsafe_allow_html=True)

            # Key levels
            sc = ai.get('scenarios', {})
            base = sc.get('base', {})
            if base.get('price'):
                st.markdown(f"""
                <div class="metric-card" style="margin-top:6px">
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:2px">3Y BASE TARGET</div>
                  <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;color:#00FF41;font-weight:700">${base['price']:,.0f}</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#00FF41">{base.get('return_pct','+')} / {ai.get('pa','—')}</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;margin-top:4px">ENTRY</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#e8e8e8">{ai.get('entry','—')}</div>
                </div>""", unsafe_allow_html=True)

        # Key edge + watch
        if ai.get('key_edge'):
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #00FF4133;border-radius:3px;padding:10px 14px;margin-top:6px">
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;letter-spacing:2px;margin-bottom:4px">⚡ KEY EDGE</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#00FF41;line-height:1.6">{ai.get('key_edge','')}</div>
            </div>""", unsafe_allow_html=True)
        if ai.get('watch'):
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #FFB80033;border-radius:3px;padding:10px 14px;margin-top:6px">
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#FFB800;letter-spacing:2px;margin-bottom:4px">⚠️ WATCH ITEM</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#888;line-height:1.6">{ai.get('watch','')}</div>
            </div>""", unsafe_allow_html=True)
        if ai.get('verdict'):
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #4285f433;border-radius:3px;padding:8px 14px;margin-top:6px">
              <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#4285f4;line-height:1.5">{ai.get('verdict','')}</div>
            </div>""", unsafe_allow_html=True)

    else:
        # No AI — show raw data
        st.markdown('<div class="sh">📋 RAW PORTFOLIO DATA (from Pyk-Inv-List)</div>', unsafe_allow_html=True)
        data_items = [
            ("Revenue LY", fmt_num(s.get('rev_ly'), decimals=0)),
            ("Rev Growth LY", fmt_pct(s.get('rev_growth_ly'))),
            ("Rev 3Y CAGR", fmt_pct(s.get('rev_3y_cagr'))),
            ("Rev 2026E", fmt_num(s.get('rev_2026e'), decimals=0)),
            ("EBITDA LY", fmt_num(s.get('ebitda_ly'), decimals=0)),
            ("EBITDA 3Y CAGR", fmt_pct(s.get('ebitda_3y_cagr'))),
            ("EPS LY", f"${s.get('eps_ly','—')}"),
            ("EPS 3Y CAGR", fmt_pct(s.get('eps_3y_cagr'))),
            ("EPS 2026E", f"${s.get('eps_2026e','—')}"),
            ("FCF TTM", fmt_num(s.get('fcf_ttm'), decimals=0)),
            ("Net Debt TTM", fmt_num(s.get('net_debt_ttm'), decimals=0)),
            ("GAPS (P/S)", f"{s.get('gaps','—')}"),
            ("GAPE (P/E)", f"{s.get('gape','—')}"),
            ("Hypothesis Price", s.get('hypothesis_price','—')),
            ("Price Follows", s.get('price_follows','—')),
        ]
        cols = st.columns(5)
        for i, (k, v) in enumerate(data_items):
            cols[i%5].markdown(f'<div class="metric-card"><div class="metric-val" style="font-size:13px">{v}</div><div class="metric-lbl">{k}</div></div>', unsafe_allow_html=True)

        if not st.session_state.gemini_key:
            st.info("💡 Add Gemini API key in sidebar to get AI thesis, moat analysis, scenarios, catalysts & risk matrix for all 78 stocks.")

# ─── VALUATION TAB ───────────────────────────────────────────────────────────
def render_valuation(ticker, s, info, fin):
    st.markdown('<div class="sh">📐 VALUATION DASHBOARD</div>', unsafe_allow_html=True)

    # Valuation table
    pe_val = s.get('pe'); ps_val = s.get('ps')
    fpe = info.get('forwardPE'); mktcap = info.get('marketCap', 0) or 0
    pb = info.get('priceToBook'); peg = info.get('trailingPegRatio')

    items = [
        ("PE (TTM)", f"{pe_val:.2f}x" if pe_val else '—', 'amber'),
        ("Forward PE", f"{fpe:.1f}x" if fpe else '—', 'amber'),
        ("P/S (TTM)", f"{ps_val:.2f}x" if ps_val else '—', ''),
        ("P/B", f"{pb:.1f}x" if pb else '—', ''),
        ("PEG Ratio", f"{peg:.2f}" if peg else '—', ''),
        ("Market Cap", f"${mktcap/1e9:.1f}B", 'cyan'),
        ("ATH", f"${s.get('high','—')}", ''),
        ("ATH Retrace", fmt_pct(s.get('ath_retrace')), 'red' if (s.get('ath_retrace') or 0) < -0.2 else ''),
        ("GAPS (P/S)", f"{s.get('gaps','—')}", ''),
        ("GAPE (P/E)", f"{s.get('gape','—')}", ''),
        ("Hypothesis Price", s.get('hypothesis_price','—'), 'green'),
        ("Score", f"{s.get('points','—')}/10", 'cyan'),
    ]
    cols = st.columns(4)
    for i, (k, v, cls) in enumerate(items):
        cols[i%4].markdown(f'<div class="metric-card {cls}"><div class="metric-val" style="font-size:14px">{v}</div><div class="metric-lbl">{k}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # PE/PS chart
    fig = pe_ps_chart(ticker, info)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # GAPS & GAPE trajectory
    st.markdown('<div class="sh">📊 P/S (GAPS) & P/E (GAPE) TRAJECTORY</div>', unsafe_allow_html=True)
    gap_data = {'Period': ['3Y Ago', 'TTM', '2025E', '2026E']}
    gs = [s.get('gaps'), s.get('gaps_ttm'), s.get('gaps_2025'), s.get('gaps_2026')]
    ge = [s.get('gape'), s.get('gape_ttm'), s.get('gape_2025'), s.get('gape_2026')]
    gs_clean = [float(v) if v and v != 'nan' else None for v in gs]
    ge_clean = [float(v) if v and v != 'nan' else None for v in ge]

    if any(v is not None for v in gs_clean) or any(v is not None for v in ge_clean):
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        if any(v is not None for v in gs_clean):
            fig2.add_trace(go.Bar(x=gap_data['Period'], y=gs_clean, name='P/S (GAPS)',
                marker_color='rgba(0,229,255,0.6)'), secondary_y=False)
        if any(v is not None for v in ge_clean):
            fig2.add_trace(go.Scatter(x=gap_data['Period'], y=ge_clean, name='P/E (GAPE)',
                mode='lines+markers', line=dict(color='#FFB800', width=2),
                marker=dict(size=7)), secondary_y=True)
        fig2.update_layout(**CHART_LAYOUT, height=220,
            title=dict(text=f"📐 {ticker} — Valuation Multiple Trajectory", font=dict(color='#00e5ff', size=11)))
        fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID, secondary_y=False)
        fig2.update_yaxes(**GRID, secondary_y=True, showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)

# ─── GROWTH TAB ──────────────────────────────────────────────────────────────
def render_growth(ticker, s, info, fin):
    st.markdown('<div class="sh">📈 GROWTH & FCF TRAJECTORY</div>', unsafe_allow_html=True)

    # Key growth metrics
    items = [
        ("Rev LY", fmt_num(s.get('rev_ly'), decimals=0), ''),
        ("Rev Growth LY", fmt_pct(s.get('rev_growth_ly')), 'green' if (s.get('rev_growth_ly') or 0)>0.2 else ''),
        ("Rev 3Y CAGR", fmt_pct(s.get('rev_3y_cagr')), 'green'),
        ("Rev TTM", fmt_num(s.get('rev_ttm'), decimals=0), ''),
        ("Rev 2026E", fmt_num(s.get('rev_2026e'), decimals=0), 'cyan'),
        ("Rev 2027E", fmt_num(s.get('rev_2027e'), decimals=0), ''),
        ("EBITDA LY", fmt_num(s.get('ebitda_ly'), decimals=0), ''),
        ("EBITDA 3Y CAGR", fmt_pct(s.get('ebitda_3y_cagr')), 'amber'),
        ("EBITDA 2026E", fmt_num(s.get('ebitda_2026e'), decimals=0), ''),
        ("EPS LY", f"${s.get('eps_ly','—')}", ''),
        ("EPS 3Y CAGR", fmt_pct(s.get('eps_3y_cagr')), 'green'),
        ("EPS 2026E", f"${s.get('eps_2026e','—')}", 'cyan'),
        ("FCF Y1", fmt_num(s.get('fcf_y1'), decimals=0), ''),
        ("FCF TTM", fmt_num(s.get('fcf_ttm'), decimals=0), 'green' if (s.get('fcf_ttm') or 0)>0 else 'red'),
        ("Net Debt TTM", fmt_num(s.get('net_debt_ttm'), decimals=0), 'red' if (s.get('net_debt_ttm') or 0)>0 else 'green'),
        ("Guidance CAGR", fmt_pct(s.get('guidance_cagr')), ''),
    ]
    cols = st.columns(4)
    for i, (k, v, cls) in enumerate(items):
        cols[i%4].markdown(f'<div class="metric-card {cls}"><div class="metric-val" style="font-size:13px">{v}</div><div class="metric-lbl">{k}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Revenue & projections bar chart
    periods = ['3Y Ago', 'Last Year', 'TTM', '2026E', '2027E', '2028E']
    rev_vals = [
        s.get('rev_3y_ago'), s.get('rev_ly'), s.get('rev_ttm'),
        s.get('rev_2026e'), s.get('rev_2027e'), s.get('rev_2028e')
    ]
    rev_clean = []
    for v in rev_vals:
        try: rev_clean.append(float(v) if v else None)
        except: rev_clean.append(None)

    c1, c2 = st.columns(2)
    with c1:
        if any(v is not None for v in rev_clean):
            fig = go.Figure()
            is_proj = [False, False, False, True, True, True]
            colors = ['rgba(0,229,255,0.6)' if not p else 'rgba(0,255,65,0.4)' for p in is_proj]
            fig.add_trace(go.Bar(x=periods, y=rev_clean, marker_color=colors,
                text=[f"${v:.0f}" if v else '' for v in rev_clean], textposition='outside',
                textfont=dict(size=9, color='#666')))
            fig.update_layout(**CHART_LAYOUT, height=260,
                title=dict(text=f"💵 {ticker} Revenue Trajectory", font=dict(color='#00e5ff', size=11)))
            fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        eps_vals = [s.get('eps_3y_ago'), s.get('eps_ly'), s.get('eps_ttm'), s.get('eps_2026e'), s.get('eps_2027e'), s.get('eps_2028e')]
        eps_clean = []
        for v in eps_vals:
            try: eps_clean.append(float(v) if v else None)
            except: eps_clean.append(None)
        if any(v is not None for v in eps_clean):
            colors_eps = ['rgba(0,255,65,0.7)' if (v or 0)>=0 else 'rgba(255,48,48,0.7)' for v in eps_clean]
            fig2 = go.Figure(go.Bar(x=periods, y=eps_clean, marker_color=colors_eps,
                text=[f"${v:.2f}" if v else '' for v in eps_clean], textposition='outside',
                textfont=dict(size=9, color='#666')))
            fig2.update_layout(**CHART_LAYOUT, height=260,
                title=dict(text=f"📊 {ticker} EPS Trajectory", font=dict(color='#FFB800', size=11)))
            fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID)
            st.plotly_chart(fig2, use_container_width=True)

    # Live financials from yfinance
    fig_rf = revenue_fcf_chart(ticker, fin)
    if fig_rf:
        st.plotly_chart(fig_rf, use_container_width=True)
    fig_eps = eps_chart(ticker, fin)
    if fig_eps:
        st.plotly_chart(fig_eps, use_container_width=True)

    # FCF timeline
    fcf_data = [
        ('Year 3', s.get('fcf_y3')), ('Year 2', s.get('fcf_y2')),
        ('Year 1', s.get('fcf_y1')), ('TTM', s.get('fcf_ttm'))
    ]
    fcf_clean = [(k, float(v)) for k, v in fcf_data if v and str(v) != 'nan']
    if fcf_clean:
        fig3 = go.Figure(go.Bar(
            x=[k for k,v in fcf_clean], y=[v for k,v in fcf_clean],
            marker_color=['rgba(0,255,65,0.7)' if v>=0 else 'rgba(255,48,48,0.7)' for k,v in fcf_clean],
            text=[f"${v:.0f}M" for k,v in fcf_clean], textposition='outside',
            textfont=dict(size=9, color='#666')
        ))
        fig3.update_layout(**CHART_LAYOUT, height=220,
            title=dict(text=f"💚 {ticker} Free Cash Flow", font=dict(color='#00FF41', size=11)))
        fig3.update_xaxes(**GRID); fig3.update_yaxes(**GRID)
        st.plotly_chart(fig3, use_container_width=True)

# ─── MOAT TAB ────────────────────────────────────────────────────────────────
def render_moat(ticker, s, ai):
    st.markdown('<div class="sh">🏰 ECONOMIC MOAT ARCHITECTURE</div>', unsafe_allow_html=True)
    if ai and 'error' not in ai and ai.get('moat_layers'):
        st.markdown(f"""<div style="background:#0f0f0f;border:1px solid rgba(66,133,244,0.35);border-radius:3px;padding:10px 14px;margin-bottom:10px">
          <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#4285f4;letter-spacing:2px;margin-bottom:4px">MOAT SUMMARY</div>
          <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4285f4;font-style:italic">"{ai.get('moat','—')}"</div>
        </div>""", unsafe_allow_html=True)

        for m in ai.get('moat_layers', []):
            stars_n = int(m.get('stars', 3))
            verdict = m.get('verdict', '—')
            vcolor = '#00FF41' if 'UNASSAILABLE' in verdict else '#00e5ff' if 'FORTRESS' in verdict else '#FFB800' if 'STRONG' in verdict else '#666'
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #252525;border-radius:3px;padding:10px 14px;margin-bottom:6px">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#00FF41;font-weight:600;flex:1">{m.get('layer','—')}</div>
                <div style="color:#FFB800;font-size:12px;margin:0 10px">{'★'*stars_n}{'☆'*(5-stars_n)}</div>
                <span style="background:{vcolor}22;border:1px solid {vcolor}44;color:{vcolor};font-family:JetBrains Mono,monospace;font-size:8px;padding:2px 7px;border-radius:2px">{verdict}</span>
              </div>
              <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#555;font-style:italic">{m.get('detail','')}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info(f"🤖 Add Gemini API key to generate moat analysis for {ticker}.")
        # Show raw data clues
        st.markdown('<div class="sh" style="margin-top:10px">📋 RAW INDICATORS</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#666;line-height:1.8">
        • Sector: <span style="color:#e8e8e8">{SECTOR_MAP.get(ticker,'Unknown')}</span><br>
        • Price Follows: <span style="color:#e8e8e8">{s.get('price_follows','—')}</span><br>
        • Rev 3Y CAGR: <span style="color:#00FF41">{fmt_pct(s.get('rev_3y_cagr'))}</span><br>
        • FCF TTM: <span style="color:#00e5ff">{fmt_num(s.get('fcf_ttm'), decimals=0)}</span><br>
        • Net Debt: <span style="color:{'#FF3030' if (s.get('net_debt_ttm') or 0)>0 else '#00FF41'}">{fmt_num(s.get('net_debt_ttm'), decimals=0)}</span>
        </div>""", unsafe_allow_html=True)

# ─── SCENARIOS TAB ───────────────────────────────────────────────────────────
def render_scenarios(ticker, s, ai):
    st.markdown('<div class="sh">🎯 BEAR / BASE / BULL SCENARIOS</div>', unsafe_allow_html=True)
    if ai and 'error' not in ai and ai.get('scenarios'):
        sc = ai['scenarios']
        c1, c2, c3 = st.columns(3)
        for col, key, label, css in [(c1,'bear','🐻 BEAR','scenario-bear'),(c2,'base','📊 BASE','scenario-base'),(c3,'bull','🐂 BULL','scenario-bull')]:
            d = sc.get(key, {})
            price = d.get('price', 0)
            ret = d.get('return_pct', '—')
            trigger = d.get('trigger', '—')
            with col:
                st.markdown(f"""
                <div class="{css}">
                  <div style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:600;margin-bottom:8px">{label}</div>
                  <div style="font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700;margin-bottom:4px">${price:,.0f}</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:14px;margin-bottom:12px">{ret}</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;text-align:left;line-height:1.5">{trigger}</div>
                </div>""", unsafe_allow_html=True)

        # Catalysts
        if ai.get('catalysts'):
            st.markdown('<div class="sh" style="margin-top:12px">⚡ CATALYST TIMELINE</div>', unsafe_allow_html=True)
            for c in ai.get('catalysts', []):
                h = c.get('horizon', 'MID')
                imp = c.get('impact', 'MEDIUM')
                hcls = 'timeline-near' if h=='NEAR' else 'timeline-mid' if h=='MID' else 'timeline-long'
                hcol = '#00FF41' if h=='NEAR' else '#FFB800' if h=='MID' else '#666'
                icol = '#FF3030' if imp=='HIGH' else '#FFB800' if imp=='MEDIUM' else '#00e5ff' if imp=='CONFIRMED' else '#666'
                st.markdown(f"""
                <div class="timeline-item {hcls}">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#e8e8e8;flex:1">{c.get('text','')}</span>
                    <span style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;margin:0 10px">{c.get('timing','')}</span>
                    <span style="background:{icol}22;border:1px solid {icol}44;color:{icol};font-family:JetBrains Mono,monospace;font-size:7px;padding:1px 5px;border-radius:2px">{imp}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("🤖 Add Gemini API key to generate Bear/Base/Bull scenarios and catalyst timeline.")
        # Show hypothesis from Excel
        hyp = s.get('hypothesis_price')
        if hyp:
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #00FF4133;border-radius:3px;padding:12px">
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;letter-spacing:2px;margin-bottom:4px">HYPOTHESIS PRICE (FROM EXCEL)</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#00FF41;line-height:1.6">{hyp}</div>
            </div>""", unsafe_allow_html=True)

# ─── RISK TAB ────────────────────────────────────────────────────────────────
def render_risk(ticker, s, ai, info):
    st.markdown('<div class="sh">⚠️ RISK MATRIX — PROBABILITY × IMPACT</div>', unsafe_allow_html=True)
    if ai and 'error' not in ai and ai.get('risks'):
        cols = st.columns(2)
        quadrants = [('HIGH PROB / HIGH IMPACT','HIGH','HIGH','risk-hi-hi','#FF3030'),
                     ('HIGH PROB / LOW IMPACT','HIGH','LOW','risk-hi-lo','#FFB800'),
                     ('LOW PROB / HIGH IMPACT','LOW','HIGH','risk-lo-hi','#FFB800'),
                     ('LOW PROB / LOW IMPACT','LOW','LOW','risk-lo-lo','#00FF41')]
        for i, (label, prob, imp, cls, bc) in enumerate(quadrants):
            items = [r for r in ai.get('risks',[]) if r.get('prob')==prob and r.get('imp')==imp]
            with cols[i%2]:
                html = f'<div class="{cls}" style="margin-bottom:8px"><div style="font-family:JetBrains Mono,monospace;font-size:8px;color:{bc};letter-spacing:1px;margin-bottom:8px">{label}</div>'
                if items:
                    for r in items:
                        sev = r.get('sev','🟡')
                        html += f'''<div style="background:#080808;border-radius:2px;padding:6px 8px;margin-bottom:4px;border-left:3px solid {"#FF3030" if sev=="🔴" else "#FFB800" if sev=="🟡" else "#00FF41"}">
                          <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#e8e8e8">{sev} {r.get("risk","")}</div>
                          <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;margin-top:2px">{r.get("detail","")}</div>
                        </div>'''
                else:
                    html += '<div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#333;font-style:italic">No items</div>'
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

        # Beta & short interest from live
        beta = info.get('beta'); short = (info.get('shortPercentOfFloat',0) or 0)*100
        if beta or short:
            st.markdown(f"""
            <div style="display:flex;gap:10px;margin-top:8px">
              <div class="metric-card" style="flex:1"><div class="metric-val" style="font-size:14px">{f"{beta:.2f}" if beta else "—"}</div><div class="metric-lbl">BETA</div></div>
              <div class="metric-card" style="flex:1"><div class="metric-val" style="font-size:14px">{f"{short:.1f}%"}</div><div class="metric-lbl">SHORT FLOAT</div></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("🤖 Add Gemini API key to generate risk matrix.")

# ─── DECISION TAB ────────────────────────────────────────────────────────────
def render_decision(ticker, s, ai, price):
    st.markdown('<div class="sh">💼 INVESTMENT DECISION BOX</div>', unsafe_allow_html=True)
    if ai and 'error' not in ai:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            sig = ai.get('signal','HOLD')
            sig_col = SIG_COLOR.get(sig,'#FFB800')
            grade = ai.get('grade','—')
            conviction = ai.get('conviction',3)
            st.markdown(f"""
            <div style="background:#0f0f0f;border:2px solid {sig_col};border-radius:4px;padding:16px">
              <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:2px;margin-bottom:4px">SIGNAL</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;color:{sig_col};font-weight:700;margin-bottom:10px">{sig}</div>
              {"".join([f'''<div style="display:flex;justify-content:space-between;border-bottom:1px solid #252525;padding:6px 0">
                <span style="font-family:JetBrains Mono,monospace;font-size:8px;color:#444;letter-spacing:1px">{k}</span>
                <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:{v_col}">{v}</span>
              </div>''' for k,v,v_col in [
                ('ENTRY', ai.get('entry','—'), sig_col),
                ('3Y TARGET', ai.get('target_3y','—'), '#00FF41'),
                ('3Y RETURN', ai.get('return_3y','—'), '#00FF41'),
                ('P.A. RETURN', ai.get('pa','—'), '#00FF41'),
                ('GRADE', grade, '#00e5ff'),
                ('CONVICTION', '★'*conviction+'☆'*(5-conviction), '#FFB800'),
                ('RISK SCORE', f"{ai.get('risk_score',50)}/100", '#FF3030'),
                ('ANTIGRAVITY', f"{ai.get('antigravity_score',50)}/100", '#b06bff'),
              ]])}
              <div style="margin-top:10px;font-family:JetBrains Mono,monospace;font-size:8px;color:#555;letter-spacing:2px">VERDICT</div>
              <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:{sig_col};line-height:1.5;margin-top:4px">{ai.get('verdict','—')}</div>
            </div>""", unsafe_allow_html=True)

        with col_r:
            if ai.get('key_edge'):
                st.markdown(f"""
                <div style="background:#0f0f0f;border:1px solid #00FF4133;border-radius:3px;padding:12px;margin-bottom:8px">
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;letter-spacing:2px;margin-bottom:5px">⚡ KEY EDGE</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#00FF41;line-height:1.6">{ai.get('key_edge','')}</div>
                </div>""", unsafe_allow_html=True)
            if ai.get('exit_trigger'):
                st.markdown(f"""
                <div style="background:#0f0f0f;border:1px solid #FF303033;border-radius:3px;padding:12px;margin-bottom:8px">
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#FF3030;letter-spacing:2px;margin-bottom:5px">🚪 EXIT TRIGGER</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#888;line-height:1.6">{ai.get('exit_trigger','')}</div>
                </div>""", unsafe_allow_html=True)
            if ai.get('watch'):
                st.markdown(f"""
                <div style="background:#0f0f0f;border:1px solid #FFB80033;border-radius:3px;padding:12px">
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#FFB800;letter-spacing:2px;margin-bottom:5px">👁 WATCH ITEM</div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#888;line-height:1.6">{ai.get('watch','')}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("🤖 Add Gemini API key for full investment decision analysis.")
        # Show from Excel
        hyp = s.get('hypothesis_price')
        pts = s.get('points') or s.get('reconcile')
        rec = s.get('recommendation','')
        st.markdown(f"""
        <div style="display:flex;gap:10px">
          <div class="metric-card green" style="flex:1"><div class="metric-val">{rec or '—'}</div><div class="metric-lbl">RECOMMENDATION</div></div>
          <div class="metric-card cyan" style="flex:1"><div class="metric-val">{f"{pts:.1f}/10" if pts else '—'}</div><div class="metric-lbl">PYKUPZ SCORE</div></div>
          <div class="metric-card" style="flex:2"><div class="metric-val" style="font-size:11px">{hyp or '—'}</div><div class="metric-lbl">HYPOTHESIS PRICE</div></div>
        </div>""", unsafe_allow_html=True)


# ─── PORTFOLIO OVERVIEW ───────────────────────────────────────────────────────
def render_portfolio_overview():
    st.markdown('<div class="pyk-header"><div class="pyk-logo">⚡ PYKUPZ — 78 STOCK UNIVERSE OVERVIEW</div><div class="pyk-sub">CITADEL GLOBAL EQUITIES · Q1 2026 · MARCH 2026</div></div>', unsafe_allow_html=True)

    # Summary metrics
    total = len(STOCKS)
    buy_count = sum(1 for s in STOCKS if 'buy' in str(s.get('recommendation','')).lower())
    watch_count = sum(1 for s in STOCKS if 'watch' in str(s.get('recommendation','')).lower())

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Stocks", total)
    c2.metric("Buy Signals", buy_count)
    c3.metric("Watch Signals", watch_count)
    c4.metric("AI Analyses", len(st.session_state.ai_cache))
    c5.metric("Last Update", datetime.now().strftime("%H:%M"))

    st.markdown("<br>", unsafe_allow_html=True)

    # Portfolio map
    fig = portfolio_scatter(STOCKS)
    st.plotly_chart(fig, use_container_width=True)

    # Master table
    st.markdown('<div class="sh">📋 MASTER STOCK TABLE — ALL 78 STOCKS</div>', unsafe_allow_html=True)

    rows = []
    for s in STOCKS:
        ticker = s['ticker']
        ai = st.session_state.ai_cache.get(f"analysis_{ticker}")
        rows.append({
            '#': s.get('sr',''),
            'Ticker': ticker,
            'Company': s['name'][:30],
            'Sector': SECTOR_MAP.get(ticker,'Unknown'),
            'PE': s.get('pe'),
            'PS': s.get('ps'),
            'MCap ($B)': s.get('mcap_b'),
            'Price': s.get('price'),
            'Rev Grw% LY': f"{float(s.get('rev_growth_ly',0))*100:.1f}%" if s.get('rev_growth_ly') else '—',
            'EPS CAGR': f"{float(s.get('eps_3y_cagr',0))*100:.1f}%" if s.get('eps_3y_cagr') else '—',
            'FCF TTM': s.get('fcf_ttm'),
            'Score': s.get('points') or s.get('reconcile'),
            'Rec (Excel)': s.get('recommendation',''),
            'AI Signal': ai.get('signal','—') if ai and 'error' not in ai else '—',
            'AI Grade': ai.get('grade','—') if ai and 'error' not in ai else '—',
        })

    df = pd.DataFrame(rows)
    # Format numeric columns
    for col in ['PE','PS','MCap ($B)','Price','FCF TTM','Score']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    st.dataframe(
        df.style.format({
            'PE': lambda x: f"{x:.1f}x" if pd.notna(x) else '—',
            'PS': lambda x: f"{x:.1f}x" if pd.notna(x) else '—',
            'MCap ($B)': lambda x: f"${x:.1f}B" if pd.notna(x) else '—',
            'Price': lambda x: f"${x:.2f}" if pd.notna(x) else '—',
            'FCF TTM': lambda x: f"${x:.0f}M" if pd.notna(x) else '—',
            'Score': lambda x: f"{x:.1f}" if pd.notna(x) else '—',
        }),
        use_container_width=True, height=600
    )

    # Sector breakdown
    st.markdown('<div class="sh" style="margin-top:12px">🏭 SECTOR BREAKDOWN</div>', unsafe_allow_html=True)
    sector_counts = {}
    for s in STOCKS:
        sec = SECTOR_MAP.get(s['ticker'],'Other')
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    df_sec = pd.DataFrame(list(sector_counts.items()), columns=['Sector','Count']).sort_values('Count', ascending=False)
    fig_sec = px.bar(df_sec, x='Count', y='Sector', orientation='h',
        color='Count', color_continuous_scale=[[0,'#1a1a1a'],[1,'#00FF41']])
    fig_sec.update_layout(**CHART_LAYOUT, height=350,
        title=dict(text="Stocks per Sector", font=dict(color='#00FF41', size=11)))
    fig_sec.update_xaxes(**GRID); fig_sec.update_yaxes(**GRID, tickfont=dict(size=9))
    st.plotly_chart(fig_sec, use_container_width=True)

    # MCap distribution
    mcap_cats = {}
    for s in STOCKS:
        cat = str(s.get('mcap_cat','')).strip() or 'Unknown'
        mcap_cats[cat] = mcap_cats.get(cat, 0) + 1
    if mcap_cats:
        df_mc = pd.DataFrame(list(mcap_cats.items()), columns=['Category','Count']).sort_values('Count', ascending=False)
        fig_mc = go.Figure(go.Pie(labels=df_mc['Category'], values=df_mc['Count'],
            hole=0.4, marker_colors=['#00FF41','#00e5ff','#FFB800','#FF3030','#b06bff','#ff6b9d']))
        fig_mc.update_layout(**CHART_LAYOUT, height=280,
            title=dict(text="MCap Category Distribution", font=dict(color='#00e5ff', size=11)))
        st.plotly_chart(fig_mc, use_container_width=True)

# ─── AI BATCH SCAN ────────────────────────────────────────────────────────────
def render_ai_scan(model):
    st.markdown('<div class="sh">🚀 ANTIGRAVITY SCANNER — AI RANKS ALL STOCKS</div>', unsafe_allow_html=True)

    if not model:
        st.info("🤖 Add Gemini API key to run the Antigravity Scanner across all 78 stocks.")
        return

    cached = {k.replace('analysis_',''):v for k,v in st.session_state.ai_cache.items() if 'error' not in v}
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        n = st.slider("Stocks to scan", 5, 20, 10, label_visibility="collapsed")
    with col_b:
        scan_mode = st.selectbox("Scan mode", ["Top by Score", "Random Sample", "Custom Selection"], label_visibility="collapsed")
    with col_c:
        run = st.button("🚀 RUN SCAN", use_container_width=True)

    if run:
        if scan_mode == "Top by Score":
            sorted_stocks = sorted([s for s in STOCKS if s.get('points')], key=lambda x: float(x.get('points',0)), reverse=True)[:n]
        else:
            sorted_stocks = STOCKS[:n]

        prog = st.progress(0, text="Scanning stocks...")
        for i, s in enumerate(sorted_stocks):
            t = s['ticker']
            if f"analysis_{t}" not in st.session_state.ai_cache:
                info = fetch_info(t)
                price, chg, vol = fetch_price(t)
                if price:
                    ai_result = ai_analyze_stock(model, t, s['name'], s, info, price, chg or 0)
            prog.progress((i+1)/len(sorted_stocks), text=f"Scanning {t}... ({i+1}/{len(sorted_stocks)})")
        prog.empty()
        st.success(f"✅ Scanned {len(sorted_stocks)} stocks. Results below.")
        st.rerun()

    # Show results
    if cached:
        results = [(t, v) for t, v in cached.items()]
        results.sort(key=lambda x: x[1].get('antigravity_score', 0), reverse=True)

        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#444">{len(results)} stocks analysed</div>', unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (ticker, ai) in enumerate(results[:12]):
            s_data = next((s for s in STOCKS if s['ticker']==ticker), {})
            ag = ai.get('antigravity_score',0)
            sig = ai.get('signal','HOLD')
            grade = ai.get('grade','—')
            sig_col = SIG_COLOR.get(sig,'#FFB800')
            ag_col = '#00FF41' if ag>=70 else '#FFB800' if ag>=40 else '#FF3030'
            with cols[i%3]:
                st.markdown(f"""
                <div style="background:#0f0f0f;border:1px solid {ag_col}33;border-top:2px solid {ag_col};border-radius:4px;padding:12px;margin-bottom:8px">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:{ag_col}">{ticker}</span>
                    <span style="font-family:JetBrains Mono,monospace;font-size:9px;color:#444">{SECTOR_MAP.get(ticker,'')}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                    <div><div style="font-family:JetBrains Mono,monospace;font-size:22px;color:{ag_col};line-height:1">{ag}</div>
                    <div style="font-family:JetBrains Mono,monospace;font-size:7px;color:#444">ANTIGRAVITY</div></div>
                    <div style="text-align:right">
                      <div style="font-family:JetBrains Mono,monospace;font-size:14px;color:{sig_col}">{sig}</div>
                      <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;color:#00e5ff;font-weight:700">{grade}</div>
                    </div>
                  </div>
                  <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#555;line-height:1.4">{ai.get('antigravity_reason','')[:80]}</div>
                </div>""", unsafe_allow_html=True)

# ─── AI CHAT ──────────────────────────────────────────────────────────────────
def render_chat(model):
    st.markdown('<div class="sh">💬 GEMINI AI CHAT — ASK ABOUT ANY STOCK</div>', unsafe_allow_html=True)
    if not model:
        st.info("🤖 Add Gemini API key in sidebar to use AI chat.")
        return

    # Chat history
    for h in st.session_state.chat_history[-10:]:
        role_icon = "🤖" if h['role']=='model' else "👤"
        bg = '#0a1422' if h['role']=='model' else '#0f0f0f'
        st.markdown(f"""<div style="background:{bg};border:1px solid #252525;border-radius:4px;padding:10px 14px;
          margin-bottom:6px;font-family:JetBrains Mono,monospace;font-size:10px;line-height:1.6;color:#e8e8e8">
          {role_icon} {h['content']}</div>""", unsafe_allow_html=True)

    user_q = st.text_input("Ask Gemini about any stock...",
        placeholder="e.g. Compare NVDA vs AMD PE, Is MELI a buy at current price?, Explain CRM moat, Which stocks have best FCF?",
        label_visibility="collapsed")
    col_a, col_b = st.columns([4, 1])
    with col_b:
        clear = st.button("Clear Chat")
    if clear:
        st.session_state.chat_history = []
        st.rerun()

    if user_q:
        ctx = f"Selected stock: {st.session_state.selected_ticker}. AI analyses available for: {list(st.session_state.ai_cache.keys())[:8]}. Universe: {len(STOCKS)} stocks including NVDA, MELI, CRM, ANET, NU, PLTR, META, GOOG, AMZN."
        with st.spinner("🤖 Gemini thinking..."):
            reply = ai_chat(model, user_q, ctx)
        st.session_state.chat_history.append({'role':'user','content':user_q})
        st.session_state.chat_history.append({'role':'model','content':reply})
        st.rerun()

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    # Gemini model
    model = get_gemini_model(st.session_state.gemini_key)

    # Navigation buttons at top
    c1,c2,c3,c4,c5 = st.columns(5)
    views = [('🏠 PORTFOLIO','portfolio'),('🚀 AI SCANNER','scanner'),('💬 AI CHAT','chat'),
             ('📋 WATCHLIST','watchlist'),('📡 LIVE','live')]
    for col, (lbl, view) in zip([c1,c2,c3,c4,c5], views):
        active = st.session_state.get('main_view','portfolio') == view
        if col.button(lbl, use_container_width=True, key=f"nav_{view}"):
            st.session_state.main_view = view
            st.rerun()

    main_view = st.session_state.get('main_view', 'portfolio')

    if main_view == 'portfolio':
        render_portfolio_overview()
        return
    if main_view == 'scanner':
        render_ai_scan(model)
        return
    if main_view == 'chat':
        render_chat(model)
        return

    # ── Individual Stock View ──
    ticker = st.session_state.selected_ticker
    s = next((x for x in STOCKS if x['ticker']==ticker), None)
    if not s:
        st.error(f"Stock {ticker} not found in universe.")
        return

    # Fetch live data
    with st.spinner(f"⚡ Loading {ticker}..."):
        price, chg, vol = fetch_price(ticker)
        info = fetch_info(ticker)
        if price is None:
            price = float(s.get('price', 0) or 0)
            chg = 0

    render_header(ticker, s, info, price, chg, vol)

    # AI analysis (if key available)
    ai = None
    if model and f"analysis_{ticker}" not in st.session_state.ai_cache:
        with st.spinner(f"🤖 Gemini analysing {ticker}..."):
            ai = ai_analyze_stock(model, ticker, s['name'], s, info, price, chg or 0)
    elif f"analysis_{ticker}" in st.session_state.ai_cache:
        ai = st.session_state.ai_cache[f"analysis_{ticker}"]

    # Tabs
    tabs = st.tabs(["📊 OVERVIEW", "📐 VALUATION", "📈 GROWTH & FCF", "🏰 MOAT",
                    "🎯 SCENARIOS", "⚠️ RISK MATRIX", "💼 DECISION", "📉 CHARTS"])
    tab_ov, tab_val, tab_gr, tab_moat, tab_sc, tab_risk, tab_dec, tab_chart = tabs

    with tab_ov:
        render_overview(ticker, s, info, price, chg, ai, model)
    with tab_val:
        fin = fetch_financials(ticker)
        render_valuation(ticker, s, info, fin)
    with tab_gr:
        fin = fetch_financials(ticker)
        render_growth(ticker, s, info, fin)
    with tab_moat:
        render_moat(ticker, s, ai)
    with tab_sc:
        render_scenarios(ticker, s, ai)
    with tab_risk:
        render_risk(ticker, s, ai, info)
    with tab_dec:
        render_decision(ticker, s, ai, price)
    with tab_chart:
        st.markdown('<div class="sh">📉 PRICE CHART</div>', unsafe_allow_html=True)
        hist = fetch_history(ticker, "5y")
        fig = price_chart(ticker, hist, info)
        st.plotly_chart(fig, use_container_width=True)
        # 1Y chart too
        hist1y = fetch_history(ticker, "1y")
        if not hist1y.empty:
            fig1y = price_chart(ticker, hist1y, info)
            fig1y.update_layout(title=dict(text=f"📈 {ticker} — 1 Year"))
            st.plotly_chart(fig1y, use_container_width=True)

    # AI re-analyse button
    if model:
        if st.button(f"🔄 Re-Analyse {ticker} with Gemini", use_container_width=False):
            cache_key = f"analysis_{ticker}"
            if cache_key in st.session_state.ai_cache:
                del st.session_state.ai_cache[cache_key]
            st.rerun()

if __name__ == "__main__":
    main()
