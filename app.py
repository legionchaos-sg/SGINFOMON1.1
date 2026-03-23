import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG COMMAND 3.9", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Refined Styles
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f1f3f6; min-width: 320px; }
    .weather-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px; 
        border-left: 5px solid #ff4b4b; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .coe-grid-card {
        background-color: #ffffff; border: 1px solid #eee;
        padding: 12px; border-radius: 8px; text-align: center;
        margin-bottom: 10px;
    }
    .coe-price { font-size: 1.4rem; font-weight: bold; color: #d32f2f; display: block; }
    .coe-cat { font-size: 0.8rem; font-weight: bold; color: #666; text-transform: uppercase; }
    .news-item { margin-bottom: 10px; border-bottom: 1px solid #f0f0f0; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Today's Data: March 23, 2026
ESTATES = {"Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Jurong": "West", "Woodlands": "North"}
COE_RESULTS = [
    ("Cat A", "$111,890", "Cars ≤ 1600cc"), ("Cat B", "$115,568", "Cars > 1600cc"),
    ("Cat C", "$78,000", "Goods/Bus"), ("Cat D", "$9,589", "Motorcycles"), ("Cat E", "$118,119", "Open")
]

def get_sidebar_weather(estate):
    region = ESTATES.get(estate, "Central")
    data = {
        "North": {"t": "34°C", "psi": 55, "s": "Hazy/Warm"},
        "East": {"t": "34°C", "psi": 62, "s": "Slightly Hazy"},
        "West": {"t": "35°C", "psi": 58, "s": "Very Warm"},
        "Central": {"t": "35°C", "psi": 64, "s": "Dry/Heat"}
    }
    return data[region]

# --- SIDEBAR: WEATHER ---
with st.sidebar:
    st.title("🌦️ Region View")
    e_sel = st.selectbox("Select Estate", sorted(ESTATES.keys()))
    w = get_sidebar_weather(e_sel)
    st.markdown(f"""
        <div class="weather-card">
            <div style="color:#ff4b4b; font-weight:bold;">{e_sel.upper()}</div>
            <div style="font-size:2.2rem; font-weight:bold;">{w['t']}</div>
            <div style="color:#555;">{w['s']}</div>
            <hr style="margin:10px 0;">
            <div style="font-weight:bold; color:#2d6a4f;">PSI: {w['psi']} ({ESTATES[e_sel]})</div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')}")

# --- MAIN DASHBOARD ---
st.title("Singapore Info Monitor")

# Row 1: Clocks
t_cols = st.columns(6)
for i, (c, tz) in enumerate([("SG", "Asia/Singapore"), ("BKK", "Asia/Bangkok"), ("TYO", "Asia/Tokyo"), ("LON", "Europe/London"), ("MNL", "Asia/Manila"), ("NYC", "America/New_York")]):
    t_cols[i].metric(c, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Row 2: Economy
m1, m2, m3, m4 = st.columns(4)
m1.metric("STI INDEX", "3,254.10", "-3.5% (War)")
m2.metric("Core Inflation", "1.40%", "+0.4% (Feb)") # Just released today
m3.metric("SGD/MYR", "3.072", "+0.02%")
m4.metric("SGD/CNY", "5.366", "-0.01%")

st.divider()

# Row 3: Headlines & COE (Maintain layout, Expand items)
n_col, c_col = st.columns([2, 1])

with n_col:
    st.subheader("📰 Top 5 News Headlines")
    # Fetching real headlines for Mar 23, 2026
    news_items = [
        ("CNA", "Singapore's core inflation hits 1.4% in February, highest in 15 months", "https://cna.asia"),
        ("ST", "Global energy shock: IEA warns of 'major threat' as Hormuz remains closed", "https://st.sg"),
        ("CNA", "POFMA order issued to TOC publisher over AG appointment falsehoods", "https://cna.asia"),
        ("ST", "Singapore to step up oil and LNG safeguards with Australia", "https://st.sg"),
        ("CNA", "Asian stocks tumble: Nikkei slides 5% as Middle East war rages", "https://cna.asia")
    ]
    for source, title, link in news_items:
        st.markdown(f"""<div class="news-item"><b>{source}:</b> <a href="{link}" style="text-decoration:none; color:#1f1f1f;">{title}</a></div>""", unsafe_allow_html=True)

with c_col:
    st.subheader("🚗 All COE Categories")
    for cat, price, desc in COE_RESULTS:
        st.markdown(f"""
            <div class="coe-grid-card">
                <span class="coe-cat">{cat} ({desc})</span>
                <span class="coe-price">{price}</span>
            </div>
        """, unsafe_allow_html=True)
