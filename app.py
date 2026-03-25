import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# SG INFO MONITOR - Weather & Market Update 10.9.4 (gold 10)

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# 2. Adaptive CSS (Reduced fonts by 10pts for gold 10)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); font-size: 0.8rem; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 5px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); font-size: 0.75rem; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; color: var(--text-color); line-height: 1.1; font-size: 0.75rem; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 8px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.1; font-size: 0.75rem; }
    .news-tag { font-size: 0.6rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.75rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.75rem; }
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 0.9rem !important; }
    .weather-box { background: var(--secondary-background-color); border-radius: 10px; padding: 10px; text-align: center; border: 1px solid var(--border-color); font-size: 0.75rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. LIVE DATA ENGINE (NEW INTEGRATION)
def get_live_market_data():
    tickers = {"STI Index": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Brent": "BZ=F", "Nat Gas": "NG=F", "USD/SGD": "USDSGD=X"}
    results = {}
    for label, sym in tickers.items():
        try:
            data = yf.Ticker(sym).history(period="2d")
            latest, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
            results[label] = {"val": latest, "chg": ((latest - prev) / prev) * 100}
        except: results[label] = {"val": 0.0, "chg": 0.0}
    return results

def get_upcoming_holiday():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz).date()
    holidays_2026 = [("Good Friday", datetime(2026, 4, 3).date()), ("Labour Day", datetime(2026, 5, 1).date())] # Simplified for brevity
    for name, h_date in holidays_2026:
        if h_date >= now: return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9 (gold 10)")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🔮 COE STRATEGIC", "✈️ AIRFARE ENGINE"])

# ==========================================
# TAB 1: LIVE MONITOR (INTEGRATED FEED)
# ==========================================
with tab1:
    # 1. World Clocks
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    
    # 2. Live Market Indices (REAL FEED)
    live_feeds = get_live_market_data()
    with st.expander("📈 Live Market Indices & Commodities", expanded=True):
        m_cols = st.columns(6)
        m_cols[0].metric("STI Index", f"{live_feeds['STI Index']['val']:,.2f}", f"{live_feeds['STI Index']['chg']:.2f}%")
        m_cols[1].metric("Gold (Spot)", f"${live_feeds['Gold']['val']:,.1f}", f"{live_feeds['Gold']['chg']:.2f}%")
        m_cols[2].metric("Silver", f"${live_feeds['Silver']['val']:.2f}", f"{live_feeds['Silver']['chg']:.2f}%")
        m_cols[3].metric("Brent Crude", f"${live_feeds['Brent']['val']:.2f}", f"{live_feeds['Brent']['chg']:.2f}%")
        m_cols[4].metric("USD/SGD", f"{live_feeds['USD/SGD']['val']:.4f}", f"{live_feeds['USD/SGD']['chg']:.2f}%")
        m_cols[5].metric("SG Inflation", "1.40%", "+0.40%", help="MAS Core YoY")

    # 3. Fuel Prices (SHELL 5-CENT CUT LOGIC)
    with st.expander("⛽ Fuel Prices (Avg with Shell Correction)", expanded=True):
        # Base prices Mar 25th before Shell cut
        fuel_base = {"92 Octane": 3.43, "95 Octane": 3.47, "98 Octane": 3.98, "Premium": 4.15, "Diesel": 3.73}
        fc = st.columns(5)
        for i, (ftype, price) in enumerate(fuel_base.items()):
            # Dynamic calculation: Shell 5-cent cut applies to 95/98/Premium
            adj_price = price - 0.05 if ftype != "Diesel" and ftype != "92 Octane" else price
            status = "📉 Shell -5¢" if ftype in ["95 Octane", "98 Octane"] else "Stable"
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1rem;font-weight:bold;">${adj_price:.2f}</span><br><small>{status}</small></div>', unsafe_allow_html=True)

    st.divider()

    # 4. News Feed (Existing Logic)
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)
    # ... [Insert your existing news_list looping logic here] ...

# ==========================================
# CODE FREEZE: TABS 2-5 (No logic/display changes)
# ==========================================
with tab2:
    st.header("🏢 Government & Public Services")
    # ... [Rest of your Tab 2 code] ...

with tab3:
    st.header("🎯 Tactical Trade Scheduler")
    # ... [Rest of your Tab 3 code] ...

with tab4:
    st.header("🤖 COE Intelligence & Feasibility")
    # ... [Rest of your Tab 4 code] ...

with tab5:
    st.header("✈️ Global Airfare Prediction Engine")
    # ... [Rest of your Tab 5 code] ...
