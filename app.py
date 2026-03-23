import streamlit as st
import feedparser
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh Trigger (3 mins = 180,000 milliseconds)
# This will force the entire script to rerun every 3 minutes
refresh_count = st_autorefresh(interval=3 * 60 * 1000, key="newsfeedrefresh")

# 3. Capture exact refresh time
last_refresh = datetime.now().strftime("%H:%M:%S")

# 4. Custom Styling for the "Refresh Bar"
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; max-width: 1200px; }
    .refresh-status {
        background-color: #007bff15;
        padding: 5px 15px;
        border-radius: 5px;
        border: 1px solid #007bff33;
        color: #007bff;
        font-weight: bold;
        text-align: right;
    }
    .source-tag { 
        background-color: #f1f3f4; color: #3c4043; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 5. Header with Refresh Visibility
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("Singapore Info Monitor 1.1")

with col_status:
    # This is now highly visible in the top right
    st.markdown(f"<div class='refresh-status'>🕒 Last Refresh: {last_refresh} SGT</div>", unsafe_allow_html=True)
    st.caption(f"Automatic update every 3 mins (Cycle: {refresh_count})")

st.divider()

# 6. Optimized News Fetcher
def fetch_feed(name, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return [{"source": name, "title": e.title, "link": e.link, "date": e.get('published', 'Just now')} for e in feed.entries]
    except:
        return []
    return []

sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore"
}

# 7. Content Layout
st.header("Singapore Headline News")
tab_unified, tab_sources = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])

# Gather all data
all_news = []
for name, url in sources.items():
    all_news.extend(fetch_feed(name, url))

with tab_unified:
    if all_news:
        # Display top 9 from combined sources
        for item in all_news[:9]:
            st.markdown(f"<span class='source-tag'>{item['source']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
            st.caption(f"🕒 {item['date']}")
            st.write("---")
    else:
        st.warning("All news sources are currently stalling. The system will auto-retry in 3 minutes.")

with tab_sources:
    selected = st.radio("Choose Source", list(sources.keys()), horizontal=True)
    items = fetch_feed(selected, sources[selected])
    for item in items[:5]:
        st.markdown(f"### {item['title']}")
        st.write(f"[Source: {selected}]({item['link']})")
        st.write("---")
