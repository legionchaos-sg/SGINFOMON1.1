import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Page Config
st.set_page_config(
    page_title="SG INFO MON 1.1",
    page_icon="🇸🇬",
    layout="wide"
)

# 2. Custom CSS (Fixed Syntax)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.title("🇸🇬 Singapore Info Monitor 1.1")
st.caption(f"Real-time Data | Last System Check: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}")

# 4. Data Functions
def get_weather():
    try:
        url = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
        res = requests.get(url, timeout=5)
        return res.json()['items'][0]['forecasts']
    except:
        return None

def get_psi():
    try:
        url = "https://api.data.gov.sg/v1/environment/psi"
        res = requests.get(url, timeout=5)
        val = res.json()['items'][0]['readings']['psi_twenty_four_hourly']['national']
        return int(val)
    except:
        return None

# 5. Layout (Defining the columns clearly)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📡 Environment")
    psi_val = get_psi()
    if psi_val is not None:
        status = "Healthy" if psi_val < 50 else "Moderate"
        st.metric(label="24h PSI (National)", value=psi_val, delta=status)
    else:
        st.metric(label="24h PSI (National)", value="Offline", delta="API Error")
    
    st.write("---")
    st.info("💡 **Portable Build:** This app is running via GitHub + Streamlit Cloud.")

with col_right:
    st.subheader("🌦️ 2-Hour Weather Forecast")
    weather_data = get_weather()
    if weather_data:
        df = pd.DataFrame(weather_data)
        # Show key areas in a grid
        key_areas = ["Orchard", "Changi", "Tuas", "Woodlands"]
        display_df = df[df['area'].isin(key_areas)]
        
        m_cols = st.columns(len(key_areas))
        for i, area in enumerate(key_areas):
            forecast = display_df[display_df['area'] == area]['forecast'].values[0]
            m_cols[i].metric(area, forecast)
            
        with st.expander("View All Singapore Areas"):
            st.dataframe(df, use_container_width=True)
    else:
        st.error("Weather data currently unavailable.")

# 6. Footer
st.markdown("---")
st.markdown("Data Source: [data.gov.sg](https://data.gov.sg)")
