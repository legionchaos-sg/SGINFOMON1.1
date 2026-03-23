import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 4.5", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; }
    .time-value { font-size: 1.1rem; font-weight: bold; }
    .news-tag { font-size: 0.7rem; background: #eee; padding: 2px 5px; border-radius: 4px; color: #666; margin-right: 8px; }
    .translation-text { color: #d32f2f; font-size: 0.9rem; font-style: italic; display: block; margin-left: 25px; }
    .coe-card { background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 8px; min-height: 140px; }
    @media (prefers-color-scheme: dark) {
        .time-card, .coe-card { background-color: #262730; border-color: #444; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Helper Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

@st.cache_data(ttl=600) # Cache news for 10 mins to prevent lag
def fetch_pooled_news(sources_dict):
    pool = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for name, url in sources_dict.items():
        try:
            resp = requests.get(url, timeout=5, headers=headers)
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:3]: # Take top 3 from each to build the pool
                pool.append({'source': name, 'title': entry.title, 'link': entry.link})
        except: continue
    return pool

@st.cache_data(ttl=3600) # Cache translations for 1 hour
def translate_cached(text):
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except: return "Translation Error"

# --- UI START ---
st.title("Singapore Info Monitor 4.5")

# Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# 5. POOLED NEWS PANEL (TOP 5 ONLY)
st.header("🗞️ Top 5 Regional Headlines")
translate_on = st.toggle("Translate Headlines (中)", value=False)

news_sources = {
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Business Times": "https://www.businesstimes.com.sg/rss-feeds/singapore",
    "Mothership": "https://mothership.sg/feed/"
}

pooled_data = fetch_pooled_news(news_sources)

if pooled_data:
    # We display only the top 5 from the entire gathered pool
    for item in pooled_data[:5]:
        st.markdown(f"<span class='news-tag'>{item['source']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
        if translate_on:
            chinese = translate_cached(item['title'])
            st.markdown(f"<span class='translation-text'>🇨🇳 {chinese}</span>", unsafe_allow_html=True)
else:
    st.error("Could not load news pool. Check internet connection.")

st.divider()

# --- DROP
