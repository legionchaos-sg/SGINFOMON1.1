import streamlit as st
import feedparser
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .source-tag { 
        background-color: #ff4b4b; color: white; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.7rem; font-weight: bold; 
        margin-right: 10px; vertical-align: middle;
    }
    .news-item { margin-bottom: 1.2rem; border-bottom: 1px solid #eeeeee33; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & UI Toggle
col_title, col_mode = st.columns([4, 1])
with col_title:
    st.title("Singapore Info Monitor 1.1")
with col_mode:
    st.selectbox("Mode", ["Default", "Light", "Dark"], label_visibility="collapsed")

st.divider()

# 4. News Processing Engine
def fetch_news(name, url):
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            results.append({
                "source": name,
                "title": entry.title,
                "link": entry.link,
                "date": entry.get('published', 'Recently')
            })
        return results
    except:
        return []

# Define Sources (SPH & Mediacorp)
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore",
    "Berita Harian": "https://www.beritaharian.sg/rss/singapura",
    "Tamil Murasu": "https://www.tamilmurasu.com.sg/rss/singapore",
    "Shin Min Daily": "https://www.shinmin.sg/rss/news"
}

# 5. Main Panels
tab_combined, tab_individual = st.tabs(["📊 Unified Top 9 Headlines", "📰 Source Specific (Top 5)"])

# Collect all news for the Unified view
all_news = []
for name, url in sources.items():
    all_news.extend(fetch_news(name, url))

with tab_combined:
    st.subheader("Latest Across All Singapore Media")
    # Take the top 9 from the combined list
    top_9 = all_news[:9]
    if top_9:
        for item in top_9:
            st.markdown(f"""
            <div class="news-item">
                <span class="source-tag">{item['source']}</span>
                <strong><a href="{item['link']}" style="text-decoration:none;">{item['title']}</a></strong>
                <br><small>🕒 {item['date']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aggregating latest news... please refresh in a moment.")

with tab_individual:
    # Let user pick the specific source to see Top 5
    source_choice = st.radio("Select News Source:", list(sources.keys()), horizontal=True)
    st.write(f"### Top 5 Headlines from {source_choice}")
    
    source_news = fetch_news(source_choice, sources[source_choice])
    for item in source_news[:5]:
        st.markdown(f"**[{item['title']}]({item['link']})**")
        st.caption(f"Published: {item['date']}")
        st.write("---")

# 6. Footer
st.divider()
st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} SGT | Sources: SPH Media, Mediacorp")
