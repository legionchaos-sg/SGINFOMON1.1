import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 4.9", page_icon="🇸🇬", layout="wide")
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

# 3. Helpers (Cleaned for Python 3.14)
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

def fetch_news(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        feed = feedparser.parse(resp.content)
        return [{'title': e.title, 'link': e.link} for e in feed.entries[:8]]
    except: return []

# --- UI START ---
st.title("Singapore Info Monitor 4.9")

# 4. Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# 5. News Panel
st.header("🗞️ News Headlines")
trans_on = st.toggle("Translate to Chinese (翻译中)", value=False)
news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/"}
tab1, tab2 = st.tabs(["📊 Unified", "📰 Select Source"])

with tab1:
    for name, url in news_sources.items():
        e = fetch_news(url)[0]
        st.write(f"**{name}**: [{e['title']}]({e['link']})")

with tab2:
    src = st.selectbox("Outlet", list(news_sources.keys()))
    for e in fetch_news(news_sources[src]):
        st.write(f"• [{e['title']}]({e['link']})")
        if trans_on: st.caption(f"🇨🇳 {GoogleTranslator(source='auto', target='zh-CN').translate(e['title'])}")

st.divider()

# 6. EXPANDERS (Restored Full Data)
with st.expander("🚇 MRT/LRT Status", expanded=True):
    lines = ["NSL", "EWL", "NEL", "CCL", "DTL", "TEL"]
    s_cols = st.columns(6)
    for i, line in enumerate(lines):
        s_cols[i].markdown(f'<div class="status-card status-normal">{line}<br>Normal</div>', unsafe_allow_html=True)

with st.expander("📊 Market Info - Mar 23 Close", expanded=False):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,400.12", "-8.8%")
    m3.metric("Brent Crude", "$92.58", "-13.0%")
    m4.metric("DBS Bank", "$56.42", "-1.7%")

with st.expander("💱 Forex Rates (1 SGD to X)", expanded=False):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("MYR (Ringgit)", "3.071", "-0.12%")
    f2.metric("CNY (Yuan)", "5.378", "+0.05%")
    f3.metric("THB (Baht)", "23.04", "-0.15%")
    f4.metric("JPY (Yen)", "111.28", "-0.88%")
    f5.metric("USD (Dollar)", "0.772", "-0.10%")

with st.expander("🚗 COE Bidding - Mar 2026 (2nd Round)", expanded=False):
    coe_data = [
        ("Cat A", 111890, 3670, 1264, 1895),
        ("Cat B", 115568, 1566, 812, 1185),
        ("Cat C", 78000, 2000, 290, 438),
        ("Cat D", 9589, 987, 546, 726),
        ("Cat E", 118119, 3229, 246, 422)
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

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v4.9 Full Data Restore")
