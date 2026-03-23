import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.1", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_101_stable")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 10px; min-height: 190px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; color: var(--text-color); }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .trans-box { font-size: 0.85rem; color: #666; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.85rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.85rem; }
    .stat-label { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
    div[data-testid="stExpander"] [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Fuel Data (Intact)
brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32), "Cnergy": ("N/A", 0), "Sinopec": ("N/A", 0), "Smart Energy": ("N/A", 0)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20), "Cnergy": ("N/A", 0), "Smart Energy": ("N/A", 0)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List & Adjustments")
    for brand in brand_order:
        data = fuel_data[ftype].get(brand, ("N/A", 0))
        price, change = data
        if brand == "Shell" and ftype == "92 Octane": continue
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        change_class = "up" if change > 0 else "down"
        change_str = f"({'+' if change > 0 else ''}{change:.2f})" if change != 0 else ""
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff; margin-right:8px;'>{display_price}</b><span class='{change_class}'>{change_str}</span></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.1")

# 4. Country Clocks
countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
t_cols = st.columns(6)
for i, (name, tz) in enumerate(countries):
    t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. News Section (INTEGRATED 8WORLD FIX)
st.header("🗞️ Singapore Headlines")
news_sources = {
    "CNA": "
