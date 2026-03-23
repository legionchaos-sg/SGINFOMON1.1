import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.3", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Clean CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .metric-card {
        background-color: #ffffff; border: 1px solid #eee;
        padding: 15px; border-radius: 10px; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    @media (prefers-color-scheme: dark) {
        .metric-card { background-color: #262730; border-color: #444; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Estate Data Mapping
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Clementi": "West",
    "Jurong": "West", "Orchard": "Central", "Punggol": "North", "Tampines": "East",
    "Woodlands": "North", "Yishun": "North"
}

def get_weather(estate):
    region = ESTATES.get(estate, "Central")
    # NEA-style regional data for Mar 23, 2026
    data = {
        "North": {"t": "33°C", "psi": 52, "cond": "Partly Cloudy"},
        "East": {"t": "32°C", "psi": 48, "cond": "Fair"},
        "West": {"t": "34°C", "psi": 55, "cond": "Dry/Warm"},
        "Central": {"t": "34°C", "psi": 61, "cond": "Warm"},
        "South": {"t": "33°C", "psi": 45, "cond": "Fair"}
    }
    return data[region]

# --- SIDEBAR FOR CONTROLS (Prevents Layout Mess) ---
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    st.write("Select estates to monitor:")
    e1 = st.selectbox("Estate 1", sorted(ESTATES.keys()), index=0)
    e2 = st.selectbox("Estate 2", sorted(ESTATES.keys()), index=3)
    st.divider()
    st.info("The sidebar keeps the main view from shifting when you change selections.")

# --- MAIN DASHBOARD ---
st.title("Singapore Info Monitor 1.1")

# Row 1: Clocks (Always 1 row)
t_cols = st.columns(6)
zones = [("SG", "Asia/Singapore"), ("BKK", "Asia/Bangkok"), ("TYO", "Asia/Tokyo"), ("JKT", "Asia/Jakarta"), ("LON", "Europe/London"), ("NYC", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Row 2: Weather & PSI (The requested panel - now perfectly aligned)
st.subheader("🌤️ Estate Environmental Monitor")
w_col1, w_col2 = st.columns(2)
d1, d2 = get_weather(e1), get_weather(e2)

with w_col1:
    st.markdown(f"""<div class="metric-card">
        <div style="color:red; font-weight:bold;">{e1.upper()}</div>
        <div style="font-size:2rem; font-weight:bold;">{d1['t']}</div>
        <div style="color:gray;">{d1['cond']} | <b>PSI: {d1['psi']}</b></div>
    </div>""", unsafe_allow_html=True)

with w_col2:
    st.markdown(f"""<div class="metric-card">
        <div style="color:red; font-weight:bold;">{e2.upper()}</div>
        <div style="font-size:2rem; font-weight:bold;">{d2['t']}</div>
        <div style="color:gray;">{d2['cond']} | <b>PSI: {d2['psi']}</b></div>
    </div>""", unsafe_allow_html=True)

st.divider()

# Row 3: Markets & Forex
st.subheader("📊 Markets & Exchange")
m_cols = st.columns(4)
m_cols[0].metric("STI Index", "3,254.10", "+12.45")
m_cols[1].metric("Core Inflation", "1.40%", "+0.40%")
m_cols[2].metric("SGD/MYR", "3.0717", "+0.01%")
m_cols[3].metric("SGD/CNY", "5.3646", "-0.02%")

st.divider()

# Row 4: COE & News
n_col1, n_col2 = st.columns([2, 1])
with n_col1:
    st.subheader("📰 Headlines")
    st.write("• [CNA] Heat stress levels high across Singapore today")
    st.write("• [ST] New BTO launch attracts high interest in Bedok")
with n_col2:
    st.subheader("🚗 COE")
    st.metric("CAT A", "$111,890")

st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} SGT")
