import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Page Config (Keeps the emoji in the browser tab ONLY)
st.set_page_config(
    page_title="SG INFO MON 1.1",
    page_icon="🇸🇬",
    layout="wide"
)

# 2. Custom CSS (Cleaner & Professional)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stMetric { background-color: #ffffff; border: 1px solid #eeeeee; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header (Cleaned Title - No Emoji)
st.title("Singapore Info Monitor 1.1")
st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} SGT")

# 4. Data Functions (Improved PSI Logic)
def get_psi():
    try:
        url = "https://api.data.gov.sg/v1/environment/psi"
        res = requests.get(url, timeout=5)
        data = res.json()
        # In 2026, we drill down carefully into the JSON layers
        val = data['items'][0]['readings']['psi_twenty_four_hourly']['national']
        return int(val)
    except Exception as e:
        return None

def get_weather():
    try:
        url = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
        res = requests.get(url, timeout=5)
        return res.json()['items'][0]['forecasts']
    except:
        return None

# 5. Layout
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Environment")
    psi = get_psi()
    if psi:
        color = "normal" if psi < 50 else "off"
        st.metric(label="National PSI (24h)", value=psi, delta="Healthy" if psi < 50 else "Moderate")
    else:
        st.info("PSI Data currently updating...")

with col_right:
    st.subheader("Weather Forecast")
    weather = get_weather()
    if weather:
        df = pd.DataFrame(weather)
        # Showing key hubs
        hubs = ["Orchard", "Changi", "Tuas", "Woodlands"]
        m_cols = st.columns(len(hubs))
        for i, area in enumerate(hubs):
            row = df[df['area'] == area]
            if not row.empty:
                m_cols[i].metric(area, row['forecast'].values[0])
    else:
        st.warning("Awaiting Weather API response...")
