import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 8.8", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_88_final")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 10px; min-height: 175px; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); }
    .sentiment-val { font-size: 2rem; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 3. Restored Fuel Logic & Dialog
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.04), "Caltex": (3.43, 0.04), "SPC": (3.43, 0.00)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Sinopec": (3.47, 0.04)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "Caltex": (4.16, 0.08)},
    "Premium": {"Shell V-Power": (4.21, 0.05), "Sinopec X-Power": (4.10, 0.04)},
    "Diesel": {"Esso": (3.73, -0.04), "Shell": (3.73, -0.04), "SPC": (3.56, -0.06)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List")
    for brand, (price, change) in fuel_data[ftype].items():
        st.markdown(f"**{brand}**: ${price:.2f} ({'▲' if change > 0 else '▼'} ${abs(change):.2f})")

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 8.8")

# 4. Country Clocks
t_cols = st.columns(6)
for i, (name, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. News Section with NEW SEARCH BAR
st.header("🗞️ Singapore Headlines")
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/",
    "8world News": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
}

c1, c2, c3 = st.columns([1.5, 1, 1])
with c1:
    search_query = st.text_input("🔍 Search News Keywords:", placeholder="e.g. Grab, Housing, War")
with c2:
    view_mode = st.selectbox("Source:", ["Unified (All)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
with c3:
    do_tr = st.checkbox("Translate (English to Chinese)")

# Fetch news and filter by search query
news_list = []
for src, url in news_sources.items():
    if "Unified" in view_mode or src in view_mode:
        try:
            feed = feedparser.parse(requests.get(url, timeout=5).content)
            for entry in feed.entries[:10]:
                if search_query.lower() in entry.title.lower():
                    news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
        except: pass

# Display filtered news
for item in news_list[:15]:
    st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

st.divider()

# 6. Live Market & Forex (Updated for March 23, 2026)
with st.expander("📈 Market Indices (Mar 23, 2026)", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,912.45", "-2.10%")
    m2.metric("Gold (Spot)", "$5,774.20", "+0.45%")
    m3.metric("Silver (Spot)", "$87.10", "+1.20%")
    m4.metric("Brent Crude", "$113.34", "+1.02%")

with st.expander("💱 Foreign Exchange (SGD Base)", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("USD/SGD", "1.2756", "-0.50%")
    f2.metric("CNY/SGD", "0.1852", "-0.50%")
    f3.metric("MYR/SGD", "0.3246", "-0.23%")
    f4.metric("JPY/SGD", "0.0080", "-0.08%")
    f5.metric("THB/SGD", "0.0395", "+0.81%")

# 7. Restored Fuel Section with Dialogs
with st.expander("⛽ Fuel Prices", expanded=True):
    fuel_cols = st.columns(5)
    for i, ftype in enumerate(fuel_data.keys()):
        avg = sum([v[0] for v in fuel_data[ftype].values()]) / len(fuel_data[ftype])
        fuel_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><b>${avg:.2f}</b></div>', unsafe_allow_html=True)
        if fuel_cols[i].button("Details", key=f"btn_{i}"):
            show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
