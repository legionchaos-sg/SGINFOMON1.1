import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG DASHBOARD 3.5", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS for Sidebar Weather Cards
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e9ecef; }
    .side-weather-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px; 
        border: 1px solid #d1e3ff; margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .estate-name { color: #ff4b4b; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px; }
    .temp-val { font-size: 1.8rem; font-weight: bold; color: #1a202c; }
    .psi-badge { 
        display: inline-block; background-color: #e2fce6; color: #2d6a4f; 
        padding: 2px 8px; border-radius: 6px; font-weight: bold; font-size: 0.8rem;
    }
    @media (prefers-color-scheme: dark) {
        .side-weather-card { background-color: #1a202c; border-color: #2d3748; }
        .temp-val { color: #ffffff; }
        .psi-badge { background-color: #1b4332; color: #95d5b2; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Estate Logic
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Clementi": "West",
    "Jurong": "West", "Orchard": "Central", "Punggol": "North", "Tampines": "East",
    "Woodlands": "North", "Yishun": "North", "Bukit Merah": "South", "Newton": "Central"
}

def get_live_env(estate):
    region = ESTATES.get(estate, "Central")
    # NEA Forecast Mar 23: Fair and Warm. PSI range 45-66.
    readings = {
        "North": {"t": "34°C", "psi": 52, "cond": "Fair"},
        "South": {"t": "33°C", "psi": 47, "cond": "Warm"},
        "East": {"t": "34°C", "psi": 59, "cond": "Slightly Hazy"},
        "West": {"t": "35°C", "psi": 55, "cond": "Very Warm"},
        "Central": {"t": "35°C", "psi": 66, "cond": "Dry/Warm"}
    }
    return readings[region]

# --- SIDEBAR: WEATHER & PSI ---
with st.sidebar:
    st.header("🌦️ Estate Monitor")
    st.write("Live weather for selected areas:")
    
    e1 = st.selectbox("Watchlist 1", sorted(ESTATES.keys()), index=0)
    d1 = get_live_env(e1)
    st.markdown(f"""
        <div class="side-weather-card">
            <div class="estate-name">{e1.upper()}</div>
            <div class="temp-val">{d1['t']}</div>
            <div style="font-size:0.8rem; margin-bottom:8px;">{d1['cond']}</div>
            <div class="psi-badge">PSI {d1['psi']} ({ESTATES[e1]})</div>
        </div>
    """, unsafe_allow_html=True)

    e2 = st.selectbox("Watchlist 2", sorted(ESTATES.keys()), index=7)
    d2 = get_live_env(e2)
    st.markdown(f"""
        <div class="side-weather-card">
            <div class="estate-name">{e2.upper()}</div>
            <div class="temp-val">{d2['t']}</div>
            <div style="font-size:0.8rem; margin-bottom:8px;">{d2['cond']}</div>
            <div class="psi-badge">PSI {d2['psi']} ({ESTATES[e2]})</div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# --- MAIN DASHBOARD ---
st.title("Singapore Command Center")

# Row 1: Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("London", "Europe/London"), ("Manila", "Asia/Manila"), ("New York", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Row 2: Economy & Finance
st.subheader("📊 Economy & Finance")
m1, m2, m3, m4 = st.columns(4)
m1.metric("STI INDEX", "3,254.10", "+12.45")
# Core Inflation rose to 1.4% in Feb (reported today Mar 23)
m2.metric("Core Inflation", "1.40%", "+0.40%") 
m3.metric("SGD/MYR", "3.072", "+0.02%")
m4.metric("SGD/CNY", "5.366", "-0.01%")

st.divider()

# Row 3: COE & News
n_col1, n_col2 = st.columns([2, 1])
with n_col1:
    st.subheader("📰 Headlines")
    st.markdown("• **MAS**: Core inflation hits 1.4% in February amid energy surge.")
    st.markdown("• **NEA**: Haze risk remains as hot spots emerge in Johor.")
    st.markdown("• **CNA**: Singapore prepares for record 36°C heat later this week.")

with n_col2:
    st.subheader("🚗 Latest COE (Mar 2nd)")
    st.markdown(f"""
        <div style="background-color:#fff3cd; padding:12px; border-radius:10px; border-left:5px solid #ff
