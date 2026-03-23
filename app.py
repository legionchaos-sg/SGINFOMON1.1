import streamlit as st
import feedparser
import requests
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 8.2", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_82")

# 2. CSS Styling
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; }
    .t-card {background:#f8f9fa; border:1px solid #ddd; padding:8px; border-radius:8px; text-align:center; margin-bottom:5px;}
    .c-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:12px; border-radius:6px; margin-bottom:10px; min-height:175px;}
    .f-card {background:#f1f7ff; border:1px solid #007bff; padding:15px; border-radius:10px; text-align:center;}
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    .up {color: #d32f2f !important; font-weight: bold;} 
    .down {color: #28a745 !important; font-weight: bold;}
    .stat-label {font-size: 0.75rem; color: #666; text-transform: uppercase;}
    @media (prefers-color-scheme: dark) { .t-card, .c-card {background:#262730; border-color:#444;} .f-card {background:#1e2630;} }
    </style>
    """, unsafe_allow_html=True)

# 3. Fuel Pricing Logic
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.04), "Caltex": (3.43, 0.04), "SPC": (3.43, 0.00)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Sinopec": (3.47, 0.04)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "Caltex": (4.16, 0.08)},
    "Premium": {"Shell V-Power": (4.21, 0.05), "Sinopec X-Power": (4.10, 0.04)},
    "Diesel": {"Esso": (3.73, -0.04), "Shell": (3.73, -0.04), "SPC": (3.56, -0.06)}
}

@st.dialog("Fuel Brand Details")
def show_fuel(ftype):
    st.subheader(f"📍 {ftype} Breakdown")
    cols = st.columns(2)
    for i, (brand, (p, c)) in enumerate(fuel_data[ftype].items()):
        tr = f'<span class="{"up" if c>0 else "down"}">{"▲" if c>0 else "▼"} ${abs(c):.2f}</span>' if c!=0 else "Stable"
        cols[i%2].markdown(f'<div style="padding:10px; border-bottom:1px solid #ddd;"><b>{brand}</b><br><span style="color:#007bff; font-size:1.1rem;">${p:.2f}</span><br>{tr}</div>', unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 Singapore Info Monitor 8.2")

# 4. Country Clocks (Reverted to Country Names)
countries = [
    ("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), 
    ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), 
    ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")
]
t_cols = st.columns(6)
for i, (name, tz) in enumerate(countries):
    t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. Refined News Section (Unified Top 3)
st.header("🗞️ Singapore Headlines")
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/"
}

col_n1, col_n2 = st.columns([2, 1])
with col_n1:
    view_mode = st.radio("View Mode:", ["Unified (Top 3 per source)", "CNA Only", "Straits Times Only", "Mothership Only"], horizontal=True)
with col_n2:
    do_tr = st.checkbox("Translate (Chinese)")

news_list = []
if "Unified" in view_mode:
    for src, url in news_sources.items():
        try:
            feed = feedparser.parse(requests.get(url, timeout=5).content)
            # Take only the top 3 items from each source
            for entry in feed.entries[:3]:
                news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
        except: pass
else:
    src_key = view_mode.replace(" Only", "")
    try:
        feed = feedparser.parse(requests.get(news_sources[src_key], timeout=5).content)
        for entry in feed.entries[:10]:
            news_list.append({'src': src_key, 'title': entry.title, 'link': entry.link})
    except: pass

# Translation Logic
tr_list = []
if do_tr and news_list:
    try: tr_list = GoogleTranslator(target='zh-CN').translate("\n".join([x['title'] for x in news_list])).split("\n")
    except: pass

for i, item in enumerate(news_list):
    st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
    if do_tr and i < len(tr_list):
        st.markdown(f"<div class='trans-box'>🇨🇳 {tr_list[i].strip()}</div>", unsafe_allow_html=True)

st.divider()

# 6. Market Expanders
with st.expander("📈 Market Indices & Commodities", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,892.27", "-0.30%")
    m2.metric("Gold (Spot)", "$4,202.90", "-8.04%")
    m3.metric("Silver (Spot)", "$64.12", "-7.56%")
    m4.metric("Brent Crude", "$113.13", "+0.84%")

with st.expander("💱 Foreign Exchange (SGD Base)", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("USD/SGD", "1.3369", "+0.22%")
    f2.metric("CNY/SGD", "5.3975", "-0.07%")
    f3.metric("MYR/SGD", "3.4412", "+0.12%")
    f4.metric("JPY/SGD", "118.55", "-0.43%")
    f5.metric("THB/SGD", "26.85", "+0.15%")

# 7. COE Bidding Results
with st.expander("🚗 COE Bidding (Mar 2026 2nd Round)", expanded=True):
    coe_data = [
        ("Cat A", 111890, 3670, 1264, 1895, 133),
        ("Cat B", 115568, 1566, 812, 1185, -76),
        ("Cat C", 78000, 2000, 290, 438, -50),
        ("Cat D", 9589, 987, 546, 726, 83),
        ("Cat E", 118119, 3229, 246, 422, -92)
    ]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b, bd) in enumerate(coe_data):
        b_cls = "up" if bd > 0 else "down"
        b_sym = "▲" if bd > 0 else "▼"
        c_cols[i].markdown(f"""
            <div class="c-card">
                <b>{cat}</b><br>
                <span style="color:#d32f2f;font-size:1.1rem;font-weight:bold;">${p:,}</span><br>
                <small class="up">▲ ${d:,}</small>
                <hr style="margin:8px 0; opacity:0.1;">
                <span class="stat-label">Quota:</span> <b>{q:,}</b><br>
                <span class="stat-label">Bids:</span> <b>{b:,}</b><br>
                <small class="{b_cls}">{b_sym} {abs(bd)}</small>
            </div>
            """, unsafe_allow_html=True)

# 8. Fuel Prices
with st.expander("⛽ Fuel Prices", expanded=True):
    f_cols = st.columns(5)
    for i, ftype in enumerate(list(fuel_data.keys())):
        avg = sum([v[0] for v in fuel_data[ftype].values()]) / len(fuel_data[ftype])
        f_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if f_cols[i].button("Details", key=f"fbtn_{i}"):
            show_fuel(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
