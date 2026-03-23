import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.2", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (Every 3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .status-card { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px; }
    .status-normal { background-color: #28a745; }
    .status-advisory { background-color: #ffc107; color: #212529; }
    .coe-card { background-color: #f8f9fa; border-top: 4px solid #ff4b4b; padding: 12px; border-radius: 8px; text-align: center; }
    @media (prefers-color-scheme: dark) {
        .time-card, .coe-card { background-color: #262730; border-color: #333; }
        .time-value { color: #ffffff; }
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Helper Functions
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

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

def fetch_news(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=5, headers=headers)
        return feedparser.parse(response.content)
    except: return None

# --- UI START ---
st.title("Singapore Info Monitor 3.2")

# 5. CLOCKS
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_time = get_tz_time(tz)
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{t_time}</div></div>', unsafe_allow_html=True)

st.divider()

# 6. TRAIN STATUS (March 2026 Updates)
st.subheader("🚇 MRT/LRT Service Status")
train_lines = {"NSL": "Normal", "EWL": "Normal", "NEL": "Normal", "CCL": "Advisory", "DTL": "Normal", "TEL": "Normal"}
s_cols = st.columns(6)
for i, (line, status) in enumerate(train_lines.items()):
    bg = "status-normal" if status == "Normal" else "status-advisory"
    s_cols[i].markdown(f'<div class="status-card {bg}">{line}<br>{status}</div>', unsafe_allow_html=True)
st.caption("⚠️ **CCL Advisory**: Scheduled tunnel strengthening works between Mountbatten and Paya Lebar.")

# 7. MARKETS & COE (March 2026 Data)
with st.expander("📊 Markets & COE Prices", expanded=True):
    # COE Section
    st.write("**Current COE Premiums (March 2nd Bidding)**")
    c_cols = st.columns(5)
    coe = {"Cat A": 111890, "Cat B": 115568, "Cat C": 78000, "Cat D": 9589, "Cat E": 118119}
    for i, (cat, price) in enumerate(coe.items()):
        c_cols[i].markdown(f'<div class="coe-card"><div style="font-size:0.7rem;">{cat}</div><div style="font-size:1.1rem; font-weight:bold; color:#d32f2f;">${price:,}</div></div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Financial Section
    m_tickers = {"Gold": "GC=F", "Crude": "CL=F", "STI": "^STI"}
    m_data = get_financial_data(m_tickers)
    m1, m2, m3 = st.columns(3)
    m1.metric("Gold Price", f"${m_data['Gold']['p']:,.2f}", f"{m_data['Gold']['change']:+.2f}")
    m2.metric("Crude Oil", f"${m_data['Crude']['p']:,.2f}", f"{m_data['Crude']['change']:+.2f}")
    m3.metric("STI INDEX", f"{m_data['STI']['p']:,.2f}", f"{m_data['STI']['change']:+.2f}")

# 8. NEWS
st.header("🇸🇬 Singapore Headline News")
sources = {"Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"}
tab1, tab2 = st.tabs(["📊 Unified", "📰 Sources"])
with tab1:
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries:
            st.write(f"**{name}**: [{feed.entries[0].title}]({feed.entries[0].link})")

st.divider()
st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')} SGT")
