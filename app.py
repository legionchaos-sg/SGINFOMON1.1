import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.4", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_v104")

# 2. Ultra-Compact CSS (Content Reverted & Shifting 6-rows worth of space)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; padding-top: 0rem !important; margin-top: -30px; color: var(--text-color); }
    header { visibility: hidden; height: 0px; } 
    hr { margin: 0.3rem 0 !important; }
    .stHeader { margin-bottom: 0.2rem !important; margin-top: 0.1rem !important; }
    
    /* Card Styles */
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 2px; border-radius: 6px; text-align: center; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 5px; border-radius: 6px; min-height: 130px; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 6px; border-radius: 8px; text-align: center; }
    
    /* News Logic Restored Syntax */
    .news-tag { font-size: 0.6rem; background: var(--secondary-background-color); padding: 1px 4px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 5px; border-radius: 3px; }
    .news-link { text-decoration: none; color: inherit; font-size: 0.88rem; line-height: 1.2; }
    
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.75rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.75rem; }
    .next-h { color: #28a745; font-size: 0.85rem; font-weight: normal; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Dynamic Holiday & News Functions
def get_next_holiday():
    now = datetime.now(pytz.timezone('Asia/Singapore'))
    h_date = datetime(2026, 4, 3, tzinfo=pytz.timezone('Asia/Singapore'))
    days_left = (h_date - now).days + 1
    return f"Next: Good Friday (Apr 3) — ⏳ {days_left} days"

@st.cache_data(ttl=600)
def fetch_news(source, url, query, limit=10):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        res = []
        for e in f.entries:
            if not query or query.lower() in e.title.lower():
                res.append({'src': source, 'title': e.title, 'link': e.link})
            if len(res) >= limit: break
        return res
    except: return []

# --- DATA ---
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

# --- UI START ---
# ROW 1: CLOCKS
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# ROW 2: HEADLINES
h_text = get_next_holiday()
st.markdown(f'### 🗞️ Headlines <span class="next-h">{h_text}</span>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
with c1: q = st.text_input("🔍", placeholder="Search...", label_visibility="collapsed")
with c2: v = st.selectbox("Src", ["Unified", "CNA Only", "ST Only", "Mothership", "8world"], label_visibility="collapsed")

sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "ST": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/",
    "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
}

headlines = []
if v == "Unified":
    for s, url in sources.items(): headlines.extend(fetch_news(s, url, q, 1))
else:
    sk = v.replace(" Only", ""); headlines = fetch_news(sk, sources[sk], q, 10)

for h in headlines:
    st.markdown(f"<span class='news-tag'>{h['src']}</span> <a class='news-link' href='{h['link']}'>{h['title']}</a>", unsafe_allow_html=True)

st.divider()

# ROW 3: MARKETS (SEGREGATED)
with st.expander("📈 Market Indices", expanded=True):
    m_c = st.columns(4)
    m_c[0].metric("STI Index", "4,836.39", "-2.27%")
    m_c[1].metric("Gold Spot", "$4,410.90", "-3.49%")
    m_c[2].metric("Brent Crude", "$104.35", "-6.99%")
    m_c[3].metric("Silver Spot", "$68.04", "-1.91%")

# ROW 4: FOREX (SEGREGATED & REVERTED)
with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    fx_c = st.columns(5)
    fx_c[0].metric("SGD/MYR", "3.0717", "-0.31%")
    fx_c[1].metric("SGD/USD", "0.7480", "-0.22%")
    fx_c[2].metric("SGD/THB", "26.850", "+0.15%")
    fx_c[3].metric("SGD/JPY", "118.55", "-0.43%")
    fx_c[4].metric("SGD/CNY", "5.3975", "-0.07%")

# ROW 5: COE
with st.expander("🚗 COE Bidding (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    coe_c = st.columns(5)
    for i, (cat, p, d) in enumerate(coe_data):
        coe_c[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>', unsafe_allow_html=True)

# ROW 6: FUEL
with st.expander("⛽ Fuel Prices", expanded=True):
    f_c = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ft in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ft].values()]
        avg = sum(prices)/len(prices)
        f_c[i].markdown(f'<div class="f-card"><b>{ft}</b><br><b>${avg:.2f}</b></div>', unsafe_allow_html=True)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')}")
