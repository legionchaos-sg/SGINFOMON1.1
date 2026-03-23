import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 5.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 2. Styles
st.markdown("""
    <style>
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .coe-card { background-color: #f8f9fa; border-left: 4px solid #ff4b4b; padding: 10px; border-radius: 6px; min-height: 120px; }
    .status-card { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.8rem; }
    .status-normal { background-color: #28a745; }
    @media (prefers-color-scheme: dark) { .time-card, .coe-card { background-color: #262730; border-color: #444; } }
    </style>
    """, unsafe_allow_html=True)

def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

# --- UI START ---
st.title("Singapore Info Monitor 5.0")

# 4. Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# 5. Market Information (Ordered: STI, Gold, Silver, Brent)
with st.expander("📊 Market Info - March 23, 2026", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,427.43", "-1.37%")
    m3.metric("Silver (Spot)", "$64.58", "-4.82%")
    m4.metric("Brent Crude", "$113.34", "+1.02%")

# 6. Forex Rates (Ordered: CNY, THB, JPY, MYR, AUD, USD)
with st.expander("💱 Forex Rates (1 SGD to X)", expanded=True):
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    f1.metric("CNY (Yuan)", "5.382", "+0.20%")
    f2.metric("THB (Baht)", "25.435", "-0.26%")
    f3.metric("JPY (Yen)", "124.22", "+0.01%")
    f4.metric("MYR (Ringgit)", "3.071", "+0.17%")
    f5.metric("AUD (Dollar)", "1.119", "+0.60%")
    f6.metric("USD (Dollar)", "0.781", "+0.19%")

# 7. COE Bidding (Full Data Restored)
with st.expander("🚗 COE Bidding - Mar 2026 (2nd Round)", expanded=False):
    coe_data = [
        ("Cat A (<1600cc)", 111890, 3670, 1264, 1895),
        ("Cat B (>1600cc)", 115568, 1566, 812, 1185),
        ("Cat C (Goods/Bus)", 78000, 2000, 290, 438),
        ("Cat D (M-Cycle)", 9589, 987, 546, 726),
        ("Cat E (Open)", 118119, 3229, 246, 422)
    ]
    c_cols = st.columns(5)
    for i, (cat, price, diff, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f"""
            <div class="coe-card">
                <div style="font-weight:bold;font-size:0.8rem;">{cat}</div>
                <div style="color:#d32f2f;font-weight:bold;font-size:1.1rem;">${price:,}</div>
                <div style="color:#d32f2f;font-size:0.8rem;font-weight:bold;">▲ ${diff:,}</div>
                <div style="font-size:0.7rem;margin-top:5px;color:#666;">Quota: {q}<br>Bids: {b}</div>
            </div>
        """, unsafe_allow_html=True)

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v5.0 Custom Order Applied")
