import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.0", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (Every 3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .status-card { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px; }
    .status-normal { background-color: #28a745; }
    .status-advisory { background-color: #ffc107; color: #212529; }
    .forex-card { background-color: #ffffff; border: 1px solid #eee; padding: 12px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .forex-label { font-size: 0.7rem; color: #666; font-weight: bold; }
    .forex-price { font-size: 1.1rem; font-weight: bold; margin: 4px 0; }
    @media (prefers-color-scheme: dark) {
        .time-card, .forex-card { background-color: #262730; border-color: #333; }
        .time-value, .forex-price { color: #ffffff; }
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

# 5. HEADER & CLOCKS
st.title("Singapore Info Monitor 3.0")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz
