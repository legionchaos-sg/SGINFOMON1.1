import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG COMMAND 3.6", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Sidebar Specific Styling
st.markdown("""
    <style>
    /* Fixed Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #f1f3f6; min-width: 300px; }
    .sb-weather-box {
        background-color: #ffffff; border: 1px solid #dee2e6;
        padding: 15px; border-radius: 12px; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .sb-estate { color: #ff4b4b; font-weight: bold; font-size: 0.85rem; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 8px; }
    .sb-temp { font-size: 1.8rem; font-weight: bold; color: #1a202c; }
    .sb-psi { color: #2d6a4f; font-weight: bold; font-size: 0.9rem; margin-top: 5px; }
    
    /* Main Layout Protection */
    .main-metric { text-align: center; padding: 10px; border: 1px solid #eee; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Estate Data (Mapped to NEA Regions)
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Clementi": "West",
    "Jurong": "West", "Orchard": "Central", "Punggol": "North", "Tampines": "East",
    "Woodlands": "North", "Yishun": "North", "Bukit Merah": "South"
}

def get_sidebar_weather(estate):
    region = ESTATES.get(estate, "Central")
    # Today's Snapshot: March 23, 2026 - Hot & Hazy
    data = {
        "North": {"t": "34°C", "psi": 52, "desc": "Hazy/Warm"},
        "South": {"t": "33°C", "psi": 47, "desc": "Fair/Dry"},
        "East": {"t": "34°C", "psi": 61, "desc": "Slightly Hazy"},
        "West": {"t": "35°C", "psi": 55, "desc": "Very Warm"},
        "Central": {"t": "35°C", "psi": 64, "desc": "Dry/Heat"}
    }
    return data[region]

# --- SIDEBAR PANEL ---
with st.sidebar:
    st.title("🌦️ Estate Weather")
    st.info("Select 2 estates to monitor in the sidebar without affecting your main dashboard.")
    
    # Selection 1
    e1 = st.selectbox("Estate Watch 1", sorted(ESTATES.keys()), index=0)
    w1 = get_sidebar_weather(e1)
    st.markdown(f"""
        <div class="sb-weather-box">
            <div class="sb-estate">{e1.upper()}</div>
            <div class="sb-temp">{w1['t']}</div>
            <div style="font-size:0.8rem; color:#666;">{w1['desc']}</div>
            <div class="sb-psi">PSI {w1['psi']} ({ESTATES[e1]})</div>
        </div>
    """, unsafe_allow_html=True)

    # Selection 2
    e2 = st.selectbox("Estate Watch 2", sorted(ESTATES.keys()), index=7)
    w2 = get_sidebar_weather(e2)
    st.markdown(f"""
        <div class="sb-weather-box">
            <div class="sb-estate">{e2.upper()}</div>
            <div class="sb-temp">{w2['t']}</div>
            <div style="font-size:0.8rem; color:#666;">{w2['desc']}</div>
            <div class="sb-psi">PSI {w2['psi']} ({ESTATES[e2]})</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')}")

# --- MAIN DASHBOARD (The "Perfect" Layout) ---
st.title("Singapore Command Center")

# Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("London", "Europe/London"), ("Manila", "Asia/Manila"), ("New York", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Finance Row
st.subheader("📊 Market Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("STI INDEX", "3,254.10", "+12.45")
m2.metric("Core Inflation", "1.40%", "+0.40%") # Mar 23 actuals
m3.metric("SGD/MYR", "3.072", "+0.01%")
m4.metric("SGD/CNY", "5.366", "-0.01%")

st.divider()

# News & COE
n_col, c_col = st.columns([2, 1])
with n_col:
    st.subheader("📰 Headlines")
    st.write("• **CNA**: Core inflation edges up as energy costs fluctuate.")
    st.write("• **ST**: Heat stress risk high as temperatures hit 35°C today.")
with c_col:
    st.subheader("🚗 COE (Current)")
    st.markdown("""
        <div style="background-color:#fffcf0; border:1px solid #ffeeba; padding:15px; border-radius:10px;">
            <div style="font-weight:bold; color:#856404;">CAT A (Standard)</div>
            <div style="font-size:1.6rem; font-weight:bold;">$111,890</div>
        </div>
    """, unsafe_allow_html=True)
