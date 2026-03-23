import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 9.8", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_98_holiday")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 10px; min-height: 195px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; color: var(--text-color); }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    
    /* Dynamic Holiday Banner Colors */
    .holiday-banner { padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: bold; color: white; }
    .banner-red { background: linear-gradient(90deg, #ff4b4b, #ff7675); }
    .banner-green { background: linear-gradient(90deg, #28a745, #55efc4); border: 1px solid #1e7e34; }
    
    /* Compact Metric Text (-3 font size) */
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
    div[data-testid="stExpander"] [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Holiday Countdown Logic
def get_holiday_info():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz)
    # 2026 Holiday List
    holidays = [
        ("Good Friday", datetime(2026, 4, 3, tzinfo=sg_tz), True),
        ("Labour Day", datetime(2026, 5, 1, tzinfo=sg_tz), True),
        ("Vesak Day", datetime(2026, 5, 31, tzinfo=sg_tz), True),
        ("Hari Raya Haji", datetime(2026, 5, 27, tzinfo=sg_tz), False),
        ("National Day", datetime(2026, 8, 9, tzinfo=sg_tz), True)
    ]
    # Find the next one
    for name, date, is_long in holidays:
        if date > now:
            days = (date - now).days
            return name, days, is_long
    return "Next Holiday", 0, False

# 4. News Fetching Logic
def fetch_news(source, url, query, unified=False):
    try:
        feed = feedparser.parse(requests.get(url, timeout=5).content)
        limit = 1 if unified else 10
        results = []
        for entry in feed.entries[:limit]:
            if not query or query.lower() in entry.title.lower():
                results.append({'src': source, 'title': entry.title, 'link': entry.link})
        return results
    except: return []

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 9.8")

# 5. Clocks
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 6. Holiday Banner (Dynamic Color)
h_name, h_days, is_long_weekend = get_holiday_info()
banner_class = "banner-green" if is_long_weekend else "banner-red"
long_txt = " (Long Weekend! 🏖️)" if is_long_weekend else ""
st.markdown(f'<div class="holiday-banner {banner_class}">🗓️ Next Holiday: {h_name}{long_txt} — ⏳ {h_days} Days to go!</div>', unsafe_allow_html=True)

# 7. News Section
st.header("🗞️ Singapore Headlines")
c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍 Search Headlines:", placeholder="Filter by keywords...")
with c2: v_mode = st.selectbox("News Source:", ["Unified (Top Headlines)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])

sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Mothership": "https://mothership.sg/feed/",
    "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
}

all_news = []
if "Unified" in v_mode:
    for s_name, s_url in sources.items():
        all_news.extend(fetch_news(s_name, s_url, search_q, unified=True))
else:
    target = v_mode.replace(" Only", "")
    all_news = fetch_news(target, sources[target], search_q)

for item in all_news:
    st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

st.divider()

# 8. Markets & Forex
sent_title = "📈 Market Indices | Sentiment: :orange[⚖️ CAUTIOUS] (Energy Market Focus)"
with st.expander(sent_title, expanded=True):
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

# 9. COE & Fuel (Data from v9.7)
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>', unsafe_allow_html=True)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
