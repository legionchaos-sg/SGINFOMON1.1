import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 2.3", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .coe-card {
        background-color: #f8f9fa; border-top: 4px solid #ff4b4b;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .coe-label { font-size: 0.85rem; font-weight: bold; color: #333; }
    .coe-value { font-size: 1.3rem; font-weight: bold; color: #d32f2f; margin: 5px 0; }
    .coe-stat { font-size: 0.75rem; color: #666; display: flex; justify-content: space-between; margin-top: 2px; }
    .stat-val { font-weight: bold; color: #222; }
    @media (prefers-color-scheme: dark) {
        .coe-card { background-color: #262730; border-top-color: #ff4b4b; }
        .coe-value { color: #ff5252; } .coe-stat { color: #aaa; } .stat-val { color: #eee; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

@st.cache_data(ttl=180)
def get_market_data():
    # Real-time Tickers: STI Index, Gold Spot, Silver Spot, WTI Crude
    tickers = {"STI": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Crude": "CL=F"}
    results = {}
    for label, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            p = t.fast_info['last_price']
            results[label] = {"p": p, "d": p - t.fast_info['regular_market_previous_close']}
        except: results[label] = {"p": 0.0, "d": 0.0}
    return results

# 5. Clocks
st.title("Singapore Info Monitor 2.3")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, get_tz_time(tz))

# 6. Market Overview (Panel 1)
st.subheader("📊 Market Overview")
m_data = get_market_data()
m_cols = st.columns(4)
market_items = [("STI INDEX", "STI"), ("Gold Price", "Gold"), ("Silver Price", "Silver"), ("Crude Price", "Crude")]

for i, (label, key) in enumerate(market_items):
    m_cols[i].metric(label, f"{m_data[key]['p']:,.2f}", f"{m_data[key]['d']:+.2f}")

st.divider()

# 7. Singapore Headline News (Panel 2)
st.header("🇸🇬 Singapore Headline News")
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"
}

all_news = []
for name, url in sources.items():
    try:
        feed = feedparser.parse(requests.get(url, timeout=5).content)
        for entry in feed.entries[:4]:
            all_news.append(f"**{name}**: [{entry.title}]({entry.link})")
    except: pass

if all_news:
    for news_item in all_news[:8]:
        st.markdown(news_item)
else:
    st.info("Refreshing news feed...")

st.divider()

# 8. CURRENT COE STATS (Panel 3)
st.header("🚗 CURRENT COE STATS")
st.caption("Results: 2nd Bidding March 2026 (Published Mar 18)")

# Actual Data for March 2026 2nd Round
coe_results = [
    {"cat": "CAT A", "desc": "<1.6L/130bhp", "price": 111890, "quota": 1264, "bids": 1895},
    {"cat": "CAT B", "desc": ">1.6L/130bhp", "price": 115568, "quota": 812, "bids": 1185},
    {"cat": "CAT C", "desc": "Goods/Bus", "price": 78000, "quota": 290, "bids": 438},
    {"cat": "CAT D", "desc": "Motorcycles", "price": 9589, "quota": 546, "bids": 726},
    {"cat": "CAT E", "desc": "Open Category", "price": 118119, "quota": 246, "bids": 422}
]

c_cols = st.columns(5)
for i, res in enumerate(coe_results):
    with c_cols[i]:
        st.markdown(f"""
            <div class="coe-card">
                <div class="coe-label">{res['cat']}</div>
                <div style="font-size:0.7rem; color:#888;">{res['desc']}</div>
                <div class="coe-value">${res['price']:,}</div>
                <hr style="margin: 8px 0; border:0; border-top:1px solid #ddd;">
                <div class="coe-stat"><span>COE Issued:</span><span class="stat-val">{res['quota']}</span></div>
                <div class="coe-stat"><span>Bids Recv:</span><span class="stat-val">{res['bids']}</span></div>
            </div>
        """, unsafe_allow_html=True)

# 9. Footer
st.divider()
st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} | Data: Yahoo Finance / LTA")
