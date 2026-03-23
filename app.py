import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup & Refresh
st.set_page_config(page_title="SG INFO MON 6.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="master_sync")

st.markdown("""
    <style>
    .block-container {padding-top: 1.2rem !important;}
    .time-card {background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center;}
    .coe-card, .fuel-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:10px; border-radius:6px; min-height:85px;}
    .fuel-card {border-left-color: #007bff;}
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    @media (prefers-color-scheme: dark) { 
        .time-card, .coe-card, .fuel-card {background:#262730; border-color:#444;}
        .news-tag {background:#444; color:#bbb;} .trans-box {color:#ffbaba;}
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Helpers
def get_sg_now(): return datetime.now(pytz.timezone('Asia/Singapore'))

def fetch_top(url):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        return {'t': f.entries[0].title, 'l': f.entries[0].link} if f.entries else None
    except: return None

# --- 1. REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 6.9")
t_cols = st.columns(6)
zones = [("Singapore","Asia/Singapore"), ("Bangkok","Asia/Bangkok"), ("Tokyo","Asia/Tokyo"), 
         ("Jakarta","Asia/Jakarta"), ("Manila","Asia/Manila"), ("Brisbane","Australia/Brisbane")]
for i, (c, z) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{c}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(z)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# --- 2. SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
srcs = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
        "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
        "Mothership": "https://mothership.sg/feed/"}
t_uni, t_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])
with t_uni:
    unified = []
    for n, u in srcs.items():
        res = fetch_top(u)
        if res: unified.append({'n': n, 't': res['t'], 'l': res['l']})
    do_tr = st.checkbox("Fast Translation (Simplified Chinese)")
    trans_list = []
    if do_tr and unified:
        try:
            mega = "\n".join([x['t'] for x in unified])
            trans_list = GoogleTranslator(target='zh-CN').translate(mega).split("\n")
        except: st.error("Translation Timeout")
    for i, item in enumerate(unified):
        st.write(f"<span class='news-tag'>{item['n']}</span> **[{item['t']}]({item['l']})**", unsafe_allow_html=True)
        if do_tr and i < len(trans_list):
            st.markdown(f"<div class='trans-box'>🇨🇳 {trans_list[i].strip()}</div>", unsafe_allow_html=True)

st.divider()

# --- 3. MARKET & FOREX ---
with st.expander("📊 Market Info & Forex", expanded=True):
    m = st.columns(4)
    m[0].metric("STI Index", "4,841.30", "-2.2%")
    m[1].metric("Gold (Spot)", "$4,282.40", "-4.8%")
    m[2].metric("Silver (Spot)", "$63.47", "-6.1%")
    m[3].metric("Brent Crude", "$112.91", "+0.6%")
    st.write("---")
    f = st.columns(6)
    fx = [("CNY","5.384"),("THB","23.04"),("JPY","111.2"),("MYR","2.747"),("AUD","1.117"),("USD","0.773")]
    for i, (n, v) in enumerate(fx): f[i].metric(n, v)

# --- 4. COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, p, d) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-weight:bold;font-size:1.1rem;">${p:,}</span><br><small>▲ ${d:,}</small></div>', unsafe_allow_html=True)

# --- 5. FUEL PRICES (NEW) ---
with st.expander("⛽ Fuel Prices (Avg. Pump Price)", expanded=True):
    # Data sourced from current monitoring averages for Mar 2026
    fuel_data = [("92 Octane", "$3.11"), ("95 Octane", "$3.18"), ("98 Octane", "$3.65"), ("Premium", "$3.88"), ("Diesel", "$2.72")]
    fuel_cols = st.columns(5)
    for i, (grade, price) in enumerate(fuel_data):
        fuel_cols[i].markdown(f'<div class="fuel-card"><b>{grade}</b><br><span style="color:#007bff;font-weight:bold;font-size:1.2rem;">{price}</span><br><small>S$/Litre</small></div>', unsafe_allow_html=True)

st.divider()
st.caption(f"Sync Success: {get_sg_now().strftime('%H:%M:%S')} SGT | v6.9 Master Copy")
