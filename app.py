import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator
import yfinance as yf

# --- CORE CONFIG ---
st.set_page_config(page_title="SGINFOMON", page_icon="🇸🇬60", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# --- ADAPTIVE CSS (Concise 14px) ---
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 14px !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main .block-container { max-width: 95%; padding-top: 1rem; }
    .t-card { background: #1a1a1a; border: 1px solid #333; padding: 5px; border-radius: 4px; text-align: center; }
    .c-card { background: #111; border-left: 5px solid #ff4b4b; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
    .up { color: #ff4b4b; font-weight: bold; font-size: 0.8rem; }
    .down { color: #09ab3b; font-weight: bold; font-size: 0.8rem; }
    .data-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "g10_target_fix" not in st.session_state: st.session_state.g10_target_fix = 0.0000

# --- DATA ENGINES ---
@st.cache_data(ttl=3600)
def get_live_fuel_sync():
    # Mar 27 Data: Petrol -0.05, Diesel Peak
    return {
        "92 Octane": {"Esso": [3.38, -0.05], "Caltex": [3.38, -0.05], "SPC": [3.38, -0.05], "Cnergy": ["N/A", 0], "Sinopec": ["N/A", 0]},
        "95 Octane": {"Esso": [3.42, -0.05], "Caltex": [3.42, -0.05], "Shell": [3.42, -0.05], "SPC": [3.41, -0.05], "Sinopec": [3.42, -0.05]},
        "98 Octane": {"Esso": [3.92, -0.05], "Shell": [3.94, -0.05], "SPC": [3.92, -0.05], "Sinopec": [3.92, -0.05]},
        "Premium":   {"Caltex": [4.11, -0.05], "Shell": [4.16, -0.05], "Sinopec": [4.05, -0.05]},
        "Diesel":    {"Esso": [3.93, 0.0], "Caltex": [3.73, 0.0], "Shell": [3.93, 0.0], "SPC": [3.66, 0.0], "Sinopec": [3.72, 0.0]}
    }

fuel_data = get_live_fuel_sync()

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Details")
    for brand, vals in fuel_data[ftype].items():
        price, change = vals
        if price == "N/A": continue
        ind = f"<span class='up'>▲ ${change:+.2f}</span>" if change > 0 else f"<span class='down'>▼ ${abs(change):.2f}</span>" if change < 0 else "—"
        st.markdown(f"<div class='data-row'><b>{brand}</b><span><b style='color:#007bff;'>${price:.2f}</b> {ind}</span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9.21")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 MONITOR", "🏢 SERVICES", "🛠️ TOOLS", "🔮 COE", "✈️ AIRFARE"])

with tab1:
    # 1. Clocks
    c = st.columns(4)
    for i, (n, tz) in enumerate([("SGP", "Asia/Singapore"), ("BKK", "Asia/Bangkok"), ("TYO", "Asia/Tokyo"), ("SYD", "Australia/Sydney")]):
        c[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)
    
    st.divider()
    # 2. Fuel Avg Display
    st.subheader("⛽ Fuel Daily Averages")
    fc = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
        avg = sum(prices)/len(prices) if prices else 0
        fc[i].metric(ftype, f"${avg:.2f}")
        if fc[i].button("Details", key=f"btn_{ftype}"): show_fuel_details(ftype)

with tab2:
    st.header("🏢 Public Services")
    st.markdown("- [Singpass](https://www.singpass.gov.sg) | [CPF](https://www.cpf.gov.sg)")
    st.markdown("- [HDB](https://www.hdb.gov.sg) | [NEA Weather](https://www.nea.gov.sg)")
    st.error("🚨 Police: 999 | SCDF: 995")

with tab3:
    st.header("🛠️ System Tools")
    st.write(f"Active ID: **gold 10**")
    st.number_input("Target Fix Adjustment", value=st.session_state.g10_target_fix, step=0.0001)

with tab4:
    st.header("🔮 COE Strategic Prediction")
    st.table(pd.DataFrame({"Cat": ["A", "B", "E"], "Price": ["$111,890", "$115,568", "$118,119"], "Trend": ["UP", "STABLE", "UP"]}))

with tab5:
    st.header("✈️ Airfare Engine")
    st.info("Route Analytics: SIN -> Global Hubs (June 2026 Forecast)")
    st.json({"SIN-LHR": "1,240 SGD", "SIN-NRT": "680 SGD", "SIN-BKK": "210 SGD"})

st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} | gold 10 Concise Mode")
