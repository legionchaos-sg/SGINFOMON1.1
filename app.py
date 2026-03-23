import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 5.1", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 2. Styles
st.markdown("""
    <style>
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .coe-card { background-color: #f8f9fa; border-left: 4px solid #ff4b4b; padding: 10px; border-radius: 6px; min-height: 120px; }
    .news-tag { font-size: 0.65rem; background: #eee; padding: 2px 4px; border-radius: 3px; color: #666; margin-right: 5px; }
    @media (prefers-color-scheme: dark) { .time-card, .coe-card { background-color: #262730; border-color: #444; } }
    </style>
    """, unsafe_allow_html=True)

# 3. Helpers
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

def fetch_news(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        feed = feedparser.parse(resp.content)
        return [{'title': e.title, 'link': e.link} for e in feed.entries[:10]]
    except: return []

# --- SECTION 1: REGIONAL TIME ---
st.subheader("🌐 Regional Time")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# --- SECTION 2: SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
trans_on = st.toggle("Translate to Chinese (翻译中)", value=False)
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

tab_uni, tab_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])
with tab_uni:
    for name, url in news_sources.items():
        data = fetch_news(url)
        if data:
            item = data[0]
            st.write(f"<span class='news-tag'>{name}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

with tab_src:
    src_choice = st.selectbox("Choose News Outlet", list(news_sources.keys()))
    for e in fetch_news(news_sources[src_choice]):
        st.write(f"• [{e['title']}]({e['link']})")
        if trans_on:
            translated = GoogleTranslator(source='auto', target='zh-CN').translate(e['title'])
            st.caption(f"🇨🇳 {translated}")

st.divider()

# --- SECTION 3: MARKET INFO ---
st.header("📊 Market Information")
# Data based on March 23, 2026 Close
m1, m2, m3, m4 = st.columns(4)
m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
m2.metric("Gold (Spot)", "$4,368.70", "-4.41%")
m3.metric("Silver (Spot)", "$64.75", "-5.07%")
m4.metric("Brent Crude", "$112.91", "+0.64%")

st.divider()

# --- SECTION 4: FOREX RATES ---
st.header("💱 Forex Rates (1 SGD to X)")
f1, f2, f3, f4, f5, f6 = st.columns(6)
f1.metric("CNY (Yuan)", "5.382", "+0.20%")
f2.metric("THB (Baht)", "25.435", "-0.26%")
f3.metric("JPY (Yen)", "124.22", "+0.01%")
f4.metric("MYR (Ringgit)", "3.071", "+0.17%")
f5.metric("AUD (Dollar)", "1.119", "+0.60%")
f6.metric("USD (Dollar)", "0.781", "+0.19%")

st.divider()

# --- SECTION 5: COE BIDDING ---
st.header("🚗 COE Bidding - Mar 2026 (2nd Round)")
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

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v5.1 Layout Locked")
