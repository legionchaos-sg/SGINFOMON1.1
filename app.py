import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup
st.set_page_config(page_title="SG INFO MON 6.3", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180 * 1000, key="global_refresh")

st.markdown("""
    <style>
    .block-container {padding-top: 1.2rem !important;}
    .time-card {background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; border-radius: 8px; text-align: center;}
    .coe-card {background-color: #f8f9fa; border-left: 4px solid #ff4b4b; padding: 10px; border-radius: 6px; min-height: 120px;}
    .news-tag {font-size: 0.65rem; background: #eee; padding: 2px 4px; border-radius: 3px; color: #666; margin-right: 5px;}
    @media (prefers-color-scheme: dark) { .time-card, .coe-card {background-color: #262730; border-color: #444;} }
    </style>
    """, unsafe_allow_html=True)

# 2. Helpers
def get_sg_time(): return datetime.now(pytz.timezone('Asia/Singapore'))

def fetch_news(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        return [{'title': e.title, 'link': e.link} for e in feedparser.parse(resp.content).entries[:5]]
    except: return []

def translate_unified_fast(unified_list):
    if not unified_list: return ""
    # Combine titles with a safe delimiter
    combined_text = " ||| ".join([e['title'] for e in unified_list])
    try:
        translated_big_string = GoogleTranslator(source='auto', target='zh-CN').translate(combined_text)
        translations = translated_big_string.split(" ||| ")
        # Build the final string with proper markdown list indentation
        result = "\n"
        for i, text in enumerate(translations):
            result += f"- **{unified_list[i]['name']} (CN)**: {text}\n"
        return result
    except:
        return "\n- 翻译失败"

# --- SECTION 1: REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 6.3")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# --- SECTION 2: SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

tab_uni, tab_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])
unified_list = []

with tab_uni:
    # Build original content as a single markdown string to ensure zero-gap indentation
    original_md = ""
    for name, url in sources.items():
        data = fetch_news(url)
        if data:
            item = data[0]
            unified_list.append({'name': name, 'title': item['title']})
            original_md += f"- **{name}**: [{item['title']}]({item['link']})\n"
    
    st.markdown(original_md, unsafe_allow_html=True)
    
    st.write("---")
    # Batch Translation with matching indentation
    if st.checkbox("Fast Batch Translate Unified Pool (Simplified Chinese)"):
        with st.spinner("Batch translating..."):
            translated_md = translate_unified_fast(unified_list)
            st.markdown(translated_md)

with tab_src:
    src_choice = st.selectbox("Choose News Outlet", list(sources.keys()))
    for e in fetch_news(sources[src_choice]):
        st.write(f"• [{e['title']}]({e['link']})")

st.divider()

# --- SECTION 3: MARKET INFO ---
with st.expander("📊 Market Info", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,282.40", "-4.82%")
    m3.metric("Silver (Spot)", "$63.47", "-6.11%")
    m4.metric("Brent Crude", "$112.91", "+0.64%")

# --- SECTION 4: FOREX RATES ---
with st.expander("💱 Forex Rates", expanded=True):
    f_cols = st.columns(6)
    fx = [("CNY","5.384","+0.2%"),("THB","23.04","-0.1%"),("JPY","111.2","-0.8%"),
          ("MYR","2.747","-1.5%"),("AUD","1.117","+0.2%"),("USD","0.773","+0.0%")]
    for i, (n, v, c) in enumerate(fx): f_cols[i].metric(n, v, c)

# --- SECTION 5: COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), 
           ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-size:1.1rem;font-weight:bold;">${p:,}</span><br><small>▲ ${d:,}</small></div>', unsafe_allow_html=True)

st.divider()
st.caption(f"Sync Success: {get_sg_time().strftime('%H:%M:%S')} SGT | v6.3 Layout Fixed")
