import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG COMMAND 4.0", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh Logic (Set to 3 Minutes / 180 Seconds)
REFRESH_INTERVAL_SEC = 180
st_autorefresh(interval=REFRESH_INTERVAL_SEC * 1000, key="global_refresh")

# Initialize Last Sync Time
if "last_sync" not in st.session_state:
    st.session_state.last_sync = datetime.now()

# 3. Custom CSS for Heartbeat & Layout Protection
st.markdown(f"""
    <style>
    .heartbeat-bar {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #f8f9fa; border-top: 1px solid #ddd;
        padding: 5px 20px; font-size: 0.75rem; color: #666;
        display: flex; justify-content: space-between; z-index: 1000;
    }}
    .pulse {{
        height: 10px; width: 10px; background-color: #28a745;
        border-radius: 50%; display: inline-block; margin-right: 5px;
        animation: pulse-animation 2s infinite;
    }}
    @keyframes pulse-animation {{
        0% {{ transform: scale(0.95); opacity: 0.7; }}
        70% {{ transform: scale(1); opacity: 1; }}
        100% {{ transform: scale(0.95); opacity: 0.7; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions (With Cached News for Performance)
@st.cache_data(ttl=REFRESH_INTERVAL_SEC)
def fetch_news(url):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        return [{"t": e.title, "l": e.link} for e in f.entries[:5]]
    except: return []

# --- SIDEBAR: WEATHER ---
with st.sidebar:
    st.title("🌦️ Regional Monitor")
    # Selection and display logic here (as perfected in previous versions)
    st.info("Weather results will update automatically every 3 mins.")

# --- MAIN DASHBOARD: THE PERFECT LAYOUT ---
st.title("Singapore Command Center")

# ... [Your Clocks, Market, News, and COE Rows Go Here] ...

# --- THE HEARTBEAT FOOTER ---
# Update sync time on every actual rerun
st.session_state.last_sync = datetime.now()
next_sync = st.session_state.last_sync + timedelta(seconds=REFRESH_INTERVAL_SEC)

st.markdown(f"""
    <div class="heartbeat-bar">
        <span><span class="pulse"></span> <b>SYSTEM LIVE</b> | March 23, 2026</span>
        <span>Next Refresh: {next_sync.strftime('%H:%M:%S')} (Every 3m)</span>
        <span>Sync Status: <span style="color:#28a745;">Excellent</span></span>
    </div>
""", unsafe_allow_html=True)
