import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup
st.set_page_config(page_title="SG INFO MON 5.6", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="refresh_sync")

# 2. Appearance
st.markdown("""<style>
    .time-card {background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center;}
    .coe-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:10px; border-radius:6px;}
    @media(prefers-color-scheme:dark){.time-card,.coe-card{background:#262730; border-color:#444;}}
</style>""", unsafe_allow_html=True)

# 3. Functional Logic
def get_tz(z): return datetime.now(pytz.timezone(z)).strftime("%H:%M")
def fetch(u):
    try:
        r = requests.get(u, timeout=5)
        return [{'t': e.title, 'l': e.link} for e in feedparser.parse(r.content).entries[:8]]
    except: return []

# --- 1. REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 5.6")
t_cols = st.columns(6)
zones = [("Singapore","Asia/Singapore"),("Bangkok","Asia/Bangkok"),("Tokyo","Asia/Tokyo"),
         ("Jakarta","Asia/Jakarta"),("Manila","Asia/Manila"),("Brisbane","Australia/Brisbane")]
for i, (c, z) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{c}</div><div style="font-size:1.1rem;font-weight:bold;">{get_tz(z)}</div></div>', unsafe_allow_html=True)

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
        if d: st.write(f"**{n}**: [{d[0]['t']}]({d[0]['l']})")

with t2:
    s = st.selectbox("Choose Outlet", list(srcs.keys()))
    news_items = fetch(srcs[s])
    for e in news_items: st.write(f"• [{e['t']}]({e['l']})")
    st.write("---")
    if st.button("Translate Selected News to Chinese"):
        with st.spinner("Translating..."):
            for e in news_items:
                st.caption(f"🇨🇳 {GoogleTranslator(target='zh-CN').translate(e['t'])}")

st.divider()

# --- 3. MARKET INFO (STI; Gold; Silver; Brent Crude) ---
with st.expander("📊 Market Info", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,239.09", "-5.56%")
    m3.metric("Silver (Spot)", "$63.43", "-6.16%")
    m4.metric("Brent Crude", "$113.36", "+1.04%")

# --- 4. FOREX RATES (CNY; THB; JPY; MYR; AUD; USD) ---
with st.expander("💱 Forex Rates (1 SGD to X)", expanded=True):
    f_cols = st.columns(6)
    fx = [("CNY","5.381","+0.18%"),("THB","25.435","-0.26%"),("JPY","124.22","+0.01%"),
          ("MYR","3.071","+0.17%"),("AUD","1.119","+0.60%"),("USD","0.781","+0.19%")]
    for i, (n, v, c) in enumerate(fx): f_cols[i].metric(n, v, c)

# --- 5. COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), 
           ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-size:1.1rem;font-weight:bold;">${p:,}</span><br><small>
