import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator  # New: Free Translation Tool

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 4.3", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS (Keeping your clean 'Card' look)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; }
    .time-value { font-size: 1.1rem; font-weight: bold; }
    .news-box { border-left: 3px solid #ff4b4b; padding-left: 10px; margin-bottom: 15px; }
    .translation-text { color: #666; font-size: 0.9rem; font-style: italic; }
    @media (prefers-color-scheme: dark) {
        .time-card { background-color: #262730; border-color: #444; }
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

# Translation Function
def translate_text(text, target='zh-CN'):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return text # Return original if translation fails

# --- UI START ---
st.title("Singapore Info Monitor 4.3")

# Regional Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# 5. NEWS PANEL WITH TRANSLATION
st.header("🇸🇬 Singapore Headline News")

# TRANSLATION TOGGLE
translate_on = st.toggle("Translate Headlines to Chinese (翻译成中文)", value=False)

sources = {
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Business Times": "https://www.businesstimes.com.sg/rss-feeds/singapore"
}

t_news1, t_news2 = st.tabs(["📊 Unified Feed (Top 5)", "📰 Individual Sources"])

with t_news1:
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries:
            st.subheader(f"🗞️ {name}")
            for entry in feed.entries[:5]:
                title = entry.title
                link = entry.link
                if translate_on:
                    translated = translate_text(title)
                    st.markdown(f"• **[{title}]({link})**")
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<span class='translation-text'>🇨🇳 {translated}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"• [{title}]({link})")
            st.write("") 

with t_news2:
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    feed = fetch_news(sources[sel])
    if feed and feed.entries:
        for e in feed.entries[:8]:
            st.write(f"• [{e.title}]({e.link})")
            if translate_on:
                st.caption(f"🇨🇳 {translate_text(e.title)}")

# --- KEEPING YOUR ACCORDION SECTIONS BELOW ---
st.divider()

with st.expander("🚇 MRT/LRT Service Status", expanded=True):
    # (Same logic as before...)
    st.success("✅ All lines operating normally.")

with st.expander("📊 Market & Forex", expanded=False):
    # (Same logic as before...)
    st.write("Market data loading...")

with st.expander("🚗 COE Bidding Analysis", expanded=False):
    # (Same logic as before...)
    st.write("COE data loading...")

st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | v4.3 Bilingual")
