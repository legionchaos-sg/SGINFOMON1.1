import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config & Padding Reset
st.set_page_config(page_title="SG INFO MON 5.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=3 * 60 * 1000, key="global_refresh")

# Custom CSS to fix the top gap and style the cards
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
def get_tz_time(zone_name):
    return datetime.now(pytz.timezone(zone_name)).strftime("%H:%M")

def fetch_news(url):
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        feed = feedparser.parse(resp.content)
        return [{'title': e.title, 'link': e.link} for e in feed.entries[:8]]
    except: return []

# --- SECTION 1: REGIONAL TIME ---
st.title("🇸🇬 Singapore Info Monitor 5.9")
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), 
         ("Jakarta", "Asia/Jakarta"), ("Manila", "Asia/Manila"), ("Brisbane", "Australia/Brisbane")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{city}</div><div style="font-size:1.1rem;font-weight:bold;">{get_tz_time(tz)}</div></div>', unsafe_allow_html=True)

st.divider()

# --- SECTION 2: SINGAPORE HEADLINES ---
st.header("🗞️ Singapore Headlines")
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

tab_uni, tab_src = st.tabs(["📊 Unified Pool", "📰 Select Source"])

# Step A: Load Unified Pool
unified_data = []
with tab_uni:
    for name, url in news_sources.items():
        data = fetch_news(url)
        if data:
            item = data[0]
            unified_data.append({'name': name, 'title': item['title']})
            st.write(f"<span class='news-tag'>{name}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
    
    # Step B: Translation specifically for Unified Pool
    st.write("---")
    if st.checkbox("Translate Unified Pool to Chinese (简体中文)"):
        with st.status("Translating pool content...", expanded=False):
            for entry in unified_data:
                translated = GoogleTranslator(source='auto', target='zh-CN').translate(entry['title'])
                st.caption(f"🇨🇳 **{entry['name']}**: {translated}")

with tab_src:
    src_choice = st.selectbox("Choose News Outlet", list(news_sources.keys()))
    selected_news = fetch_news(news_sources[src_choice])
    for e in selected_news:
        st.write(f"• [{e['title']}]({e['link']})")

st.divider()

# --- SECTION 3: MARKET INFO ---
with st.expander("📊 Market Info", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    # March 23, 2026 Closing Data
    m1.metric("STI Index", "4,841.30", "-107.57 (-2.2%)")
    m2.metric("Gold (Spot)", "$4,282.40", "-4.82%")
    m3.metric("Silver (Spot)", "$63.47", "-6.11%")
    m4.metric("Brent Crude", "$112.91", "+0.64%")

# --- SECTION 4: FOREX RATES ---
with st.expander("💱 Forex Rates (1 SGD to X)", expanded=True):
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    f1.metric("CNY (Yuan)", "5.384", "+0.24%")
    f2.metric("THB (Baht)", "23.040", "-0.15%")
    f3.metric("JPY (Yen)", "111.28", "-0.80%")
    f4.metric("MYR (Ringgit)", "2.747", "-1.50%")
    f5.metric("AUD (Dollar)", "1.117", "+0.21%")
    f6.metric("USD (Dollar)", "0.773", "+0.05%")

# --- SECTION 5: COE BIDDING ---
with st.expander("🚗 COE Bidding - Mar 2026 2nd Round", expanded=True):
    coe_data = [
        ("Cat A", 111890, 3670, 1264, 1895),
        ("Cat B", 115568, 1566, 812, 1185),
        ("Cat C", 78000, 2000, 290, 438),
        ("Cat D", 9589, 987, 546, 726),
        ("Cat E", 118119, 3229, 246, 422)
    ]
    c_cols = st.columns(5)
    for i, (cat, price, diff, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f"""
            <div class="coe-card">
                <div style="font-weight:bold;font-size:0.8rem;">{cat}</div>
                <div style="color:#d32f2f;font-weight:bold;font-size:1.1rem;">${price:,}</div>
                <div style="color:#d32f2f;font-size:0.8rem;font-weight:bold;">▲ ${diff:,}</div>
                <div style="font-size:0.7rem;margin-top:5px;color:#666;">Quota: {q}<br>Bids: {b}</div>
            </div>
        """, unsafe_allow_html=True)

st.caption(f"Sync Success: {datetime.now().strftime('%H:%M:%S')} SGT | v5.9 Fixed")
