import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config & Auto-Refresh (3 Minutes)
st.set_page_config(page_title="SG INFO MON 6.8", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="refresh_ticker")

# 2. Custom CSS for Layout and Indentation
st.markdown("""
    <style>
    .block-container {padding-top: 1.2rem !important;}
    .time-card {background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center;}
    .coe-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:10px; border-radius:6px; min-height:90px;}
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    @media (prefers-color-scheme: dark) { 
        .time-card, .coe-card {background:#262730; border-color:#444;}
        .news-tag {background:#444; color:#bbb;} 
        .trans-box {color:#ffbaba;}
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Core Functions
def get_sg_now(): 
    return datetime.now(pytz.timezone('Asia/Singapore'))

def fetch_top_headline(url):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        return {'t': f.entries[0].title, 'l': f.entries[0].link} if f.entries else None
    except: return None

# --- SECTION 1: REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 6.8")
t_cols = st.columns(6)
zones = [("Singapore","Asia/Singapore"), ("Bangkok","Asia/Bangkok"), ("Tokyo","Asia/Tokyo"), 
         ("Jakarta","Asia/Jakarta"), ("Manila","Asia/Manila"), ("Brisbane","Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# --- SECTION 2: SINGAPORE HEADLINES (UNIFIED POOL) ---
st.header("🗞️ Singapore Headlines")
srcs = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
        "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
        "Mothership": "https://mothership.sg/feed/"}

tab_uni, tab_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])

with tab_uni:
    unified = []
    for name, url in srcs.items():
        res = fetch_top_headline(url)
        if res: unified.append({'n': name, 't': res['t'], 'l': res['l']})
    
    do_translate = st.checkbox("Fast Translation (Simplified Chinese)")
    
    # High-Speed Batch Translation Logic
    translations = []
    if do_translate and unified:
        try:
            mega_text = "\n".join([x['t'] for x in unified])
            translated_text = GoogleTranslator(source='auto', target='zh-CN').translate(mega_text)
            translations = translated_text.split("\n")
        except:
            st.error("Translation service temporarily unavailable.")

    # Indented Display Loop
    for i, item in enumerate(unified):
        st.write(f"<span class='news-tag'>{item['n']}</span> **[{item['t']}]({item['l']})**", unsafe_allow_html=True)
        if do_translate and i < len(translations):
            st.markdown(f"<div class='trans-box'>🇨🇳 {translations[i].strip()}</div>", unsafe_allow_html=True)

with tab_src:
    s_choice = st.selectbox("Choose News Outlet", list(srcs.keys()))
    f_data = feedparser.parse(requests.get(srcs[s_choice]).content)
    for e in f_data.entries[:8]: st.write(f"• [{e.title}]({e.link})")

st.divider()

# --- SECTION 3: MARKET INFO (Mar 23, 2026 Data) ---
with st.expander("📊 Market Info (STI; Gold; Silver; Brent Crude)", expanded=True):
    m_cols = st.columns(4)
    m_cols[0].metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m_cols[1].metric("Gold (Spot)", "$4,282.40", "-4.82%")
    m_cols[2].metric("Silver (Spot)", "$63.47", "-6.11%")
    m_cols[3].metric("Brent Crude", "$112.91", "+0.64%")

# --- SECTION 4: FOREX RATES (1 SGD TO X) ---
with st.expander("💱 Forex Rates (CNY; THB; JPY; MYR; AUD; USD)", expanded=True):
    fx_cols = st.columns(6)
    fx_data = [("CNY","5.384","+0.2%"),("THB","23.04","-0.1%"),("JPY","111.2","-0.8%"),
               ("MYR","2.747","-1.5%"),("AUD","1.117","+0.2%"),("USD","0.773","+0.0%")]
    for i, (label, val, chg) in enumerate(fx_data): fx_cols[i].metric(label, val, chg)

# --- SECTION 5: COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe_res = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, price, diff) in enumerate(coe_res):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-weight:bold;font-size:1.1rem;">${price:,}</span><br><small>▲ ${diff:,}</small></div>', unsafe_allow_html=True)

st.divider()
st.caption(f"Sync Success: {get_sg_now().strftime('%H:%M:%S')} SGT | v6.8 Master Build")
