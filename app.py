import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.2", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Enhanced Styling for Compactness
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 8px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.7rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; }
    .time-value { font-size: 1.1rem; font-weight: bold; }
    
    /* Compact Weather Row */
    .env-panel { 
        background-color: #f0f7ff; border: 1px solid #d1e3ff; 
        padding: 10px; border-radius: 10px; display: flex; 
        justify-content: space-around; align-items: center;
    }
    .env-stat { text-align: center; border-right: 1px solid #d1e3ff; padding: 0 15px; }
    .env-label { font-size: 0.7rem; color: #555; font-weight: bold; text-transform: uppercase; }
    .env-val { font-size: 1.2rem; font-weight: bold; color: #004a99; }
    
    @media (prefers-color-scheme: dark) {
        .time-card { background-color: #262730; border-color: #333; }
        .env-panel { background-color: #1a202c; border-color: #2d3748; }
        .env-val { color: #63b3ed; }
        .env-label { color: #a0aec0; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Logic
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Boon Lay": "West",
    "Bukit Merah": "South", "Changi": "East", "Clementi": "West", "Hougang": "North", 
    "Jurong": "West", "Orchard": "Central", "Pasir Ris": "East", "Punggol": "North", 
    "Queenstown": "South", "Sengkang": "North", "Tampines": "East", "Woodlands": "North", "Yishun": "North"
}

def get_env_data(estate):
    region = ESTATES.get(estate, "Central")
    # Today's Forecast (Mar 23, 2026): Warm/Dry, haze risk.
    # Current PSI range: 45-66 (Good to Moderate)
    readings = {
        "North": {"t": "33°C", "psi": 53, "st": "Warm/Dry"},
        "South": {"t": "34°C", "psi": 48, "st": "Fair"},
        "East": {"t": "33°C", "psi": 52, "st": "Hazy"},
        "West": {"t": "34°C", "psi": 53, "st": "Dry"},
        "Central": {"t": "34°C", "psi": 66, "st": "Warm"}
    }
    return readings[region]

# 5. Clocks
st.subheader("🌐 Global Clocks")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), ("Jakarta", "Asia/Jakarta"), ("London", "Europe/London"), ("New York", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# 6. Market & Forex (Side-by-Side to save space)
c1, c2 = st.columns([1, 1.5])
with c1:
    st.subheader("📊 Markets")
    st.metric("STI INDEX", "3,254.10", "+12.45")
    st.metric("SG Core Inflation", "1.40%", "+0.40%")
with c2:
    st.subheader("💱 Forex (1 SGD)")
    f_cols = st.columns(3)
    f_cols[0].metric("MYR", "3.0717", "+0.02%")
    f_cols[1].metric("CNY", "5.3646", "-0.01%")
    f_cols[2].metric("JPY", "124.30", "+0.15%")

st.divider()

# 7. WEATHER & PSI (The Requested Panel - COMPACT VERSION)
st.subheader("🌤️ Estate Environmental Monitor")
sel_col1, sel_col2 = st.columns(2)
e1 = sel_col1.selectbox("Select Estate 1", sorted(ESTATES.keys()), index=0)
e2 = sel_col2.selectbox("Select Estate 2", sorted(ESTATES.keys()), index=14) # Tampines

d1, d2 = get_env_data(e1), get_env_data(e2)

# Row 1: Comparison Display
st.markdown(f"""
    <div class="env-panel">
        <div class="env-stat">
            <div class="env-label">{e1}</div>
            <div class="env-val">{d1['t']} | PSI {d1['psi']}</div>
            <div style="font-size:0.7rem; color:gray;">{d1['st']}</div>
        </div>
        <div class="env-stat" style="border:none;">
            <div class="env-label">{e2}</div>
            <div class="env-val">{d2['t']} | PSI {d2['psi']}</div>
            <div style="font-size:0.7rem; color:gray;">{d2['st']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# 8. News & COE
n1, n2 = st.columns([2, 1])
with n1:
    st.subheader("🇸🇬 News")
    st.markdown("• [CNA] NEA warns of heat stress risk this week")
    st.markdown("• [ST] Singapore core inflation rises to 1.4%")
with n2:
    st.subheader("🚗 COE")
    st.metric("CAT A", "$111,890")

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT")
