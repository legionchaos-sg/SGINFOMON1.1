import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.1", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card {
        background-color: #f8f9fa; border: 1px solid #e9ecef;
        padding: 10px; border-radius: 8px; text-align: center;
    }
    .time-city { 
        font-size: 0.75rem; color: #ff4b4b; /* RED TEXT */
        font-weight: bold; text-transform: uppercase; margin-bottom: 2px;
    }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .forex-card {
        background-color: #ffffff; border: 1px solid #eee; 
        padding: 12px; border-radius: 8px; text-align: center;
    }
    .coe-card {
        background-color: #f8f9fa; border-top: 4px solid #ff4b4b;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
    .coe-value { font-size: 1.3rem; font-weight: bold; color: #d32f2f; }
    @media (prefers-color-scheme: dark) {
        .time-card, .forex-card, .coe-card { background-color: #262730; border-color: #333; }
        .time-value, .forex-price { color: #ffffff; }
        .coe-value { color: #ff5252; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
def get_tz_time(zone_name):
    try:
        return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")
    except: return "00:00"

@st.cache_data(ttl=180)
def get_financial_data(tickers_dict):
    results = {}
    for label, sym in tickers_dict.items():
        try:
            t = yf.Ticker(sym)
            p = t.fast_info['last_price']
            prev = t.fast_info['regular_market_previous_close']
            results[label] = {"p": p, "change": p - prev, "pc": ((p - prev) / prev) * 100}
        except: results[label] = {"p": 0.0, "change": 0.0, "pc": 0.0}
    return results

def fetch_feed(url):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        return [{"t": e.title, "l": e.link, "d": e.get('published', 'Recent')} for e in f.entries]
    except: return []

# 5. REGIONAL Current Time Panel
st.title("Singapore Info Monitor 1.1")
st.subheader("🌐 REGIONAL Current Time")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]

for i, (city, tz) in enumerate(zones):
    with t_cols[i]:
        st.markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

# 6. Market Overview
st.write("")
st.subheader("📊 Market Overview")
m_tickers = {"STI": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Crude": "CL=F"}
m_data = get_financial_data(m_tickers)
m_cols = st.columns(5)
market_items = [("STI INDEX", "STI"), ("Gold Price", "Gold"), ("Silver Price", "Silver"), ("Crude Price", "Crude")]

for i, (l, k) in enumerate(market_items):
    m_cols[i].metric(l, f"{m_data[k]['p']:,.2f}", f"{m_data[k]['change']:+.2f}")
m_cols[4].metric("SG Core Inflation", "1.40%", "+0.40%")

# 7. Forex Exchange Panel
st.write("")
st.subheader("💱 Forex Exchange (Base: 1 SGD)")
fx_tickers = {"CNY (China)": "SGDCNY=X", "MYR (Malaysia)": "SGDMYR=X", "THB (Thailand)": "SGDTHB=X", "JPY (Japan)": "SGDJPY=X", "AUD (Australia)": "SGDAUD=X"}
fx_data = get_financial_data(fx_tickers)
fx_cols = st.columns(5)

for i, label in enumerate(fx_tickers.keys()):
    val = fx_data[label]
    color = "#28a745" if val['change'] >= 0 else "#dc3545"
    arrow = "▲" if val['change'] >= 0 else "▼"
    with fx_cols[i]:
        st.markdown(f"""
            <div class="forex-card">
                <div class="forex-label">{label}</div>
                <div style="font-size:1.1rem; font-weight:bold;">{val['p']:.4f}</div>
                <div style="color:{color}; font-size:0.8rem; font-weight:bold;">{arrow} {abs(val['pc']):.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# 8. Singapore Headline News
st.header("🇸🇬 Singapore Headline News")
sources = {"The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"}
tab1, tab2 = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])

with tab1:
    all_news = []
    for name, url in sources.items():
        for item in fetch_feed(url)[:3]:
            all_news.append(f"**{name}**: [{item['t']}]({item['l']})")
    for news in all_news[:6]: st.markdown(news)

with tab2:
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    for item in fetch_feed(sources[sel])[:5]:
        st.markdown(f"#### [{item['t']}]({item['l']})")
        st.write("---")

st.divider()

# 9. CURRENT COE STATS
st.header("🚗 CURRENT COE STATS")
coe_results = [
    {"cat": "CAT A", "price": 111890, "quota": 1264, "bids": 1895},
    {"cat": "CAT B", "price": 115568, "quota": 812, "bids": 1185},
    {"cat": "CAT C", "price": 78000, "quota": 290, "bids": 438},
    {"cat": "CAT D", "price": 9589, "quota": 546, "bids": 726},
    {"cat": "CAT E", "price": 118119, "quota": 246, "bids": 422}
]
c_cols = st.columns(5)
for i, res in enumerate(coe_results):
    with c_cols[i]:
        st.markdown(f"""
            <div class="coe-card">
                <div style="font-weight:bold; font-size:0.85rem;">{res['cat']}</div>
                <div class="coe-value">${res['price']:,}</div>
                <div style="font-size:0.7rem; color:gray; margin-top:5px;">Quota: {res['quota']} | Bids: {res['bids']}</div>
            </div>
        """, unsafe_allow_html=True)

# 10. Footer
st.divider()
st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT | Stable Build 3.1")
