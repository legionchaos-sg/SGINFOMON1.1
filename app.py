import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 4.8", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 2. Helper Functions (Removed @st.cache_data to fix Python 3.14 NameError)
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

def fetch_news_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, timeout=5, headers=headers)
        feed = feedparser.parse(resp.content)
        # Return a simple list of dicts (fast and safe)
        return [{'source': '', 'title': e.title, 'link': e.link} for e in feed.entries[:10]]
    except: return []

def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except: return "翻译错误"

# --- UI START ---
st.title("Singapore Info Monitor 4.8")

# 3. Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, get_tz_time(tz))

st.divider()

# 4. News Panel with Tabs & Toggle
st.header("🗞️ Singapore Headline News")
trans_on = st.toggle("Translate (中)", value=False)
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

tab1, tab2 = st.tabs(["📊 Unified Pool", "📰 By Source"])

with tab1:
    pool = []
    for name, url in news_sources.items():
        entries = fetch_news_data(url)
        for e in entries[:2]:
            e['source'] = name
            pool.append(e)
    for item in pool[:5]:
        st.write(f"**{item['source']}**: [{item['title']}]({item['link']})")
        if trans_on: st.caption(f"🇨🇳 {translate_text(item['title'])}")

with tab2:
    src = st.selectbox("Select Outlet", list(news_sources.keys()))
    entries = fetch_news_data(news_sources[src])
    for e in entries[:8]:
        st.write(f"• [{e['title']}]({e['link']})")
        if trans_on: st.caption(f"🇨🇳 {translate_text(e['title'])}")

st.divider()

# 5. Expanders (Ensuring they are all here!)
with st.expander("📊 Market & Forex", expanded=False):
    c1, c2 = st.columns(2)
    with c1: st.metric("STI Index", "4,841.30", "-107.57")
    with c2: st.metric("USD/SGD", "1.34", "+0.01")

with st.expander("🚗 COE Bidding", expanded=False):
    st.write("Cat A: $111,890 | Cat B: $115,568")

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v4.8 Fix")
