import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Silent Auto-Refresh (Every 3 minutes)
st_autorefresh(interval=3 * 60 * 1000, key="market_news_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .market-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .market-label { font-size: 0.8rem; color: #666; font-weight: bold; }
    .market-price { font-size: 1.3rem; font-weight: bold; color: #1a1a1a; margin: 5px 0; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.7rem; color: #6c757d; font-weight: bold; }
    .time-value { font-size: 1.1rem; font-weight: bold; }
    @media (prefers-color-scheme: dark) {
        .market-card { background-color: #1e1e1e; border-color: #333; }
        .market-price { color: #ffffff; }
        .time-card { background-color: #262730; border-color: #333; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    tz = pytz.timezone(zone_name)
    return datetime.now(tz).strftime("%H:%M")

@st.cache_data(ttl=180) # Cache for 3 mins to match refresh
def get_market_data():
    tickers = {
        "STI INDEX": "^STI",
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Crude Oil": "CL=F"
    }
    data = {}
    for label, sym in tickers.items():
        try:
            ticker = yf.Ticker(sym)
            price = ticker.fast_info['last_price']
            change = ticker.fast_info['regular_market_previous_close']
            diff = price - change
            data[label] = {"price": price, "diff": diff}
        except:
            data[label] = {"price": 0, "diff": 0}
    return data

def fetch_feed(name, url):
    try:
        res = requests.get(url, timeout=6)
        feed = feedparser.parse(res.content)
        return [{"source": name, "title": e.title, "link": e.link, "date": e.get('published', 'Recent')} for e in feed.entries]
    except: return []

# 5. UI Layout - Clocks
st.title("Singapore Info Monitor 1.1")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), 
         ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]

for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f"<div class='time-card'><div class='time-city'>{city}</div><div class='time-value'>{get_tz_time(tz)}</div></div>", unsafe_allow_html=True)

st.write("") # Spacer

# 6. Market Overview Panel
st.subheader("📊 Market Overview")
m_data = get_market_data()
m_cols = st.columns(4)

labels = ["STI INDEX", "Gold Price", "Silver price", "Crude Price"]
keys = ["STI INDEX", "Gold", "Silver", "Crude Oil"]

for i, label in enumerate(labels):
    val = m_data[keys[i]]
    color = "#28a745" if val['diff'] >= 0 else "#dc3545"
    arrow = "▲" if val['diff'] >= 0 else "▼"
    
    with m_cols[i]:
        st.markdown(f"""
            <div class="market-card">
                <div class="market-label">{label}</div>
                <div class="market-price">{val['price']:,.2f}</div>
                <div style="color:{color}; font-size:0.85rem; font-weight:bold;">
                    {arrow} {abs(val['diff']):,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# 7. News Panel
st.header("Singapore Headline News")
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
    for item in all_news[:9]:
        st.markdown(f"**{item['source']}**: [{item['title']}]({item['link']})")
        st.caption(f"🕒 {item['date']}")
        st.write("---")

with tab2:
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    for item in fetch_feed(sel, sources[sel])[:5]:
        st.markdown(f"#### [{item['title']}]({item['link']})")
        st.caption(item['date'])
        st.write("---")

# 8. Footer
st.caption(f"Full Monitor Active | Market Data via Yahoo Finance | Last Sync: {datetime.now().strftime('%H:%M:%S')}")
