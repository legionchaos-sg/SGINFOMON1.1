import streamlit as st
import feedparser
import requests
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Capture Refresh Time (This runs every time the page loads)
last_refresh = datetime.now().strftime("%d %b %Y, %H:%M:%S")

# 3. Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .refresh-text { font-size: 0.9rem; color: #666; font-weight: 500; }
    .source-tag { 
        background-color: #f1f3f4; color: #3c4043; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Header & New Refresh UI
col_title, col_refresh = st.columns([3, 1.5])

with col_title:
    st.title("Singapore Info Monitor 1.1")

with col_refresh:
    # Right-aligned refresh info and manual trigger
    st.markdown(f"<p class='refresh-text'>⏱️ Last Page Refresh: {last_refresh} SGT</p>", unsafe_allow_html=True)
    if st.button("🔄 Pull Latest Updates", use_container_width=True):
        st.rerun()

st.divider()

# 5. News Logic (The Core Engine)
def fetch_feed(name, url):
    try:
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return [{"source": name, "title": e.title, "link": e.link, "date": e.get('published', 'Recent')} for e in feed.entries]
    except:
        return []
    return []

sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore"
}

# 6. Content Display
st.header("Singapore Headline News")
tab_combined, tab_sources = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])

all_news = []
for name, url in sources.items():
    all_news.extend(fetch_feed(name, url))

with tab_combined:
    if all_news:
        for item in all_news[:9]:
            st.markdown(f"<span class='source-tag'>{item['source']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
            st.caption(f"🕒 {item['date']}")
            st.write("---")
    else:
        st.warning("All sources are currently stalling. Please click 'Pull Latest Updates' above.")

with tab_sources:
    selected = st.radio("Choose Source", list(sources.keys()), horizontal=True)
    specific_news = fetch_feed(selected, sources[selected])
    for item in specific_news[:5]:
        st.markdown(f"### {item['title']}")
        st.write(f"[Read story on {selected}]({item['link']})")
        st.write("---")

# 7. Footer
st.caption("Version 1.5 | Professional News Aggregator")
