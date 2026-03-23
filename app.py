import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.1", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card {
        background-color: #f8f9fa; border: 1px solid #e9ecef;
        padding: 10px; border-radius: 8px; text-align: center;
    }
    .time-city { 
        font-size: 0.75rem; color: #ff4b4b; /* RED TEXT */
        font-weight: bold; text-transform: uppercase; margin-bottom: 2px;
    }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .forex-card {
        background-color: #ffffff; border: 1px solid #eee; 
        padding: 12px; border-radius: 8px; text-align: center;
    }
    .coe-card {
        background-color: #f8f9fa; border-top: 4px solid #ff4b4b;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
    .coe-value { font-size: 1.3rem; font-weight: bold; color: #d32f2f; }
    @media (prefers-color-scheme: dark) {
        .time-card, .forex-card, .coe-card { background-color: #262730; border-color: #333; }
        .time-value, .forex-price { color: #ffffff; }
        .coe-value { color: #ff5252; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    try:
        return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")
    except: return "00:00"

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

def fetch_feed(url):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        return [{"t": e.title, "l": e.link, "d": e.get('published', 'Recent')} for e in f.entries]
    except: return []

# 5. REGIONAL Current Time Panel
st.title("Singapore Info Monitor 1.1")
st.subheader("🌐 REGIONAL Current Time")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]

for i, (city, tz) in enumerate(zones):
    with t_cols[i]:
        st.markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

# 6. Market Overview
st.write("")
st.subheader("📊 Market Overview")
m_tickers = {"STI": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Crude": "CL=F"}
m_data = get_financial_data(m_tickers)
m_cols = st.columns(5)
market_items = [("STI INDEX", "STI"), ("Gold Price", "Gold"), ("Silver Price", "Silver"), ("Crude
