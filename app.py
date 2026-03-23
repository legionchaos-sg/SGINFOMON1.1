import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Silent Auto-Refresh (Every 3 minutes)
st_autorefresh(interval=3 * 60 * 1000, key="newsfeed_and_time_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .time-city { font-size: 0.8rem; color: #6c757d; font-weight: bold; text-transform: uppercase; }
    .time-value { font-size: 1.2rem; font-weight: bold; color: #212529; }
    .source-tag { 
        background-color: #f1f3f4; color: #3c4043; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 8px;
    }
    @media (prefers-color-scheme: dark) {
        .time-card { background-color: #1e1e1e; border-color: #333; }
        .time-value { color: #ffffff; }
        .time-city { color: #aaaaaa; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Time Logic Function
def get_tz_time(zone_name):
    tz = pytz.timezone(zone_name)
    return datetime.now(tz).strftime("%H:%M")

# 5. Header & Time Monitor Panel
st.title("Singapore Info Monitor 1.1")

# Creating the Clock Bar
t_col1, t_col2, t_col3, t_col4, t_col5, t_col6 = st.columns(6)

time_zones = [
    ("Singapore", "Asia/Singapore", t_col1),
    ("Bangkok", "Asia/Bangkok", t_col2),
    ("Japan", "Asia/Tokyo", t_col3),
    ("Indonesia", "Asia/Jakarta", t_col4),
    ("Philippines", "Asia/Manila", t_col5),
    ("Brisbane", "Australia/Brisbane", t_col6)
]

for city, zone, col in time_zones:
    with col:
        st.markdown(f"""
            <div class="time-card">
                <div class="time-city">{city}</div>
                <div class="time-value">{get_tz_time(zone)}</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# 6. News Fetching Engine
def fetch_feed(name, url):
    try:
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
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore"
}

# 7. Content Display
st.header("Singapore Headline News")
tab_unified, tab_sources = st.tabs(["📊 Unified Top 9", "📰 Individual Sources"])

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
        st.info("Syncing latest news...")

# 8. Footer
st.caption(f"Region Monitor Active | Automated Sync | {datetime.now().strftime('%Y')}")
