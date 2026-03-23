import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 4.1", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .status-card { padding: 12px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.85rem; margin-bottom: 10px; }
    .status-normal { background-color: #28a745; }
    .status-advisory { background-color: #ffc107; color: #212529; }
    .coe-card { background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 8px; margin-bottom: 10px; min-height: 150px; }
    .coe-price { font-size: 1.2rem; font-weight: bold; color: #d32f2f; }
    @media (prefers-color-scheme: dark) {
        .time-card, .coe-card { background-color: #262730; border-color: #444; }
        .time-value { color: #ffffff; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Helper Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

def fetch_news(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=5, headers=headers)
        return feedparser.parse(response.content)
    except: return None

# --- UI START ---
st.title("Singapore Info Monitor 4.1")

# Clocks - FIXED Syntax at line 63
t_cols = st.columns(6)
zones = [
    ("Singapore", "Asia/Singapore"), 
    ("Bangkok", "Asia/Bangkok"), 
    ("Tokyo", "Asia/Tokyo"), 
    ("Jakarta", "Asia/Jakarta"), 
    ("Manila", "Asia/Manila"), 
    ("Brisbane", "Australia/Brisbane")
]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# News Section
st.header("🇸🇬 Singapore Headline News")
sources = {"Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"}
t_news1, t_news2 = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])
with t_news1:
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries: st.markdown(f"**{name}**: [{feed.entries[0].title}]({feed.entries[0].link})")
with t_news2:
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    feed = fetch_news(sources[sel])
    if feed and feed.entries:
        for e in feed.entries[:6]: st.write(f"• [{e.title}]({e.link})")

st.divider()

# 1. DROPDOWN: TRAIN STATUS (March 23 Status)
with st.expander("🚇 MRT/LRT Service Status", expanded=True):
    train_lines = {"NSL": "Normal", "EWL": "Normal", "NEL": "Normal", "CCL": "Advisory", "DTL": "Normal", "TEL": "Normal"}
    s_cols = st.columns(6)
    for i, (line, status) in enumerate(train_lines.items()):
        bg = "status-normal" if status == "Normal" else "status-advisory"
        icon = "✅" if status == "Normal" else "⚠️"
        s_cols[i].markdown(f'<div class="status-card {bg}">{line}<br>{icon} {status}</div>', unsafe_allow_html=True)
    if "Advisory" in train_lines.values():
        st.warning("⚠️ **Circle Line (CCL):** Expect 5-10 min additional travel time due to track maintenance near Paya Lebar.")

# 2. DROPDOWN: MARKET INFO (Mar 23 Closing Data)
with st.expander("📊 Market Info - Mar 23 Close", expanded=False):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,400.12", "-114.20")
    m3.metric("Silver", "$67.42", "-2.24")
    m4.metric("Brent Crude", "$113.15", "+0.86")

# 3. DROPDOWN: FOREX (Mar 23 Rates)
with st.expander("💱 Forex Rates (Base: 1 SGD)", expanded=False):
    f_cols = st.columns(5)
    f_cols[0].metric("MYR", "3.0717", "+0.17%")
    f_cols[1].metric("CNY", "5.3142", "-0.05%")
    f_cols[2].metric("THB", "26.410", "+0.12%")
    f_cols[3].metric("JPY", "112.45", "-0.22%")
    f_cols[4].metric("AUD", "1.1241", "+0.08%")

# 4. DROPDOWN: COE COMPARISON (Latest Results)
with st.expander("🚗 COE Bidding - Mar 2026 (2nd Ex)", expanded=False):
    # Data: (Cat, Price, Diff vs Last, Quota, Bids)
    coe_data = [
        ("Cat A", 111890, 3670, 1264, 1895),
        ("Cat B", 115568, 1566, 812, 1185),
        ("Cat C", 78000, 2000, 290, 438),
        ("Cat D", 9589, 987, 546, 726),
        ("Cat E", 118119, 3229, 246, 422)
    ]
    c_cols = st.columns(5)
    for i, (cat, price, diff, q, b) in enumerate(coe_data):
        with c_cols[i]:
            ratio = b / q if q > 0 else 0
            st.markdown(f"""
                <div class="coe-card">
                    <div style="font-weight:bold; font-size:0.8rem;">{cat}</div>
                    <div class="coe-price">${price:,}</div>
                    <div style="color:#d32f2f; font-weight:bold; font-size:0.85rem;">▲ ${diff:,}</div>
                    <hr style="margin:8px 0;">
                    <div style="font-size:0.7rem; color:#666;">
                        Quota: <b>{q}</b><br>
                        Bids: <b>{b}</b><br>
                        Ratio: <b>{ratio:.2f}x</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v4.1 Stable")
