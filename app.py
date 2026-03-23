import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 2.9", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling (Enhanced for Train Status)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .status-card { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.9rem; }
    .status-normal { background-color: #28a745; }
    .status-delay { background-color: #ffc107; color: #212529; }
    .status-disruption { background-color: #dc3545; }
    .forex-card { background-color: #ffffff; border: 1px solid #eee; padding: 12px; border-radius: 8px; text-align: center; }
    @media (prefers-color-scheme: dark) {
        .time-card, .forex-card { background-color: #262730; border-color: #333; }
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
            results[label] = {"p": p, "change": p - prev, "pc": ((p - prev) / prev) * 100}
        except: results[label] = {"p": 0.0, "change": 0.0, "pc": 0.0}
    return results

def fetch_news(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=5, headers=headers)
        return feedparser.parse(response.content)
    except: return None

# Mock function for Train Status (In production, replace with LTA DataMall API call)
def get_train_status():
    # Example logic: Return 'Normal' or 'Advisory'
    # real_api_url = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
    lines = {
        "NSL": "Normal", "EWL": "Normal", "NEL": "Normal", 
        "CCL": "Advisory", "DTL": "Normal", "TEL": "Normal"
    }
    advisories = {"CCL": "Tunnel works: Mtbatten to Paya Lebar"}
    return lines, advisories

# 5. Header & Clocks
st.title("Singapore Info Monitor 2.9")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# --- NEW: Train Service Status Panel ---
st.subheader("🚇 MRT/LRT Service Status")
train_lines, train_adv = get_train_status()
s_cols = st.columns(6)
for i, (line, status) in enumerate(train_lines.items()):
    bg_class = "status-normal" if status == "Normal" else "status-delay"
    icon = "✅" if status == "Normal" else "⚠️"
    s_cols[i].markdown(f'<div class="status-card {bg_class}">{line}<br>{icon} {status}</div>', unsafe_allow_html=True)

if train_adv:
    for line, msg in train_adv.items():
        st.warning(f"**{line} Advisory:** {msg}")

st.divider()

# 6. Market & 7. Forex (Consolidated for space)
col_m, col_f = st.columns([1, 1])
with col_m:
    st.subheader("📊 Markets")
    m_data = get_financial_data({"STI": "^STI", "Gold": "GC=F"})
    st.metric("STI INDEX", f"{m_data['STI']['p']:,.2f}", f"{m_data['STI']['change']:+.2f}")
    st.metric("Gold Price", f"{m_data['Gold']['p']:,.2f}", f"{m_data['Gold']['change']:+.2f}")

with col_f:
    st.subheader("💱 Forex (1 SGD)")
    fx_data = get_financial_data({"MYR": "SGDMYR=X", "CNY": "SGDCNY=X"})
    st.metric("MYR (Malaysia)", f"{fx_data['MYR']['p']:.4f}", f"{fx_data['MYR']['pc']:+.2f}%")
    st.metric("CNY (China)", f"{fx_data['CNY']['p']:.4f}", f"{fx_data['CNY']['pc']:+.2f}%")

st.divider()

# 8. News Section
st.header("🇸🇬 Singapore Headline News")
sources = {
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Mothership": "https://mothership.sg/feed/",
    "Shin Min (新明)": "https://www.zaobao.com.sg/rss/realtime/singapore"
}
tab1, tab2 = st.tabs(["📊 Unified", "📰 Select Source"])
with tab1:
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries:
            st.markdown(f"**{name}**: [{feed.entries[0].title}]({feed.entries[0].link})")
with tab2:
    sel = st.selectbox("Source", list(sources.keys()))
    feed = fetch_news(sources[sel])
    if feed:
        for e in feed.entries[:5]: st.write(f"• [{e.title}]({e.link})")

st.divider()
st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')} SGT | Data: LTA DataMall / Yahoo Finance")
