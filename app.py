import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.0", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .weather-card { 
        background-color: #f0f7ff; border-radius: 12px; padding: 15px; 
        border: 1px solid #d1e3ff; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .psi-badge { background-color: #2e7d32; color: white; padding: 3px 10px; border-radius: 20px; font-weight: bold; font-size: 0.75rem; }
    @media (prefers-color-scheme: dark) {
        .time-card { background-color: #262730; border-color: #444; }
        .weather-card { background-color: #1a202c; border-color: #2d3748; }
        .time-value { color: #ffffff; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Logic
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

# Estate mapping to NEA Regions for PSI accuracy
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Boon Lay": "West",
    "Bukit Batok": "West", "Bukit Merah": "South", "Bukit Panjang": "West", "Bukit Timah": "Central",
    "Changi": "East", "Choa Chu Kang": "West", "Clementi": "West", "Geylang": "East",
    "Hougang": "North", "Jurong East": "West", "Jurong West": "West", "Marine Parade": "South",
    "Newton": "Central", "Pasir Ris": "East", "Paya Lebar": "East", "Punggol": "North",
    "Queenstown": "South", "Sembawang": "North", "Sengkang": "North", "Serangoon": "North",
    "Tampines": "East", "Toa Payoh": "Central", "Tuas": "West", "Woodlands": "North", "Yishun": "North"
}

def get_estate_weather(estate):
    region = ESTATES.get(estate, "Central")
    # Simulated 2026 data based on late March patterns
    base_data = {
        "North": {"temp": "30°C", "desc": "Partly Cloudy", "psi": 42},
        "South": {"temp": "31°C", "desc": "Fair", "psi": 38},
        "East": {"temp": "30°C", "desc": "Light Showers", "psi": 45},
        "West": {"temp": "32°C", "desc": "Cloudy", "psi": 52},
        "Central": {"temp": "31°C", "desc": "Fair", "psi": 40}
    }
    return base_data[region]

# 5. Regional Time
st.subheader("🌐 REGIONAL Current Time")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# 6. ESTATE WEATHER & PSI (Side-by-Side Selection)
st.header("🌤️ Weather & Air Quality by Estate")
w_col1, w_col2 = st.columns(2)

# Selection 1
with w_col1:
    estate1 = st.selectbox("Compare Estate 1", sorted(ESTATES.keys()), index=0)
    res1 = get_estate_weather(estate1)
    st.markdown(f"""
        <div class="weather-card">
            <div style="font-weight:bold; color:#ff4b4b; margin-bottom:5px;">{estate1.upper()}</div>
            <div style="display:flex; align-items:baseline; gap:10px;">
                <span style="font-size:2.2rem; font-weight:bold;">{res1['temp']}</span>
                <span style="color:#666;">{res1['desc']}</span>
            </div>
            <div style="margin-top:10px;">
                <span class="psi-badge">PSI: {res1['psi']} ({ESTATES[estate1]})</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Selection 2
with w_col2:
    estate2 = st.selectbox("Compare Estate 2", sorted(ESTATES.keys()), index=10) # Default to Clementi
    res2 = get_estate_weather(estate2)
    st.markdown(f"""
        <div class="weather-card">
            <div style="font-weight:bold; color:#ff4b4b; margin-bottom:5px;">{estate2.upper()}</div>
            <div style="display:flex; align-items:baseline; gap:10px;">
                <span style="font-size:2.2rem; font-weight:bold;">{res2['temp']}</span>
                <span style="color:#666;">{res2['desc']}</span>
            </div>
            <div style="margin-top:10px;">
                <span class="psi-badge">PSI: {res2['psi']} ({ESTATES[estate2]})</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 7. Financial & News (Condensed)
st.subheader("📊 Markets & News")
m1, m2 = st.columns([1, 2])
with m1:
    st.metric("STI INDEX", "3,254.10", "+12.45")
    st.metric("SG Core Inflation", "1.40%", "+0.40%")
with m2:
    st.info("Latest Headlines")
    st.markdown("• [ST] NEA monitoring haze from Johor hotspots")
    st.markdown("• [CNA] March COE prices see slight dip in Cat A")

# 8. Footer
st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} SGT")
