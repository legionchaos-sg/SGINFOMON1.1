import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup
st.set_page_config(page_title="SG INFO MON 6.6", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180 * 1000, key="global_refresh")

st.markdown("""
    <style>
    .block-container {padding-top: 1.2rem !important;}
    .time-card {background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center;}
    .coe-card {background-color: #f8f9fa; border-left: 4px solid #ff4b4b; padding: 10px; border-radius: 6px; min-height: 120px;}
    .news-tag {font-size: 0.65rem; background: #eee; padding: 2px 4px; border-radius: 3px; color: #666; margin-right: 5px;}
    /* Adjusted translation styling for perfect vertical alignment */
    .trans-box {font-size: 0.85rem; color: #d32f2f; margin-left: 48px; margin-top: -8px; margin-bottom: 15px; font-style: italic;}
    @media (prefers-color-scheme: dark) { 
        .time-card, .coe-card {background-color: #262730; border-color: #444;}
        .news-tag {background: #444; color: #bbb;}
        .trans-box {color: #ffbaba;}
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Helpers
def get_sg_time(): return datetime.now(pytz.timezone('Asia/Singapore'))

def fetch_news(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        # Fetch top 1 from each source
        feed = feedparser.parse(resp.content)
        if feed.entries:
            return {'title': feed.entries[0].title, 'link': feed.entries[0].link}
        return None
    except: return None

def fast_batch_translate(titles):
    if not titles: return []
    mega_string = " ||| ".join(titles)
    try:
        # SINGLE API CALL for speed
        translated_mega = GoogleTranslator(source='auto', target='zh-CN').translate(mega_string)
        return translated_mega.split(" ||| ")
    except:
        return ["翻译暂时不可用"] * len(titles)

# --- 1. REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 6.6")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# --- 2. SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

tab_uni, tab_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])

with tab_uni:
    unified_data = []
    # 1. Fetch current top headlines
    for name, url in sources.items():
        entry = fetch_news(url)
        if entry:
            unified_data.append({'name': name, 'title': entry['title'], 'link': entry['link']})
    
    do_trans = st.checkbox("Enable Fast Translation (Unified Pool Only)")
    
    # 2. Batch Translate BEFORE the loop
    translated_list = []
    if do_trans and unified_data:
        titles_to_trans = [item['title'] for item in unified_data]
        translated_list = fast_batch_translate(titles_to_trans)

    # 3. DISPLAY LOOP: One headline + One translation per iteration
    for i, item in enumerate(unified_data):
        # Display Original
        st.write(f"<span class='news-tag'>{item['name']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
        
        # Display Translation immediately after if enabled
        if do_trans and i < len(translated_list):
            st.markdown(f"<div class='trans-box'>🇨🇳 {translated_list[i]}</div>", unsafe_allow_html=True)

with tab_src:
    src_choice = st.selectbox("Choose News Outlet", list(sources.keys()))
    resp = requests.get(sources[src_choice], timeout=5)
    feed = feedparser.parse(resp.content)
    for e in feed.entries[:8]:
        st.write(f"• [{e.title}]({e.link})")

st.divider()

# --- 3. MARKET INFO ---
with st.expander("📊 Market Info (STI; Gold; Silver; Brent Crude)", expanded=True):
    m_cols = st.columns(4)
    m_cols[0].metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m_cols[1].metric("Gold (Spot)", "$4,282.40", "-4.82%")
    m_cols[2].metric("Silver (Spot)", "$63.47", "-6.11%")
    m_cols[3].metric("Brent Crude", "$112.91", "+0.64%")

# --- 4. FOREX RATES ---
with st.expander("💱 Forex Rates (CNY; THB; JPY; MYR; AUD; USD)", expanded=True):
    f_cols = st.columns(6)
    fx = [("CNY","5.384","+0.2%"),("THB","23.04","-0.1%"),("JPY","111.2","-0.8%"),
          ("MYR","2.747","-1.5%"),("AUD","1.117","+0.2%"),("USD","0.773","+0.0%")]
    for i, (n, v, c) in enumerate(fx): f_cols[i].metric(n, v, c)

# --- 5. COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, p, d) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-size:1.1rem;font-weight:bold;">${p:,}</span><br><small>▲ ${d:,}</small></div>', unsafe_allow_html=True)

st.divider()
st.caption(f"Sync Success: {get_sg_time().strftime('%H:%M:%S')} SGT | v6.6 Layout Fixed
