import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration & Meta
st.set_page_config(page_title="SG INFO MON 10.3", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_v103")

# 2. Ultra-Compact CSS (Shifted up 6 rows)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; padding-top: 0rem !important; margin-top: -25px; color: var(--text-color); }
    header { visibility: hidden; height: 0px; }
    hr { margin: 0.3rem 0 !important; }
    .stHeader { margin-bottom: 0.2rem !important; margin-top: 0.2rem !important; }
    
    /* Card Tightness */
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 2px; border-radius: 6px; text-align: center; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 5px; border-radius: 6px; min-height: 135px; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 6px; border-radius: 8px; text-align: center; }
    
    /* News Styling */
    .news-tag { font-size: 0.6rem; background: var(--secondary-background-color); padding: 1px 4px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 5px; border-radius: 3px; }
    .news-link { text-decoration: none; color: inherit; font-size: 0.9rem; }
    
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.75rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.75rem; }
    .next-h { color: #28a745; font-size: 0.85rem; font-weight: normal; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Holiday & News Logic
def get_next_holiday():
    now = datetime.now(pytz.timezone('Asia/Singapore'))
    h_date = datetime(2026, 4, 3, tzinfo=pytz.timezone('Asia/Singapore'))
    days_left = (h_date - now).days + 1
    return f"Next: Good Friday (Apr 3) — ⏳ {days_left} days"

@st.cache_data(ttl=600)
def fetch_sg_news(source_name, url, query, limit=10):
    try:
        resp = requests.get(url, timeout=5)
        feed = feedparser.parse(resp.content)
        results = []
        for entry in feed.entries:
            if not query or query.lower() in entry.title.lower():
                results.append({'src': source_name, 'title': entry.title, 'link': entry.link})
            if len(results) >= limit: break
        return results
    except: return []

# 4. Fuel Data & Dialog
brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

@st.dialog("Fuel Details")
def show_fuel(ftype):
    for b in brand_order:
        if b in fuel_data[ftype]:
            p, c = fuel_data[ftype][b]
            st.markdown(f"**{b}**: `${p:.2f}` <small class='{'up' if c>0 else 'down'}'>({c:+.2f})</small>", unsafe_allow_html=True)

# --- UI START ---
# Row 1: Clocks
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# Row 2: Headlines (Restored Syntax)
h_text = get_next_holiday()
st.markdown(f'### 🗞️ Headlines <span class="next-h">{h_text}</span>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍", placeholder="Search news...", label_visibility="collapsed")
with c2: v_mode = st.selectbox("Src", ["Unified", "CNA Only", "ST Only", "Mothership", "8world"], label_visibility="collapsed")

news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "ST": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/",
    "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
}

all_headlines = []
if v_mode == "Unified":
    for name, url in news_sources.items():
        all_headlines.extend(fetch_sg_news(name, url, search_q, limit=1))
else:
    src_key = v_mode.replace(" Only", "")
    all_headlines = fetch_sg_news(src_key, news_sources[src_key], search_q, limit=12)

for news in all_headlines:
    st.markdown(f"<span class='news-tag'>{news['src']}</span> <a class='news-link' href='{news['link']}'>{news['title']}</a>", unsafe_allow_html=True)

st.divider()

# Row 3 & 4: Markets, Forex, COE & Fuel
m_exp = st.expander("📈 Markets & Forex", expanded=True)
with m_exp:
    c_m = st.columns(4)
    c_m[0].metric("STI Index", "4,841.30", "-2.20%")
    c_m[1].metric("Gold Spot", "$4,202.90", "-8.04%")
    c_m[2].metric("SGD/MYR", "3.4412", "+0.12%")
    c_m[3].metric("SGD/USD", "0.7480", "-0.22%")

with st.expander("🚗 COE Bidding (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_coe = st.columns(5)
    for i, (cat, p, d) in enumerate(coe_data):
        c_coe[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>', unsafe_allow_html=True)

with st.expander("⛽ Fuel Prices", expanded=True):
    f_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
        avg = sum(prices) / len(prices) if prices else 0
        f_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><b>${avg:.2f}</b></div>', unsafe_allow_html=True)
        if f_cols[i].button("Details", key=f"f_{i}"): show_fuel(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')}")
