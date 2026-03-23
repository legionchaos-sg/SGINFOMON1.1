import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="SG INFO MON 1.1",
    page_icon="🇸🇬",
    layout="wide"
)

# Custom CSS for a clean look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🇸🇬 Singapore Info Monitor 1.1")
st.caption(f"Real-time Data Dashboard | Last System Check: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}")

# --- Data Fetching Functions ---
def get_weather():
    try:
        url = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
        response = requests.get(url)
        return response.json()['items'][0]['forecasts']
    except:
        return None

def get_psi():
    try:
        url = "https://api.data.gov.sg/v1/environment/psi"
        response = requests.get(url)
        return response.json()['items'][0]['readings']['psi_twenty_four_hourly']['national']
    except:
        return "N/A"

# --- Layout ---
col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("📡 Environment Status")
    psi_val = get_psi()
    st.metric(label="24h PSI (National)", value=psi_val, delta="Healthy" if int(psi_val) < 50 else "Moderate")
    
    st.write("---")
    st.info("💡 **Tip:** This dashboard is portable. To run locally, use `streamlit run app.py` after installing requirements.")

with col_b:
    st.subheader("🌦️ 2-Hour Weather Forecast")
    weather_data = get_weather()
    if weather_data:
        df = pd.DataFrame(weather_data)
        # Displaying a selection of key areas
        key_areas = ["Orchard", "Changi", "Tuas", "Woodlands", "Ang Mo Kio"]
        display_df = df[df['area'].isin(key_areas)]
        
        cols = st.columns(len(key_areas))
        for i, area in enumerate(key_areas):
            forecast = display_df[display_df['area'] == area]['forecast'].values[0]
            cols[i].metric(area, forecast)
            
        with st.expander("Show All Areas"):
            st.dataframe(df, use_container_width=True)
    else:
        st.error("Weather API currently unavailable.")

# Footer
st.markdown("---")
st.markdown("Data Source: [data.gov.sg](https://data.gov.sg)")
