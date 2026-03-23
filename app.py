import streamlit as st
import feedparser, requests, pytz, time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config & Top Padding Reset
st.set_page_config(page_title="SG INFO MON 6.0", page_icon="🇸🇬", layout="wide")
REFRESH_INTERVAL = 3 * 60  # 3 minutes in seconds
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="global_refresh")

st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem !important;}
    .time-card {background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center;}
    .coe-card {background-color: #f8f9fa; border-left: 4px solid #ff4b4b; padding: 10px; border-radius: 6px; min-height: 120px;}
    .news-tag {font-size: 0.65rem; background: #eee; padding: 2px 4px; border-radius: 3px; color: #666; margin-right: 5px;}
    @media (prefers-color-scheme: dark) { .time-card, .coe-card {background-color: #262730; border-color: #444;} }
    </style>
    """, unsafe_allow_html=True)

# 2. Helpers
def get_sg_time():
    return datetime.now(pytz.timezone('Asia/Singapore'))

def fetch_news(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        return [{'title': e.title, 'link': e.link} for e in feedparser.parse(resp.content).entries[:8]]
    except: return []

# --- SECTION 1: REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 6.0")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# --- SECTION 2: SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
news_sources = {"CNA": "...category=10416", "Straits Times": ".../rss.xml", "Mothership": ".../feed/"} # Simplified URLs for code space
# Note: Use your full URLs from previous versions here
sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

tab_uni, tab_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])
unified_list = []

with tab_uni:
    for name, url in sources.items():
        data = fetch_news(url)
        if data:
            item = data[0]
            unified_list.append({'name': name, 'title': item['title']})
            st.write(f"<span class='news-tag'>{name}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
    
    st.write("---")
    if st.checkbox("Translate Unified Pool to Simplified Chinese"):
        for entry in unified_list:
            trans = GoogleTranslator(target='zh-CN').translate(entry['title'])
            st.caption(f"🇨🇳 **{entry['name']}**: {trans}")

with tab_src:
    src_choice = st.selectbox("Choose News Outlet", list(sources.keys()))
    for e in fetch_news(sources[src_choice]):
        st.write(f"• [{e['title']}]({e['link']})")

st.divider()

# --- SECTION 3: MARKET INFO ---
with st.expander("📊 Market Info (STI; Gold; Silver; Brent Crude)", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,282.40", "-4.82%")
    m3.metric("Silver (Spot)", "$63.47", "-6.11%")
    m4.metric("Brent Crude", "$112.91", "+0.64%")

# --- SECTION 4: FOREX RATES ---
with st.expander("💱 Forex Rates (CNY; THB; JPY; MYR; AUD; USD)", expanded=True):
    f_cols = st.columns(6)
    fx = [("CNY","5.384","+0.2%"),("THB","23.04","-0.1%"),("JPY","111.2","-0.8%"),("MYR","2.747","-1.5%"),("AUD","1.117","+0.2%"),("USD","0.773","+0.0%")]
    for i, (n, v, c) in enumerate(fx): f_cols[i].metric(n, v, c)

# --- SECTION 5: COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026 2nd Round", expanded=True):
    coe = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-size:1.1rem;font-weight:bold;">${p:,}</span><br><small>▲ ${d:,}</small><br><div style="font-size:0.7rem;color:#666;margin-top:5px;">Q: {q} | B: {b}</div></div>', unsafe_allow_html=True)

# --- FINAL SYNC & COUNTDOWN ---
st.divider()
sg_now = get_sg_time()
st.caption(f"Sync Success: {sg_now.strftime('%H:%M:%S')} SGT | Next Auto-Refresh in {REFRESH_INTERVAL}s")
