import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup & Padding Fix
st.set_page_config(page_title="SG INFO MON 5.8", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="refresh_sync")

# This CSS removes the huge top gap (padding-top) and hides the header
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stMetric {background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #eee;}
        @media (prefers-color-scheme: dark) {
            .stMetric {background-color: #262730; border-color: #444;}
        }
    </style>
    """, unsafe_allow_html=True)

# 2. Helpers
def get_tz(z): return datetime.now(pytz.timezone(z)).strftime("%H:%M")
def fetch(u):
    try:
        r = requests.get(u, timeout=5)
        return [{'t': e.title, 'l': e.link} for e in feedparser.parse(r.content).entries[:8]]
    except: return []

# --- 1. REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 5.8")
t_cols = st.columns(6)
zones = [("Singapore","Asia/Singapore"),("Bangkok","Asia/Bangkok"),("Tokyo","Asia/Tokyo"),
         ("Jakarta","Asia/Jakarta"),("Manila","Asia/Manila"),("Brisbane","Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    with t_cols[i]:
        st.caption(city)
        st.subheader(get_tz(tz))

st.divider()

# --- 2. SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
srcs = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", 
        "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", 
        "Mothership": "https://mothership.sg/feed/"}
t1, t2 = st.tabs(["📊 Unified Pool", "📰 Select Source"])

with t1:
    for n, u in srcs.items():
        d = fetch(u)
        if d: st.markdown(f"**{n}**: [{d[0]['t']}]({d[0]['l']})")

with t2:
    s = st.selectbox("Choose Outlet", list(srcs.keys()))
    news_items = fetch(srcs[s])
    for e in news_items: st.markdown(f"• [{e['t']}]({e['l']})")
    if st.checkbox("Show Chinese Translations"):
        for e in news_items:
            st.write(f"🇨🇳 {GoogleTranslator(target='zh-CN').translate(e['t'])}")

st.divider()

# --- 3. MARKET INFO (Ordered: STI, Gold, Silver, Brent) ---
with st.expander("📊 Market Info", expanded=True):
    m_cols = st.columns(4)
    # Mar 23, 2026 Data
    m_cols[0].metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m_cols[1].metric("Gold (Spot)", "$4,285.00", "-4.51%")
    m_cols[2].metric("Silver (Spot)", "$64.80", "-3.12%")
    m_cols[3].metric("Brent Crude", "$111.86", "-0.29%")

# --- 4. FOREX RATES (Ordered: CNY, THB, JPY, MYR, AUD, USD) ---
with st.expander("💱 Forex Rates (1 SGD to X)", expanded=True):
    f_cols = st.columns(6)
    fx = [("CNY","5.378","+0.12%"),("THB","23.04","-0.15%"),("JPY","111.28","-0.8%"),
          ("MYR","2.747","-1.5%"),("AUD","1.117","+0.21%"),("USD","0.773","+0.05%")]
    for i, (n, v, c) in enumerate(fx):
        f_cols[i].metric(n, v, c)

# --- 5. COE BIDDING (Full Data) ---
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), 
           ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, p, d) in enumerate(coe):
        c_cols[i].metric(cat, f"${p:,}", f"+{d}")

st.divider()
st.caption(f"Refreshed: {datetime.now().strftime('%H:%M:%S')} SGT")
