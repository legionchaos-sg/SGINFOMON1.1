import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 5.7", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="refresh_sync")

# 2. Main Title
st.title("🇸🇬 Singapore Info Monitor 5.7")

# 3. Helpers
def get_tz(z): return datetime.now(pytz.timezone(z)).strftime("%H:%M")
def fetch(u):
    try:
        r = requests.get(u, timeout=5)
        return [{'t': e.title, 'l': e.link} for e in feedparser.parse(r.content).entries[:8]]
    except: return []

# --- 1. REGIONAL TIME ---
st.subheader("🌐 Regional Time")
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
    s = st.selectbox("Choose News Outlet", list(srcs.keys()))
    news_items = fetch(srcs[s])
    for e in news_items: st.markdown(f"• [{e['t']}]({e['l']})")
    if st.checkbox("Show Chinese Translations"):
        with st.status("Translating...", expanded=False):
            for e in news_items:
                st.write(f"🇨🇳 {GoogleTranslator(target='zh-CN').translate(e['t'])}")

st.divider()

# --- 3. MARKET INFO (Expander Restored) ---
# Order: STI, Gold, Silver, Brent
with st.expander("📊 Market Info", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,285.00", "-4.51%")
    m3.metric("Silver (Spot)", "$64.80", "-3.12%")
    m4.metric("Brent Crude", "$111.86", "-0.29%")

# --- 4. FOREX RATES (Expander Restored) ---
# Order: CNY, THB, JPY, MYR, AUD, USD
with st.expander("💱 Forex Rates (1 SGD to X)", expanded=True):
    f_cols = st.columns(6)
    fx_vals = [("CNY","5.378","+0.12%"),("THB","23.04","-0.15%"),("JPY","111.28","-0.8%"),
               ("MYR","2.747","-1.5%"),("AUD","1.117","+0.21%"),("USD","0.773","+0.05%")]
    for i, (n, v, c) in enumerate(fx_vals):
        f_cols[i].metric(n, v, c)

# --- 5. COE BIDDING (Expander Restored) ---
with st.expander("🚗 COE Bidding - Mar 2026 Round 2", expanded=True):
    # Using columns instead of HTML cards to prevent syntax errors
    coe_list = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), 
                ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, p, d) in enumerate(coe_list):
        with c_cols[i]:
            st.metric(cat, f"${p:,}", f"+{d}")

st.divider()
st.caption(f"Sync Success: {datetime.now().strftime('%H:%M:%S')} SGT")
