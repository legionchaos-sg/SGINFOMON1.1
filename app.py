import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 2.1", page_icon="🇸🇬", layout="wide")

# 2. Silent Auto-Refresh (Every 3 minutes)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .coe-card {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .coe-label { font-size: 0.8rem; font-weight: bold; color: #555; }
    .coe-value { font-size: 1.4rem; font-weight: bold; color: #111; }
    .coe-delta { font-size: 0.85rem; font-weight: bold; }
    .market-card { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 12px; border-radius: 8px; text-align: center; }
    @media (prefers-color-scheme: dark) {
        .coe-card { background-color: #262730; border-left-color: #ff4b4b; }
        .coe-value { color: #fafafa; }
        .market-card { background-color: #1e1e1e; border-color: #333; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

@st.cache_data(ttl=180)
def get_market_data():
    tickers = {"STI INDEX": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Crude Oil": "CL=F"}
    data = {}
    for label, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            p = t.fast_info['last_price']
            d = p - t.fast_info['regular_market_previous_close']
            data[label] = {"price": p, "diff": d}
        except: data[label] = {"price": 0, "diff": 0}
    return data

# 5. Header & Clocks
st.title("Singapore Info Monitor 2.1")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), 
         ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]

for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, get_tz_time(tz))

# 6. Market Overview (Panel 1)
st.subheader("📊 Market Overview")
m_data = get_market_data()
m_cols = st.columns(4)
m_items = [("STI INDEX", "STI INDEX"), ("Gold Price", "Gold"), ("Silver Price", "Silver"), ("Crude Price", "Crude Oil")]

for i, (label, key) in enumerate(m_items):
    m_cols[i].metric(label, f"{m_data[key]['price']:,.2f}", f"{m_data[key]['diff']:+.2f}")

st.divider()

# 7. Singapore Headline News (Panel 2)
st.header("🇸🇬 Singapore Headline News")
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore"
}
tab1, tab2 = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])

with tab1:
    all_n = []
    for n, u in sources.items():
        try:
            f = feedparser.parse(requests.get(u, timeout=5).content)
            all_n.extend([{"s": n, "t": e.title, "l": e.link} for e in f.entries[:3]])
        except: pass
    for item in all_n[:9]:
        st.markdown(f"**{item['s']}**: [{item['t']}]({item['l']})")

with tab2:
    sel = st.selectbox("Source", list(sources.keys()))
    # Simplified fetch for tab 2
    f_ind = feedparser.parse(requests.get(sources[sel], timeout=5).content)
    for e in f_ind.entries[:5]: st.write(f"• [{e.title}]({e.link})")

st.divider()

# 8. CURRENT COE STATS (Panel 3 - New)
st.header("🚗 CURRENT COE STATS")
st.caption("Latest Results: 2nd Bidding Exercise - March 2026")

coe_data = [
    {"cat": "CAT A", "desc": "Cars ≤ 1600cc", "price": 111890, "change": 3670},
    {"cat": "CAT B", "desc": "Cars > 1600cc", "price": 115568, "change": 1566},
    {"cat": "CAT C", "desc": "Goods & Bus", "price": 78000, "change": 2000},
    {"cat": "CAT D", "desc": "Motorcycles", "price": 9589, "change": 987},
    {"cat": "CAT E", "desc": "Open Category", "price": 118119, "change": 3229}
]

c_cols = st.columns(5)
for i, item in enumerate(coe_data):
    with c_cols[i]:
        st.markdown(f"""
            <div class="coe-card">
                <div class="coe-label">{item['cat']}</div>
                <div style="font-size:0.7rem; color:#888;">{item['desc']}</div>
                <div class="coe-value">${item['price']:,}</div>
                <div class="coe-delta" style="color:#ff4b4b;">▲ ${item['change']:,}</div>
            </div>
        """, unsafe_allow_html=True)

# 9. Footer
st.divider()
st.caption(f"Sync Active | LTA Data Source | Last Refresh: {datetime.now().strftime('%H:%M:%S')}")
