import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 8.2", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_82")
st.set_page_config(page_title="SG INFO MON 8.3", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_83")

# 2. CSS Styling
st.markdown("""
@@ -44,9 +44,9 @@
        cols[i%2].markdown(f'<div style="padding:10px; border-bottom:1px solid #ddd;"><b>{brand}</b><br><span style="color:#007bff; font-size:1.1rem;">${p:.2f}</span><br>{tr}</div>', unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 Singapore Info Monitor 8.2")
st.title("🇸🇬 Singapore Info Monitor 8.3")

# 4. Country Clocks (Reverted to Country Names)
# 4. Country Clocks (Verified Country Names)
countries = [
    ("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), 
    ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), 
@@ -58,38 +58,40 @@

st.divider()

# 5. Refined News Section (Unified Top 3)
# 5. News Section (1 Headline per Source for Unified)
st.header("🗞️ Singapore Headlines")
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
    "Mothership": "https://mothership.sg/feed/",
    "8world News": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176",
    "Shin Min Daily": "https://www.shinmin.sg/rss" # Fallback to standard SPH Chinese if specific RSS is down
}

col_n1, col_n2 = st.columns([2, 1])
with col_n1:
    view_mode = st.radio("View Mode:", ["Unified (Top 3 per source)", "CNA Only", "Straits Times Only", "Mothership Only"], horizontal=True)
    view_mode = st.radio("View Mode:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only", "Shin Min Only"], horizontal=True)
with col_n2:
    do_tr = st.checkbox("Translate (Chinese)")
    do_tr = st.checkbox("Translate English to Chinese")

news_list = []
if "Unified" in view_mode:
    for src, url in news_sources.items():
        try:
            feed = feedparser.parse(requests.get(url, timeout=5).content)
            # Take only the top 3 items from each source
            for entry in feed.entries[:3]:
            if feed.entries:
                entry = feed.entries[0] # STRICT: ONLY THE #1 TOP STORY
                news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
        except: pass
else:
    src_key = view_mode.replace(" Only", "")
    try:
        feed = feedparser.parse(requests.get(news_sources[src_key], timeout=5).content)
        for entry in feed.entries[:10]:
        for entry in feed.entries[:10]: # Individual views still show more
            news_list.append({'src': src_key, 'title': entry.title, 'link': entry.link})
    except: pass

# Translation Logic
# Translation (Only applied to non-Chinese sources if needed, but simple logic for all here)
tr_list = []
if do_tr and news_list:
    try: tr_list = GoogleTranslator(target='zh-CN').translate("\n".join([x['title'] for x in news_list])).split("\n")
@@ -98,11 +100,13 @@
for i, item in enumerate(news_list):
    st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
    if do_tr and i < len(tr_list):
        st.markdown(f"<div class='trans-box'>🇨🇳 {tr_list[i].strip()}</div>", unsafe_allow_html=True)
        # Only show translation if the source is likely English (CNA, ST, MS)
        if item['src'] in ["CNA", "Straits Times", "Mothership"]:
            st.markdown(f"<div class='trans-box'>🇨🇳 {tr_list[i].strip()}</div>", unsafe_allow_html=True)

st.divider()

# 6. Market Expanders
# 6. Market & Forex (As per previous request)
with st.expander("📈 Market Indices & Commodities", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,892.27", "-0.30%")
