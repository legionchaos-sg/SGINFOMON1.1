import streamlit as st
import feedparser
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Silent Auto-Refresh Trigger (Every 3 minutes)
# Running this without a variable assignment keeps it hidden from the UI
st_autorefresh(interval=3 * 60 * 1000, key="newsfeedrefresh_silent")

# 3. Clean CSS for Headline Tags
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; max-width: 1100px; }
    .source-tag { 
        background-color: #f1f3f4; color: #3c4043; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 8px;
    }
    /* Dark mode support for source tags */
    @media (prefers-color-scheme: dark) {
        .source-tag { background-color: #303134; color: #e8eaed; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Simple Header
st.title("Singapore Info Monitor 1.1")
st.divider()

# 5. News Fetching Engine
def fetch_feed(name, url):
    try:
        # 6-second timeout for stability
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return [{"source": name, "title": e.title, "link": e.link, "date": e.get('published', 'Recently')} for e in feed.entries]
    except:
        return []
    return []

sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore",
    "Berita Harian": "https://www.beritaharian.sg/rss/singapura"
}

# 6. Content Display
st.header("Singapore Headline News")
tab_unified, tab_sources = st.tabs(["📊 Unified Top 9", "📰 Individual Sources"])

# Aggregate data from all sources
all_news = []
for name, url in sources.items():
    all_news.extend(fetch_feed(name, url))

with tab_unified:
    if all_news:
        for item in all_news[:9]:
            st.markdown(f"<span class='source-tag'>{item['source']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
            st.caption(f"🕒 {item['date']}")
            st.write("---")
    else:
        st.info("The monitor is currently syncing with news servers. Please wait a moment...")

with tab_sources:
    selected = st.radio("Select Newspaper", list(sources.keys()), horizontal=True)
    items = fetch_feed(selected, sources[selected])
    for item in items[:5]:
        st.markdown(f"### {item['title']}")
        st.write(f"[Read story on {selected}]({item['link']})")
        st.write("---")

# 7. Subtle Footer
st.divider()
st.caption(f"Monitor Active | Automated 3-Min Sync | {datetime.now().year} SPH & Mediacorp Integrated")
