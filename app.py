import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG MONITOR 3.4", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Sidebar Style
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f0f2f6; border-right: 1px solid #d1d4d9; }
    .side-card {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
    .side-label { font-size: 0.75rem; font-weight: bold; color: #ff4b4b; text-transform: uppercase; }
    .side-val { font-size: 1.2rem; font-weight: bold; color: #1f1f1f; }
    .side-sub { font-size: 0.7rem; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# 4. Estate Logic
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Clementi": "West",
    "Jurong": "West", "Orchard": "Central", "Punggol": "North", "Tampines": "East",
    "Woodlands": "North", "Yishun": "North", "Bukit Merah": "South"
}

def get_weather(estate):
    region = ESTATES.get(estate, "Central")
    # NEA Forecast Mar 23: 35C Highs, Smoke Haze risk from Johor
    data = {
        "North": {"t": "34°C", "psi": 58, "st": "Warm/Hazy"},
        "South": {"t": "33°C", "psi": 49, "st": "Fair/Dry"},
        "East": {"t": "34°C", "psi": 62, "st": "Slightly Hazy"},
        "West": {"t": "35°C", "psi": 55, "st": "Very Warm"},
        "Central": {"t": "35°C", "psi": 52, "st": "Dry/Warm"}
    }
    return data[region]

# --- SIDEBAR: MONITOR & SETTINGS ---
with st.sidebar:
    st.title("🇸🇬 Monitor")
    
    # Selection
    st.write("### 🏠 Watchlist")
    e1 = st.selectbox("Select Estate 1", sorted(ESTATES.keys()), index=0)
    e2 = st.selectbox("Select Estate 2", sorted(ESTATES.keys()), index=7)
    
    st.divider()
    
    # Side Displays
    d1, d2 = get_weather(e1), get_weather(e2)
    
    for estate, data in [(e1, d1), (e2, d2)]:
        st.markdown(f"""
            <div class="side-card">
                <div class="side-label">{estate}</div>
                <div class="side-val">{data['t']} | PSI {data['psi']}</div>
                <div class="side-sub">{data['st']} ({ESTATES[estate]})</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')}")

# --- MAIN DASHBOARD: FINANCE & NEWS ---
st.title("Singapore Info Dashboard")

# Row 1: Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("London", "Europe/London"), ("Manila", "Asia/Manila"), ("New York", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Row 2: Economy & Forex
st.subheader("📊 Economic Data & Forex")
m1, m2, m3, m4 = st.columns(4)
m1.metric("STI INDEX", "3,254.10", "+12.45")
m2.metric("Core Inflation", "1.40%", "Feb Peak")
m3.metric("SGD/MYR", "3.072", "+0.02%")
m4.metric("SGD/CNY", "5.366", "-0.01%")

st.divider()

# Row 3: COE & News
n_col1, n_col2 = st.columns([2, 1])
with n_col1:
    st.subheader("📰 Headlines")
    st.markdown("• **CNA**: [NEA monitors haze risk as hotspots emerge in Johor](https://www.channelnewsasia.com)")
    st.markdown("• **ST**: [MAS to update inflation outlook as energy prices surge](https://www.straitstimes.com)")
    st.markdown("• **CNA**: [Singapore set for warmest week in March with 36°C peaks](https://www.channelnewsasia.com)")

with n_col2:
    st.subheader("🚗 COE Results")
    st.markdown("""
        <div style="background-color:#fff3cd; padding:10px; border-radius:8px; border-left:5px solid #ffc107;">
            <div style="font-size:0.8rem; font-weight:bold;">CAT A (Current)</div>
            <div style="font-size:1.5rem; font-weight:bold;">$111,890</div>
            <div style="font-size:0.7rem;">Next bidding: April 6</div>
        </div>
    """, unsafe_allow_html=True)
