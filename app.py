import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 2.2", page_icon="🇸🇬", layout="wide")

# 2. Silent Auto-Refresh (Every 3 minutes)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .coe-card {
        background-color: #f8f9fa;
        border-top: 4px solid #ff4b4b;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .coe-label { font-size: 0.85rem; font-weight: bold; color: #333; }
    .coe-value { font-size: 1.3rem; font-weight: bold; color: #d32f2f; margin: 5px 0; }
    .coe-stat { font-size: 0.75rem; color: #666; display: flex; justify-content: space-between; margin-top: 3px; }
    .stat-val { font-weight: bold; color: #222; }
    @media (prefers-color-scheme: dark) {
        .coe-card { background-color: #262730; border-top-color: #ff4b4b; }
        .coe-value { color: #ff5252; }
        .coe-stat { color: #aaa; }
        .stat-val { color: #eee; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

@st.cache_data(ttl=180)
def get_market_data():
    tickers = {"STI INDEX": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Crude": "CL=F"}
    data = {}
    for label, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            p = t.fast_info['last_price']
            data[label] = {"p": p, "d": p - t.fast_info['regular_market_previous_close']}
        except: data[label] = {"p": 0, "d": 0}
    return data

def fetch_feed(name, url):
    try:
        res = requests.get(url, timeout=6)
        feed = feedparser.parse(res.content)
        return [{"source": name, "title": e.title, "link": e.link, "date": e.get('published', 'Recent')} for e in feed.entries]
    except: return []

# 5. UI Layout - Clocks & Markets
st.title("Singapore Info Monitor 2.2")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), 
         ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, get_tz_time(tz))

m_data = get_market_data()
m_cols = st.columns(4)
for i, (l, k) in enumerate([("STI INDEX", "STI INDEX"), ("Gold", "Gold"), ("Silver", "Silver"), ("Crude", "Crude")]):
    m_cols[i].metric(l, f"{m_data[k]['p']:,.2f}", f"{m_data[k]['d']:+.2f}")

st.divider()

# 6. Singapore Headline News
st.header("🇸🇬 Singapore Headline News")
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore"
}

tab1, tab2 = st.tabs(["📊 Unified Top 9", "📰 Individual Sources"])

with tab1:
    all_news = []
    for name, url in sources.items(): all_news.extend(fetch_feed(name, url))
    if all_news:
        for item in all_news[:9]:
            st.markdown(f"**{item['source']}**: [{item['title']}]({item['link']})")
            st.caption(f"🕒 {item['date']}")
            st.write("---")
    else: st.info("Syncing News Feed...")

with tab2:
    sel = st.selectbox("Select Source", list(sources.keys()))
    for item in fetch_feed(sel, sources[sel])[:5]:
        st.markdown(f
