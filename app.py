import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Silent Auto-Refresh (Every 3 minutes)
st_autorefresh(interval=3 * 60 * 1000, key="full_monitor_refresh")

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
    .time-city { font-size: 0.7rem; color: #6c757d; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .source-tag { 
        background-color: #f1f3f4; color: #3c4043; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 8px;
    }
    @media (prefers-color-scheme: dark) {
        .time-card { background-color: #1e1e1e; border-color: #333; }
        .time-value { color: #ffffff; }
        .time-city { color: #aaaaaa; }
        .source-tag { background-color: #303134; color: #e8eaed; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Core Functions
def get_tz_time(zone_name):
    try:
        tz = pytz.timezone(zone_name)
        return datetime.now(tz).strftime("%H:%M")
    except:
        return "--:--"

def fetch_feed(name, url):
    try:
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return [{"source": name, "title": e.title, "link": e.link, "date": e.get('published', 'Recently')} for e in feed.entries]
    except:
        return []
    return []

# 5. Header & Regional Clocks
st.title("Singapore Info Monitor 1.1")

t_cols = st.columns(6)
time_zones = [
    ("Singapore", "Asia/Singapore"),
    ("Bangkok", "Asia/Bangkok"),
    ("Japan", "Asia/Tokyo"),
    ("Indonesia", "Asia/Jakarta"),
    ("Philippines", "Asia/Manila"),
    ("Brisbane", "Australia/Brisbane")
]

for i, (city, zone) in enumerate(time_zones):
    with t_cols[i]:
        st.markdown(f"""
            <div class="time-card">
                <div class="time-city">{city}</div>
                <div class="time-value">{get_tz_time(zone)}</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# 6. News Sources Configuration
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore",
    "Berita Harian": "https://www.beritaharian.sg/rss/singapura"
}

# 7. Main Tabs
tab_unified, tab_individual = st.tabs(["📊 Unified Top 9", "📰 Individual Sources"])

with tab_unified:
    st.subheader("Global/Local Headlines")
    all_news = []
    # Fetch all for the unified view
    for name, url in sources.items():
        all_news.extend(fetch_feed(name, url))
    
    if all_news:
        for item in all_news[:9]:
            st.markdown(f"<span class='source-tag'>{item['source']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
            st.caption(f"🕒 {item['date']}")
            st.write("---")
    else:
        st.info("Gathering latest news from all channels...")

with tab_individual:
    # Source Selector
    selected_source = st.selectbox("Select News Outlet", list(sources.keys()))
    st.write(f"### Top 5 Headlines: {selected_source}")
    
    # Fetch specifically for the selection
    source_items = fetch_feed(selected_source, sources[selected_source])
    
    if source_items:
        for item in source_items[:5]:
            st.markdown(f"#### [{item['title']}]({item['link']})")
            st.caption(f"Published: {item['date']}")
            st.write("---")
    else:
        st.warning(f"Unable to reach {selected_source} at this moment.")

# 8. Footer
st.divider()
st.caption(f"Version 1.9 | Regional Command Center | Last Sync: {datetime.now().strftime('%H:%M:%S')} SGT")
