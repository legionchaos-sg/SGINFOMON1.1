import streamlit as st
import feedparser
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1100px; }
    .news-card { margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Top-Right Toggle
col_title, col_mode = st.columns([4, 1])
with col_title:
    st.title("Singapore Info Monitor 1.1")
with col_mode:
    st.selectbox("Mode", ["Default", "Light", "Dark"], label_visibility="collapsed")

st.write(f"**System Status:** Online | {datetime.now().strftime('%H:%M:%S')} SGT")
st.divider()

# 4. Enhanced News Function with Keyword Filtering
def get_news(url, limit=5, filter_keyword=None):
    try:
        feed = feedparser.parse(url)
        entries = feed.entries
        
        if filter_keyword:
            # Filter entries where keyword is in title or description (case-insensitive)
            filtered = [
                e for e in entries 
                if filter_keyword.lower() in e.title.lower() or 
                (hasattr(e, 'summary') and filter_keyword.lower() in e.summary.lower())
            ]
            return filtered[:limit]
        
        return entries[:limit]
    except Exception:
        return []

# 5. Panel 1: Singapore Headline News
st.header("Singapore Headline News")

tab_cna, tab_zb, tab_cnn = st.tabs(["CNA", "Lianhe Zaobao", "CNN (Filtered)"])

with tab_cna:
    items = get_news("https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416")
    for e in items:
        st.markdown(f"### [{e.title}]({e.link})")
        st.caption(f"🕒 {e.published if 'published' in e else 'Recent'}")

with tab_zb:
    items = get_news("https://www.zaobao.com.sg/rss/realtime/singapore")
    for e in items:
        st.markdown(f"### [{e.title}]({e.link})")
        st.caption(f"📅 {e.published if 'published' in e else '最新'}")

with tab_cnn:
    # CNN World RSS
    cnn_url = "http://rss.cnn.com/rss/edition_world.rss"
    # We filter specifically for "Singapore"
    items = get_news(cnn_url, filter_keyword="Singapore")
    
    if items:
        st.subheader("Global Perspective on Singapore")
        for e in items:
            st.markdown(f"### [{e.title}]({e.link})")
            st.caption(f"🌍 CNN World | {e.published if 'published' in e else ''}")
    else:
        st.info("No Singapore-specific news found on CNN World in the last 24 hours.")

# 6. Footer
st.divider()
st.caption("Version 1.2 | Multi-Source News Monitor")
