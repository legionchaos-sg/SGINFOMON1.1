import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_v10")

# 2. Adaptive CSS (Tightened Spacing & Compact Fonts)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; padding-top: 1rem; color: var(--text-color); }
    hr { margin: 0.5rem 0 !important; }
    .stHeader { margin-bottom: 0.4rem !important; }
    
    /* Reduced row spacing for clocks and COE */
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 4px; border-radius: 8px; text-align: center; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 8px; border-radius: 6px; margin-bottom: 2px; min-height: 155px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); }
    
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 5px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.8rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.8rem; }
    .stat-label { font-size: 0.7rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    
    .holiday-banner { padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 10px; font-weight: bold; color: white; background: linear-gradient(90deg, #28a745, #55efc4); }
    
    /* Compact Metric Text (-3 font size) */
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
    div[data-testid="stExpander"] [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Definitions
brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

# 4. Dialogue Pop-up for Fuel
@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List & Changes")
    for brand in brand_order:
        if brand in fuel_data[ftype]:
            price, change = fuel_data[ftype][brand]
            c_style = "up" if change > 0 else "down"
            c_str = f"({'+' if change > 0 else ''}{change:.2f})" if change != 0 else ""
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff;'>${price:.2f}</b> <small class='{c_style}'>{c_str}</small></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.0")

# 5. Regional Clocks
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 6. Holiday Banner
st.markdown(f'<div class="holiday-banner">🗓️ Next Holiday: Good Friday (Apr 3) — Long Weekend! 🏖️ — ⏳ 11 Days to go!</div>', unsafe_allow_html=True)

# 7. Headlines (Restored News Syntax)
st.header("🗞️ Singapore Headlines")
c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍 Search Keywords:", placeholder="Enter topic...")
with c2: v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])

news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/",
    "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
}

news_list = []
for src, url in news_sources.items():
    if "Unified" in v_mode or src in v_mode:
        try:
            feed = feedparser.parse(requests.get(url, timeout=5).content)
            limit = 1 if "Unified" in v_mode else 10
            for entry in feed.entries[:limit]:
                if not search_q or search_q.lower() in entry.title.lower():
                    news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
        except: pass

for item in news_list:
    st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

st.divider()

# 8. Markets & Forex
with st.expander("📈 Market Indices | Sentiment: :orange[⚖️ CAUTIOUS]", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-2.20%")
    m2.metric("Gold (Spot)", "$4,202.90", "-8.04%")
    m3.metric("Brent Crude", "$113.34", "+1.02%")
    m4.metric("Silver (Spot)", "$64.12", "-7.56%")

with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    f_cols = st.columns(5)
    f_cols[0].metric("SGD/MYR", "3.4412", "+0.12%")
    f_cols[1].metric("SGD/JPY", "118.55", "-0.43%")
    f_cols[2].metric("SGD/THB", "26.85", "+0.15%")
    f_cols[3].metric("SGD/CNY", "5.3975", "-0.07%")
    f_cols[4].metric("SGD/USD", "0.7480", "-0.22%")

# 9. COE Bidding
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:4px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>""", unsafe_allow_html=True)

# 10. Fuel Prices (RESTORED)
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    fuel_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
        avg = sum(prices) / len(prices) if prices else 0
        fuel_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if fuel_cols[i].button("Details", key=f"fuel_btn_{i}"):
            show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
