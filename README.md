# ⚡ PYKUPZ TERMINAL — 78 Stock Universe
### Citadel Global Equities · Q1 2026 · Institutional Research Terminal

Bloomberg-inspired live terminal covering all 78 stocks from the Pyk-Inv-List with:
- 🤖 **Gemini AI analysis** — thesis, moat, scenarios, risk matrix per stock
- 📊 **Live data** from yfinance (prices, financials, balance sheet)
- 🚀 **Antigravity Scanner** — AI ranks all stocks by momentum & strength
- 📐 **Valuation Dashboard** — PE, PS, GAPS, GAPE, hypothesis prices
- 📈 **Growth & FCF** — Revenue/EBITDA/EPS/FCF trajectory charts
- 🏰 **Moat Architecture** — AI-generated ★★★★★ moat ratings
- 💼 **Decision Box** — Entry, target, exit trigger per stock
- ⚠️ **Risk Matrix** — 2×2 probability × impact framework

---

## ⚡ INSTANT RUN (Streamlit Cloud)

1. Fork this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. New app → select your repo → `app.py`
4. In **Secrets**, add:
   ```toml
   GEMINI_API_KEY = "AIza..."
   ```
5. Deploy!

**Get free Gemini API key:** [aistudio.google.com](https://aistudio.google.com)

---

## 💻 LOCAL RUN

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
streamlit run app.py
```

---

## 📁 FILES

| File | Purpose |
|------|---------|
| `app.py` | Complete Streamlit terminal (1,451 lines) |
| `stocks_data.json` | 78 stocks from Pyk-Inv-List.xlsx with all metrics |
| `requirements.txt` | Python dependencies |

---

## 🎯 78 STOCKS COVERED

NVDA, ANET, PLTR, HUBS, HIMS, LLY, PMRTY, CRWD, DKNG, APP, AFRM, ONON, SHOP, NU, NFLX, AVGO, SPOT, META, MU, FTNT, SOFI, ALAB, AMD, RDDT, TTD, AMZN, ROKU, MELI, PANW, XYZ, TSM, GOOG, MSFT, JD, VEEV, ASML, IREN, BKNG, UBER, HOOD, BABA, ARGX, NET, DUOL, ELF, AXP, ISRG, DOCS, RYCEY, ETSY, UPWK, BRK.B, CRWV, COIN, IBKR, BYDDY, UPST, CRM, NVO, WPLCF, KNSL, ETOR, MGNI, AAPL, PDD, BIDU, TCEHY, MAR, ON, DOCU, TSLA, ENPH, Peri, TCOM, FUBO, GCT, LC, NBIS

---

## ⌨️ HOW TO USE

1. **Sidebar** → search/filter 78 stocks, click to open tear sheet
2. **Add Gemini key** → unlocks AI thesis, moat, scenarios, risk matrix
3. **Portfolio tab** → overview map + master table
4. **AI Scanner** → scan top stocks for antigravity signals
5. **AI Chat** → ask anything about the portfolio

---

*PYKUPZ Terminal · Citadel Global Equities · Not Financial Advice · Data: yfinance + Pyk-Inv-List.xlsx*
