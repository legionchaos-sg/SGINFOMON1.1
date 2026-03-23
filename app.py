import streamlit as st
import feedparser
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Adaptive CSS for Clean News Cards
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1100px; }
    .news-item { margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eeeeee33; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Top-Right Toggle
col_title, col_mode = st.columns([4, 1])
with col_title:
    st.title("Singapore Info Monitor 1.1")
with col_mode:
    # Small dropdown for manual mode reference
    st.selectbox("Mode", ["Default", "Light", "Dark"], label_visibility="collapsed")

st.write(f"**System Status:** Online | {datetime.now().strftime('%H:%M:%S')} SGT")
st.divider()

# 4. News Function (Enforced Top 5)
def get_news(url):
    try:
        # We parse the feed and immediately slice to the first 5 entries
        feed = feedparser.parse(url)
        return feed.entries[:5] 
    except Exception:
        return []

# 5. Panel 1: Singapore Headline News
st.header("Singapore Headline News")

# Creating tabs for a compact layout
tab_cna, tab_zb = st.tabs(["CNA (English)", "Lianhe Zaobao (联合早报)"])

with tab_cna:
    # CNA Singapore News Feed
    cna_url = "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"
    news_items = get_news(cna_url)
    
    if news_items:
        for entry in news_items:
            st.markdown(f"### [{entry.title}]({entry.link})")
            st.caption(f"🕒 {entry.published if 'published' in entry else 'Just in'}")
    else:
        st.error("CNA feed is currently unreachable.")

with tab_zb:
    # Updated 2026 Zaobao Realtime Feed
    zb_url = "https://www.zaobao.com.sg/rss/realtime/singapore"
    news_items = get_news(zb_url)
    
    if news_items:
        for entry in news_items:
            st.markdown(f"### [{entry.title}]({entry.link})")
            # Handling Chinese timestamps
            st.caption(f"📅 {entry.published if 'published' in entry else '最新消息'}")
    else:
        st.info("Lianhe Zaobao feed is updating. Please refresh in a moment.")

# 6. Footer
st.divider()
st.caption("Version 1.2 Stable | Top 5 Headlines Only")
