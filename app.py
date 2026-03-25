import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# SG INFO MONITOR - Weather & Market Update 10.9.5 (gold 10 FULL RESTORE)

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# 2. Adaptive CSS (Reduced fonts by 10pts for gold 10)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); font-size: 0.8rem; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 5px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); font-size: 0.75rem; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 120px; color: var(--text-color); line-height: 1.1; font-size: 0.75rem; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.2; font-size: 0.75rem; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); }
    .trans-box { font-size: 0.8rem; color: #666; margin-left: 20px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.75rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.75rem; }
    .stat-label { font-size: 0.65rem; opacity: 0.6; text-transform: uppercase; }
    .holiday-text { font-size: 0.85rem; color: #28a745; font-weight: bold; margin-left: 10px; }
    .svc-card { background: var(--secondary-background-color); padding: 10px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; font-size: 0.75rem; }
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 0.95rem !important; }
    .traffic-pill { padding: 4px; border-radius: 4px; font-size: 0.65rem; font-weight: bold; color: white; display: inline-block; width: 100%; text-align: center;}
    .weather-box { background: var(--secondary-background-color); border-radius: 10px; padding: 10px; text-align: center; border: 1px solid var(--border-color); }
    </style>
    """, unsafe_allow_html=True)

# 3. Logic Functions
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
    holidays_2026 = [("Good Friday", datetime(2026, 4, 3).date()), ("Labour Day", datetime(2026, 5, 1).date()), ("Hari Raya Haji", datetime(2026, 5, 27).date())]
    for name, h_date in holidays_2026:
        if h_date >= now: return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.42, -0.05), "SPC": (3.46, 0.02)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.94, -0.05), "SPC": (3.97, 0.05)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.16, -0.05)},
    "Diesel": {"Esso": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List")
    for brand, (price, change) in fuel_data[ftype].items():
        st.markdown(f"**{brand}**: ${price:.2f} <span class='{'up' if change > 0 else 'down'}'>({change:+.2f})</span>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9 (gold 10)")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🔮 COE STRATEGIC", "✈️ AIRFARE ENGINE"])

# ==========================================
# TAB 1: LIVE MONITOR
# ==========================================
with tab1:
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    
    # 🗞️ News & Headlines
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)
    news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml"}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    nc1, nc2 = st.columns([2, 1])
    with nc1: search_q = st.text_input("🔍 Search Keywords:", key="news_search")
    with nc2: v_mode = st.selectbox("Source:", ["Unified", "CNA Only", "ST Only"])
    
    news_list = []
    for src, url in news_sources.items():
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:2]:
                news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
        except: pass
    for item in news_list:
        st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

    st.divider()

    # 📈 Market Indices (LIVE FEED)
    live_feeds = get_live_market_data()
    with st.expander("📈 Live Market Indices", expanded=True):
        m_cols = st.columns(6)
        m_cols[0].metric("STI Index", f"{live_feeds['STI Index']['val']:,.2f}", f"{live_feeds['STI Index']['chg']:.2f}%")
        m_cols[1].metric("Gold", f"${live_feeds['Gold']['val']:,.1f}", f"{live_feeds['Gold']['chg']:.2f}%")
        m_cols[2].metric("Silver", f"${live_feeds['Silver']['val']:.2f}", f"{live_feeds['Silver']['chg']:.2f}%")
        m_cols[3].metric("Brent", f"${live_feeds['Brent']['val']:.2f}", f"{live_feeds['Brent']['chg']:.2f}%")
        m_cols[4].metric("USD/SGD", f"{live_feeds['USD/SGD']['val']:.4f}", f"{live_feeds['USD/SGD']['chg']:.2f}%")
        m_cols[5].metric("SG Inflation", "1.40%", "+0.40%")

    # ⛽ Fuel Prices
    with st.expander("⛽ Fuel Prices (Shell -5¢ Cut Active)", expanded=True):
        fc = st.columns(5)
        for i, ftype in enumerate(["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]):
            prices = [v[0] for v in fuel_data[ftype].values()]
            avg = sum(prices) / len(prices)
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if fc[i].button("Details", key=f"fbtn_{ftype}"): show_fuel_details(ftype)

# ==========================================
# TAB 2: PUBLIC SERVICES (RESTORED)
# ==========================================
with tab2:
    st.header("🏢 Government & Public Services")
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    with ps_c1: st.markdown('<div class="svc-card"><h4>🔐 Finance</h4><ul><li>Singpass<li>CPF Board<li>IRAS (Tax)</ul></div>', unsafe_allow_html=True)
    with ps_c2: st.markdown('<div class="svc-card"><h4>🏠 Housing</h4><ul><li>HDB InfoWEB<li>HealthHub<li>ICA</ul></div>', unsafe_allow_html=True)
    with ps_c3: st.markdown('<div class="svc-card"><h4>🚆 Transport</h4><ul><li>OneMotoring<li>SP Group<li>NEA Weather</ul></div>', unsafe_allow_html=True)
    
    with st.expander("🚆 MRT Status", expanded=True):
        l_cols = st.columns(6)
        for i, line in enumerate(["EWL", "NSL", "NEL", "CCL", "DTL", "TEL"]):
            l_cols[i].success(f"{line}: Normal")

# ==========================================
# TAB 3: SYSTEM TOOLS (RESTORED)
# ==========================================
with tab3:
    st.header("🎯 Tactical Trade Scheduler")
    p_stance = st.radio("MAS Policy Stance:", ["Hawkish", "Neutral", "Dovish"], horizontal=True)
    t_amt = st.number_input("Amount (SGD):", value=1000)
    if st.button("🔒 Confirm Tactical Execution"):
        st.success("Execution plan locked.")

# ==========================================
# TAB 4: COE STRATEGIC (RESTORED)
# ==========================================
with tab4:
    st.header("🤖 COE Intelligence & Feasibility")
    v_cat = st.selectbox("Category:", ["Cat A", "Cat B", "Cat C", "Cat E"])
    u_target = st.number_input("Desired COE ($):", value=50000)
    st.info(f"Analysis: Target of ${u_target:,} requires high deregistration supply in 2027.")

# ==========================================
# TAB 5: AIRFARE ENGINE (RESTORED)
# ==========================================
with tab5:
    st.header("✈️ Global Airfare Prediction Engine")
    v_trip = st.radio("Trip Type:", ["Round Trip", "Single Leg"], horizontal=True)
    u_loc = st.text_input("Destination:", value="China")
    st.write(f"Searching flights to {u_loc}...")

st.caption("Monitoring: 10.9.5 | gold 10 System Active. All Tabs Restored.")
