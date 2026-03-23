import streamlit as st
import feedparser
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1100px; }
    .news-card { padding: 10px; border-bottom: 1px solid #eeeeee22; margin-bottom: 10px; }
    .source-tag { font-size: 0.8rem; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Top-Right Toggle
col_title, col_mode = st.columns([4, 1])
with col_title:
    st.title("Singapore Info Monitor 1.1")
with col_mode:
    theme = st.selectbox("Mode", ["Default", "Light", "Dark"], label_visibility="collapsed")

st.write(f"**System Status:** Online | {datetime.now().strftime('%H:%M:%S')} SGT")
st.divider()

# 4. News Function
def get_news(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries[:5] # Get top 5 news items
    except:
        return []

# 5. Panel 1: Singapore Headline News
st.header("Singapore Headline News")

tab1, tab2 = st.tabs(["CNA (English)", "Lianhe Zaobao (Chinese)"])

with tab1:
    cna_news = get_news("https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416")
    if cna_news:
        for entry in cna_news:
            st.markdown(f"**[{entry.title}]({entry.link})**")
            st.caption(f"Published: {entry.published if 'published' in entry else 'Just now'}")
            st.write("---")
    else:
        st.error("Unable to load CNA feed.")

with tab2:
    # Updated 2026 Zaobao Realtime Feed
    zb_news = get_news("https://www.zaobao.com.sg/rss/realtime/singapore")
    
    if zb_news:
        for entry in zb_news:
            st.markdown(f"**[{entry.title}]({entry.link})**")
            st.caption(f"🕒 {entry.published if 'published' in entry else 'Just updated'}")
            st.write("---")
    else:
        # Improved error message for troubleshooting
        st.warning("⚠️ Zaobao feed is currently restricted or refreshing. Please check back in 5 minutes.")
        if st.button("Manual Refresh"):
            st.rerun()

# 6. Footer
st.caption("Version 1.2 | Data: RSS Feeds from Mediacorp & SPH Media")
