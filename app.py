import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 9.5", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_95_fix")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 10px; min-height: 190px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; color: var(--text-color); }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .up { color: #ff4b4b !important; font-weight: bold; } 
    .down { color: #28a745 !important; font-weight: bold; }
    .stat-label { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    
    /* Reduced font size for Markets and Forex content */
    div[data-testid="stExpander"]:nth-of-type(1) [data-testid="stMetricValue"],
    div[data-testid="stExpander"]:nth-of-type(2) [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    div[data-testid="stExpander"]:nth-of-type(1) [data-testid="stMetricLabel"],
    div[data-testid="stExpander"]:nth-of-type(2) [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Definitions
brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
fuel_data = {
    "92 Octane": {"Esso": 3.43, "Caltex": 3.43, "SPC": 3.43, "Cnergy": "N/A", "Sinopec": "N/A", "Smart Energy": "N/A"},
    "95 Octane": {"Esso": 3.47, "Caltex": 3.47, "Shell": 3.47, "SPC": 3.46, "Cnergy": 2.46, "Sinopec": 3.47, "Smart Energy": 2.61},
    "98 Octane": {"Esso": 3.97, "Shell": 3.99, "SPC": 3.97, "Cnergy": 2.80, "Sinopec": 3.97, "Smart Energy": 2.99},
    "Premium": {"Caltex": 4.16, "Shell": 4.21, "Sinopec": 4.10, "Cnergy": "N/A", "Smart Energy": "N/A"},
    "Diesel": {"Esso": 3.73, "Caltex": 3.73, "Shell": 3.73, "SPC": 3.56, "Cnergy": 2.80, "Sinopec": 3.72, "Smart Energy": 2.83}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List")
    for brand in brand_order:
        price = fuel_data[ftype].get(brand, "N/A")
        if brand == "Shell" and ftype == "92 Octane": continue
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:8px; border-bottom:1px solid #333;'><b>{brand}</b><span>{display_price}</span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 9.5")

# 4. Country Clocks
countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
t_cols = st.columns(6)
for i, (name, tz) in enumerate(countries):
    t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. News Section
st.header("🗞️ Singapore Headlines")
news_sources = {
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", 
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", 
    "Mothership": "https://mothership.sg/feed/", 
    "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
}
c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍 Search Keywords:", placeholder="Enter topic...")
with c2: v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])

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

# 6. Markets with Sentiment in Title (Reduced Content Font via CSS)
sent_title = "📈 Market Indices | Sentiment: :orange[⚖️ CAUTIOUS] (Middle East Tensions & Oil Volatility)"
with st.expander(sent_title, expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-2.20%")
    m2.metric("Gold (Spot)", "$4,202.90", "-8.04%")
    m3.metric("Brent Crude", "$113.34", "+1.02%")
    m4.metric("Silver (Spot)", "$64.12", "-7.56%")

# 7. Forex (Reduced Content Font via CSS)
with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("SGD/MYR", "3.4412", "+0.12%")
    f2.metric("SGD/JPY", "118.55", "-0.43%")
    f3.metric("SGD/THB", "26.85", "+0.15%")
    f4.metric("SGD/CNY", "5.3975", "-0.07%")
    f5.metric("SGD/USD", "0.7480", "-0.22%")

# 8. COE Bidding (Full Details Restored)
with st.expander("🚗 COE Bidding Results (Mar 2nd 2026)", expanded=True):
    # Data based on latest March 18 Results
    coe_data = [
        ("Cat A", 111890, 3670, 1264, 1895), 
        ("Cat B", 115568, 1566, 812, 1185), 
        ("Cat C", 78000, 2000, 290, 438), 
        ("Cat D", 9589, 987, 546, 726), 
        ("Cat E", 118119, 3229, 246, 422)
    ]
    coe_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        coe_cols[i].markdown(f"""
            <div class="c-card">
                <b>{cat}</b><br>
                <span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br>
                <small class="up">▲ ${d:,}</small><br>
                <hr style="margin:8px 0; opacity:0.1; border-color: var(--border-color);">
                <span class="stat-label">Quota:</span> <b>{q:,}</b><br>
                <span class="stat-label">Bids Rec'd:</span> <b>{b:,}</b>
            </div>
        """, unsafe_allow_html=True)

# 9. Fuel Prices
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    f_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v for v in fuel_data[ftype].values() if isinstance(v, (int, float))]
        avg = sum(prices) / len(prices) if prices else 0
        f_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if f_cols[i].button("Details", key=f"fbtn_v95_{i}"):
            show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
