import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.9", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .status-card { padding: 12px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.85rem; margin-bottom: 10px; }
    .status-normal { background-color: #28a745; }
    .status-advisory { background-color: #ffc107; color: #212529; }
    .coe-card { background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 8px; margin-bottom: 10px; min-height: 160px; }
    .coe-price { font-size: 1.3rem; font-weight: bold; color: #d32f2f; }
    @media (prefers-color-scheme: dark) {
        .time-card, .coe-card { background-color: #262730; border-color: #444; }
        .time-value { color: #ffffff; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Helper Functions
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

# --- UI START ---
st.title("Singapore Info Monitor 3.9")

# Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# News (Top)
st.header("🇸🇬 Singapore Headline News")
sources = {"Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Business Times": "https://www.businesstimes.com.sg/rss-feeds/singapore", "Mothership": "https://mothership.sg/feed/", "Shin Min": "https://www.zaobao.com.sg/rss/realtime/singapore"}
t_news1, t_news2 = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])
with t_news1:
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries: st.markdown(f"**{name}**: [{feed.entries[0].title}]({feed.entries[0].link})")
with t_news2:
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    feed = fetch_news(sources[sel])
    if feed and feed.entries:
        for e in feed.entries[:6]: st.write(f"• [{e.title}]({e.link})")

st.divider()

# 1. DROPDOWN: TRAIN STATUS (MODIFIED)
with st.expander("🚇 MRT/LRT Service Status", expanded=True):
    train_lines = {"NSL": "Normal", "EWL": "Normal", "NEL": "Normal", "CCL": "Advisory", "DTL": "Normal", "TEL": "Normal"}
    s_cols = st.columns(6)
    for i, (line, status) in enumerate(train_lines.items()):
        bg = "status-normal" if status == "Normal" else "status-advisory"
        icon = "✅" if status == "Normal" else "⚠️"
        s_cols[i].markdown(f'<div class="status-card {bg}">{line}<br>{icon} {status}</div>', unsafe_allow_html=True)
    
    if "Ad
