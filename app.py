import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 3.8", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .time-card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center; }
    .time-city { font-size: 0.75rem; color: #ff4b4b; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #212529; }
    .status-card { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; font-size: 0.85rem; }
    .status-normal { background-color: #28a745; }
    .status-advisory { background-color: #ffc107; color: #212529; }
    .coe-card { background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 8px; margin-bottom: 10px; min-height: 160px; }
    .coe-price { font-size: 1.3rem; font-weight: bold; color: #d32f2f; margin-bottom: 0px; }
    .coe-diff { font-size: 0.85rem; font-weight: bold; margin-bottom: 8px; }
    .coe-meta { font-size: 0.75rem; color: #666; line-height: 1.2; }
    .diff-up { color: #d32f2f; }
    .diff-down { color: #28a745; }
    @media (prefers-color-scheme: dark) {
        .time-card, .coe-card { background-color: #262730; border-color: #444; }
        .time-value { color: #ffffff; }
        .coe-meta { color: #aaa; }
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
st.title("Singapore Info Monitor 3.8")

# Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div class="time-city">{city}</div><div class="time-value">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# News (Top)
st.header("🇸🇬 Singapore Headline News")
sources = {"Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Business Times": "https://www.businesstimes.com.sg/rss-feeds/singapore", "Mothership": "https://mothership.sg/feed/", "Shin Min": "https://www.zaobao.com.sg/rss/realtime/singapore"}
t_news1, t_news2 = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])
with t_news1:
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries: st.markdown(f"**{name}**: [{feed.entries[0].title}]({feed.entries[0].link})")
with t_news2:
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    feed = fetch_news(sources[sel])
    if feed and feed.entries:
        for e in feed.entries[:6]: st.write(f"• [{e.title}]({e.link})")

st.divider()

# Train Status
st.subheader("🚇 MRT/LRT Service Status")
train_lines = {"NSL": "Normal", "EWL": "Normal", "NEL": "Normal", "CCL": "Advisory", "DTL": "Normal", "TEL": "Normal"}
s_cols = st.columns(6)
for i, (line, status) in enumerate(train_lines.items()):
    bg = "status-normal" if status == "Normal" else "status-advisory"
    s_cols[i].markdown(f'<div class="status-card {bg}">{line}<br>{status}</div>', unsafe_allow_html=True)

st.write("")

# Market Dropdown List
with st.expander("📊 Market Info", expanded=True):
    m_tickers = {"STI Index": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Crude Oil": "CL=F"}
    m_data = get_financial_data(m_tickers)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", f"{m_data['STI Index']['p']:,.2f}", f"{m_data['STI Index']['change']:+.2f}")
    m2.metric("Gold", f"${m_data['Gold']['p']:,.2f}", f"{m_data['Gold']['change']:+.2f}")
    m3.metric("Silver", f"${m_data['Silver']['p']:,.2f}", f"{m_data['Silver']['change']:+.2f}")
    m4.metric("Crude Oil", f"${m_data['Crude Oil']['p']:,.2f}", f"{m_data['Crude Oil']['change']:+.2f}")

# Forex Dropdown List
with st.expander("💱 Forex Rates (Base: 1 SGD)", expanded=False):
    fx_tickers = {"MYR": "SGDMYR=X", "CNY": "SGDCNY=X", "THB": "SGDTHB=X", "JPY": "SGDJPY=X", "AUD": "SGDAUD=X"}
    fx_data = get_financial_data(fx_tickers)
    f_cols = st.columns(5)
    for i, (label, val) in enumerate(fx_data.items()):
        f_cols[i].metric(label, f"{val['p']:.4f}", f"{val['pc']:+.2f}%")

# COE Dropdown List with Comparison
with st.expander("🚗 COE Premium & Bidding Analysis", expanded=False):
    st.write("**Latest Bidding Results: March 2026 (2nd Exercise)**")
    # Data structure: (Category, Price, Change, Quota, Bids)
    coe_results = [
        ("Cat A", 111890, 3670, 1264, 1895),
        ("Cat B", 115568, 1566, 812, 1185),
        ("Cat C", 78000, 2000, 290, 438),
        ("Cat D", 9589, 987, 546, 726),
        ("Cat E", 118119, 3229, 246, 422)
    ]
    
    c_cols = st.columns(5)
    for i, (cat, price, diff, q, b) in enumerate(coe_results):
        with c_cols[i]:
            diff_sign = "▲" if diff > 0 else "▼"
            diff_class = "diff-up" if diff > 0 else "diff-down"
            ratio = b / q if q > 0 else 0
            
            st.markdown(f"""
                <div class="coe-card">
                    <div style="font-weight:bold; font-size:0.85rem; margin-bottom:4px;">{cat}</div>
                    <div class="coe-price">${price:,}</div>
                    <div class="coe-diff {diff_class}">{diff_sign} ${abs(diff):,}</div>
                    <div class="coe-meta">Quota: <b>{q}</b></div>
                    <div class="coe-meta">Bids: <b>{b}</b></div>
                    <div class="coe-meta" style="margin-top:5px; color:#ff4b4b;">Ratio: <b>{ratio:.2f}x</b></div>
                </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')} SGT")
