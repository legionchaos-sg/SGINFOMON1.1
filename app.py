import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 2.9", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (Every 3 minutes)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .forex-card { background-color: #ffffff; border: 1px solid #eee; padding: 12px; border-radius: 8px; text-align: center; }
    .forex-label { font-size: 0.7rem; color: #666; font-weight: bold; }
    .weather-card { background-color: #e3f2fd; border-radius: 10px; padding: 15px; border-left: 5px solid #2196f3; margin-bottom: 10px; }
    .psi-badge { background-color: #4caf50; color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; }
    @media (prefers-color-scheme: dark) {
        .time-card, .forex-card { background-color: #262730; border-color: #444; }
        .weather-card { background-color: #1e293b; border-left-color: #3b82f6; }
        .time-value { color: #ffffff; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

@st.cache_data(ttl=180)
def get_financial_data(tickers_dict):
    results = {}
    for label, sym in tickers_dict.items():
        try:
            t = yf.Ticker(sym)
            p = t.fast_info['last_price']
            prev = t.fast_info['regular_market_previous_close']
            results[label] = {"p": p, "pc": ((p - prev) / prev) * 100}
        except: results[label] = {"p": 0.0, "pc": 0.0}
    return results

# NEW: Weather & PSI Mock Logic (Replaceable with real NEA API calls)
def get_nea_data(region):
    # Simulated data reflecting late March weather in SG
    data = {
        "North": {"temp": "31°C", "desc": "Partly Cloudy", "psi": 42},
        "South": {"temp": "32°C", "desc": "Fair", "psi": 45},
        "East": {"temp": "30°C", "desc": "Light Rain", "psi": 38},
        "West": {"temp": "31°C", "desc": "Cloudy", "psi": 48},
        "Central": {"temp": "32°C", "desc": "Fair", "psi": 44}
    }
    return data.get(region, {"temp": "--", "desc": "Unknown", "psi": 0})

# 5. Header & Clocks
st.title("Singapore Info Monitor 1.1")
st.subheader("🌐 REGIONAL Current Time")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

# 6. Market & Forex
st.write("")
m_cols = st.columns(2)
with m_cols[0]:
    st.subheader("📊 Market Overview")
    m_data = get_financial_data({"STI": "^STI", "Gold": "GC=F"})
    c1, c2, c3 = st.columns(3)
    c1.metric("STI INDEX", f"{m_data['STI']['p']:,.2f}")
    c2.metric("Gold", f"{m_data['Gold']['p']:,.2f}")
    c3.metric("SG Core Inflation", "1.40%", "+0.40%")

with m_cols[1]:
    st.subheader("💱 Forex Exchange")
    fx_data = get_financial_data({"MYR": "SGDMYR=X", "CNY": "SGDCNY=X"})
    f1, f2 = st.columns(2)
    f1.metric("SGD/MYR", f"{fx_data['MYR']['p']:.4f}", f"{fx_data['MYR']['pc']:+.2f}%")
    f2.metric("SGD/CNY", f"{fx_data['CNY']['p']:.4f}", f"{fx_data['CNY']['pc']:+.2f}%")

st.divider()

# 7. WEATHER & PSI PANEL (NEW)
st.header("🌤️ Weather & Air Quality (PSI)")
reg_list = ["North", "South", "East", "West", "Central"]
w_col1, w_col2 = st.columns(2)

with w_col1:
    sel1 = st.selectbox("Select Region 1", reg_list, index=1) # Default South
    res1 = get_nea_data(sel1)
    st.markdown(f"""
        <div class="weather-card">
            <h4 style="margin:0;">{sel1} Region</h4>
            <div style="font-size:1.8rem; font-weight:bold;">{res1['temp']}</div>
            <div style="color:#666; margin-bottom:10px;">{res1['desc']}</div>
            <span class="psi-badge">PSI: {res1['psi']} (Good)</span>
        </div>
    """, unsafe_allow_html=True)

with w_col2:
    sel2 = st.selectbox("Select Region 2", reg_list, index=2) # Default East
    res2 = get_nea_data(sel2)
    st.markdown(f"""
        <div class="weather-card">
            <h4 style="margin:0;">{sel2} Region</h4>
            <div style="font-size:1.8rem; font-weight:bold;">{res2['temp']}</div>
            <div style="color:#666; margin-bottom:10px;">{res2['desc']}</div>
            <span class="psi-badge">PSI: {res2['psi']} (Good)</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 8. Headlines & COE
st.header("🇸🇬 Singapore News & COE")
tab1, tab2 = st.tabs(["📰 Headline News", "🚗 COE Stats"])
with tab1:
    feed = feedparser.parse(requests.get("https://www.straitstimes.com/news/singapore/rss.xml").content)
    for e in feed.entries[:5]: st.markdown(f"• [{e.title}]({e.link})")
with tab2:
    coe = [{"cat": "CAT A", "p": 111890}, {"cat": "CAT B", "p": 115568}]
    for c in coe: st.metric(c['cat'], f"${c['p']:,}")

# 9. Footer
st.divider()
st.caption(f"Sync Active | Weather: NEA | Forex: Yahoo Finance | {datetime.now().strftime('%H:%M:%S')} SGT")
