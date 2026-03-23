import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config & Auto-Refresh
st.set_page_config(page_title="SG INFO MON 4.7", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 2. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.7rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; }
    .status-card { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.8rem; }
    .status-normal { background-color: #28a745; }
    .status-advisory { background-color: #ffc107; color: #212529; }
    .news-tag { font-size: 0.65rem; background: #eee; padding: 2px 4px; border-radius: 3px; color: #666; margin-right: 5px; }
    .translation-text { color: #d32f2f; font-size: 0.85rem; font-style: italic; margin-left: 20px; display: block; }
    .coe-card { background-color: #f8f9fa; border-left: 4px solid #ff4b4b; padding: 10px; border-radius: 6px; min-height: 130px; }
    @media (prefers-color-scheme: dark) { .time-card, .coe-card { background-color: #262730; border-color: #444; } }
    </style>
    """, unsafe_allow_html=True)

# 3. Helper Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

@st.cache_data(ttl=600)
def fetch_news_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        return feedparser.parse(requests.get(url, timeout=5, headers=headers).content)
    except: return None

@st.cache_data(ttl=3600)
def translate_cached(text):
    try: return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except: return "Error"

# --- UI START ---
st.title("Singapore Info Monitor 4.7")

# 4. Regional Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# 5. News Panel (Restored Source Options)
st.header("🇸🇬 Singapore Headline News")
trans_on = st.toggle("Translate to Chinese (翻译中)", value=False)
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Business Times": "https://www.businesstimes.com.sg/rss-feeds/singapore",
    "Mothership": "https://mothership.sg/feed/"
}

tab_unified, tab_sources = st.tabs(["📊 Unified (Top 5 Pool)", "📰 Select Source"])

with tab_unified:
    pool = []
    for name, url in news_sources.items():
        feed = fetch_news_data(url)
        if feed and feed.entries:
            for e in feed.entries[:2]: # Small slice for fast pooling
                pool.append({'source': name, 'title': e.title, 'link': e.link})
    for item in pool[:5]:
        st.markdown(f"<span class='news-tag'>{item['source']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
        if trans_on: st.markdown(f"<span class='translation-text'>🇨🇳 {translate_cached(item['title'])}</span>", unsafe_allow_html=True)

with tab_sources:
    sel_name = st.selectbox("Choose News Outlet", list(news_sources.keys()))
    feed = fetch_news_data(news_sources[sel_name])
    if feed and feed.entries:
        for e in feed.entries[:8]:
            st.markdown(f"• **[{e.title}]({e.link})**")
            if trans_on: st.markdown(f"<span class='translation-text'>🇨🇳 {translate_cached(e.title)}</span>", unsafe_allow_html=True)

st.divider()

# 6. ALL EXPANDERS
with st.expander("🚇 MRT/LRT Service Status", expanded=True):
    trains = {"NSL": "Normal", "EWL": "Normal", "NEL": "Normal", "CCL": "Advisory", "DTL": "Normal", "TEL": "Normal"}
    s_cols = st.columns(6)
    for i, (line, status) in enumerate(trains.items()):
        bg = "status-normal" if status == "Normal" else "status-advisory"
        s_cols[i].markdown(f'<div class="status-card {bg}">{line}<br>{status}</div>', unsafe_allow_html=True)

with st.expander("📊 Market Info", expanded=False):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57")
    m2.metric("Gold", "$4,400.12", "-114.20")
    m3.metric("Silver", "$67.42", "-2.24")
    m4.metric("Brent Crude", "$113.15", "+0.86")

with st.expander("💱 Forex Rates (1 SGD to X)", expanded=False):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("MYR", "3.0717", "+0.17%")
    f2.metric("CNY", "5.3142", "-0.05%")
    f3.metric("THB", "26.410", "+0.12%")
    f4.metric("JPY", "112.45", "-0.22%")
    f5.metric("AUD", "1.1241", "+0.08%")

with st.expander("🚗 COE Bidding - Mar 2026", expanded=False):
    coe = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, price, diff, q, b) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><div style="font-weight:bold;font-size:0.8rem;">{cat}</div><div style="color:#d32f2f;font-weight:bold;font-size:1.1rem;">${price:,}</div><div style="color:#d32f2f;font-size:0.8rem;font-weight:bold;">▲ ${diff:,}</div><div style="font-size:0.7rem;margin-top:5px;color:#666;">Alloc: {q}<br>Bids: {b}</div></div>', unsafe_allow_html=True)

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v4.7 Full Tab Restore")
