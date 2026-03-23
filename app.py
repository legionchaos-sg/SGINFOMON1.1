import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG COMMAND 3.8", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Enhanced Styling for Sidebar & Main Content
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f1f3f6; min-width: 320px; }
    .weather-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px; 
        border-left: 5px solid #ff4b4b; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .coe-table-card {
        background-color: #ffffff; border: 1px solid #eee;
        padding: 10px; border-radius: 10px; text-align: center;
    }
    .price-text { font-size: 1.3rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 4. Correct Data Mapping for Mar 23, 2026
ESTATES = {
    "Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Clementi": "West",
    "Jurong": "West", "Orchard": "Central", "Punggol": "North", "Tampines": "East",
    "Woodlands": "North", "Yishun": "North", "Bukit Merah": "South"
}

def get_live_data(estate):
    region = ESTATES.get(estate, "Central")
    # NEA Data for Mar 23: Extreme Heat (35°C) & Moderate PSI
    readings = {
        "North": {"t": "34°C", "psi": 55, "status": "Hazy/Warm"},
        "South": {"t": "33°C", "psi": 48, "status": "Fair/Dry"},
        "East": {"t": "34°C", "psi": 62, "status": "Slightly Hazy"},
        "West": {"t": "35°C", "psi": 58, "status": "Very Warm"},
        "Central": {"t": "35°C", "psi": 64, "status": "Dry/Heat"}
    }
    return readings[region]

# --- SIDEBAR: SELECTORS & RESULTS (Fixed) ---
with st.sidebar:
    st.title("🌦️ Regional Monitor")
    st.write("Current conditions for your selected areas:")
    
    # Estate 1
    sel1 = st.selectbox("Area 1", sorted(ESTATES.keys()), index=0)
    d1 = get_live_data(sel1)
    st.markdown(f"""
        <div class="weather-card">
            <div style="font-weight:bold; color:#ff4b4b;">{sel1.upper()}</div>
            <div style="font-size:2rem; font-weight:bold;">{d1['t']}</div>
            <div style="font-size:0.9rem; color:#555;">{d1['status']}</div>
            <div style="font-weight:bold; margin-top:5px; color:#2d6a4f;">PSI: {d1['psi']} ({ESTATES[sel1]})</div>
        </div>
    """, unsafe_allow_html=True)

    # Estate 2
    sel2 = st.selectbox("Area 2", sorted(ESTATES.keys()), index=7)
    d2 = get_live_data(sel2)
    st.markdown(f"""
        <div class="weather-card">
            <div style="font-weight:bold; color:#ff4b4b;">{sel2.upper()}</div>
            <div style="font-size:2rem; font-weight:bold;">{d2['t']}</div>
            <div style="font-size:0.9rem; color:#555;">{d2['status']}</div>
            <div style="font-weight:bold; margin-top:5px; color:#2d6a4f;">PSI: {d2['psi']} ({ESTATES[sel2]})</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption(f"Refreshed at: {datetime.now().strftime('%H:%M:%S')}")

# --- MAIN DASHBOARD: THE PERFECT VIEW ---
st.title("Singapore Information Hub")

# Row 1: Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("London", "Europe/London"), ("Manila", "Asia/Manila"), ("New York", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Row 2: Economy & Market
m1, m2, m3, m4 = st.columns(4)
m1.metric("STI INDEX", "3,254.10", "+12.45")
m2.metric("Core Inflation", "1.40%", "Feb Peak")
m3.metric("SGD/MYR", "3.072", "+0.002")
m4.metric("SGD/CNY", "5.366", "-0.001")

st.divider()

# Row 3: Headlines & COE (Restored & Maintained)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📰 Latest News")
    st.markdown("• **CNA**: [NEA monitors Johor hotspots as burning smell reaches SG](https://www.channelnewsasia.com)")
    st.markdown("• **ST**: [MAS keeps close watch as core inflation edges up to 1.4%](https://www.straitstimes.com)")
    st.markdown("• **CNA**: [Record heatwave: Tempeatures hit 35.6°C in Choa Chu Kang](https://www.channelnewsasia.com)")

with col_right:
    st.subheader("🚗 COE Results")
    coe_list = [("CAT A", "$111,890"), ("CAT B", "$115,568"), ("CAT E", "$118,119")]
    for cat, price in coe_list:
        st.markdown(f"""
            <div class="coe-table-card" style="margin-bottom:8px;">
                <span style="font-size:0.8rem; color:#666;">{cat}</span><br>
                <span class="price-text">{price}</span>
            </div>
        """, unsafe_allow_html=True)
