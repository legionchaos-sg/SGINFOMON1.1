import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.3", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_103_stable")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 10px; min-height: 190px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; color: var(--text-color); }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .trans-box { font-size: 0.85rem; color: #666; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.85rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.85rem; }
    .stat-label { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    .holiday-text { font-size: 1rem; color: #28a745; font-weight: bold; margin-left: 10px; }
    
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
    div[data-testid="stExpander"] [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Holiday Logic
def get_upcoming_holiday():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz).date()
    # 2026 Singapore Holidays
    holidays_2026 = [
        ("New Year's Day", datetime(2026, 1, 1).date()),
        ("Chinese New Year", datetime(2026, 2, 17).date()),
        ("Hari Raya Puasa", datetime(2026, 3, 21).date()),
        ("Good Friday", datetime(2026, 4, 3).date()),
        ("Labour Day", datetime(2026, 5, 1).date()),
        ("Hari Raya Haji", datetime(2026, 5, 27).date()),
        ("Vesak Day", datetime(2026, 5, 31).date()),
        ("National Day", datetime(2026, 8, 9).date()),
        ("Deepavali", datetime(2026, 11, 8).date()),
        ("Christmas Day", datetime(2026, 12, 25).date())
    ]
    for name, h_date in holidays_2026:
        if h_date >= now:
            days_diff = (h_date - now).days
            return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {days_diff} days"
    return ""

# 4. Fuel Data
brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32), "Cnergy": ("N/A", 0), "Sinopec": ("N/A", 0), "Smart Energy": ("N/A", 0)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20), "Cnergy": ("N/A", 0), "Smart Energy": ("N/A", 0)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List")
    for brand in brand_order:
        data = fuel_data[ftype].get(brand, ("N/A", 0))
        price, change = data
        if brand == "Shell" and ftype == "92 Octane": continue
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        c_class = "up" if change > 0 else "down"
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:8px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff; margin-right:8px;'>{display_price}</b><span class='{c_class}'>({change:+.2f})</span></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.3")

# 5. Clocks
t_cols = st.columns(6)
countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
for i, (name, tz) in enumerate(countries):
    t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 6. News & Holidays
holiday_info = get_upcoming_holiday()
st.markdown(f'### 🗞️ Singapore Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)

news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/", "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"}
headers = {'User-Agent': 'Mozilla/5.0'}

c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍 Search Keywords:", key="news_search")
with c2: 
    v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
    do_tr = st.checkbox("Translate (EN → CN)")

news_list = []
for src, url in news_sources.items():
    if "Unified" in v_mode or src in v_mode:
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:(1 if "Unified" in v_mode else 10)]:
                    if not search_q or search_q.lower() in entry.title.lower():
                        news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
        except: pass

tr_dict = {}
if do_tr and news_list:
    en_titles = [x['title'] for x in news_list if x['src'] != "8world"]
    if en_titles:
        try:
            translated = GoogleTranslator(target='zh-CN').translate("\n".join(en_titles)).split("\n")
            tr_dict = dict(zip(en_titles, translated))
        except: pass

for item in news_list:
    st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
    if do_tr and item['title'] in tr_dict:
        st.markdown(f"<div class='trans-box'>🇨🇳 {tr_dict[item['title']]}</div>", unsafe_allow_html=True)

st.divider()

# 7. Markets & Forex
with st.expander("📈 Market Indices | Sentiment: :orange[⚖️ CAUTIOUS]", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-2.20%")
    m2.metric("Gold (Spot)", "$4,202.90", "-8.04%")
    m3.metric("Brent Crude", "$113.34", "+1.02%")
    m4.metric("Silver (Spot)", "$64.12", "-7.56%")

with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("SGD/MYR", "3.4412", "+0.12%")
    f2.metric("SGD/JPY", "118.55", "-0.43%")
    f3.metric("SGD/THB", "26.85", "+0.15%")
    f4.metric("SGD/CNY", "5.3975", "-0.07%")
    f5.metric("SGD/USD", "0.7480", "-0.22%")

# 8. COE Bidding
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    coe_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        coe_cols[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:8px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids Rec'd:</span> <b>{b:,}</b></div>""", unsafe_allow_html=True)

# 9. Fuel Prices
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    f_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
        avg = sum(prices) / len(prices) if prices else 0
        f_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if f_cols[i].button("Details", key=f"fuel_btn_{ftype}"):
            show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
