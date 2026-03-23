import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 9.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_90_full")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 10px; min-height: 175px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; color: var(--text-color); }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .up { color: #ff4b4b !important; font-weight: bold; } 
    .down { color: #28a745 !important; font-weight: bold; }
    .stat-label { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. COMPLETE Fuel Database (All Brands Restored)
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.04), "Caltex": (3.43, 0.04), "SPC": (3.43, 0.00), "Cnergy": (3.40, -0.01)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Caltex": (3.47, 0.04), "SPC": (3.46, 0.02), "Sinopec": (3.47, 0.04), "Cnergy": (3.44, 0.00)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "Caltex": (4.16, 0.08), "SPC": (3.97, 0.05), "Sinopec": (3.98, 0.05)},
    "Premium": {"Shell V-Power": (4.21, 0.05), "Caltex Platinum": (4.16, 0.08), "Sinopec X-Power": (4.10, 0.04)},
    "Diesel": {"Esso": (3.73, -0.04), "Shell": (3.73, -0.04), "SPC": (3.56, -0.06), "Cnergy": (3.45, -0.08), "Sinopec": (3.70, -0.04)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Full Price List")
    # Display in 2 columns for better pop-up fit
    cols = st.columns(2)
    for i, (brand, (price, change)) in enumerate(fuel_data[ftype].items()):
        c_style, c_sym = ("up", "▲") if change > 0 else ("down", "▼")
        cols[i % 2].markdown(f"""
            <div style="padding:8px; border-bottom:1px solid var(--border-color);">
                <b>{brand}</b><br>
                <span style="color:#007bff; font-size:1.1rem;">${price:.2f}</span>
                <small class='{c_style}'>{c_sym}${abs(change):.2f}</small>
            </div>
        """, unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 9.0")

# 4. Country Clocks
countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
t_cols = st.columns(6)
for i, (name, tz) in enumerate(countries):
    t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. News Section with Search & Unified logic
st.header("🗞️ Singapore Headlines")
news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/", "8world News": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176", "Shin Min Daily": "https://www.shinmin.sg/rss"}

c1, c2, c3 = st.columns([1.5, 1, 1])
with c1: search_q = st.text_input("🔍 Search Keywords:", placeholder="Enter topic...")
with c2: v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only", "Shin Min Only"])
with c3: do_tr = st.checkbox("Translate (EN → CN)")

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

# 6. Market Indices
with st.expander("📈 Market Indices", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-2.20%")
    m2.metric("Gold (Spot)", "$4,202.90", "-8.04%")
    m3.metric("Silver (Spot)", "$64.12", "-7.56%")
    m4.metric("Brent Crude", "$113.13", "+0.84%")

# 7. Forex (SGD AGAINST OTHERS)
with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("SGD/MYR", "3.4412", "+0.12%")
    f2.metric("SGD/JPY", "118.55", "-0.43%")
    f3.metric("SGD/THB", "26.85", "+0.15%")
    f4.metric("SGD/CNY", "5.3975", "-0.07%")
    f5.metric("SGD/USD", "0.7480", "-0.22%") # Standard 1/1.3369

# 8. COE Bidding Results
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895, 133), ("Cat B", 115568, 1566, 812, 1185, -76), ("Cat C", 78000, 2000, 290, 438, -50), ("Cat D", 9589, 987, 546, 726, 83), ("Cat E", 118119, 3229, 246, 422, -92)]
    coe_cols = st.columns(5)
    for i, (cat, p, d, q, b, bd) in enumerate(coe_data):
        b_cls, b_sym = ("up", "▲") if bd > 0 else ("down", "▼")
        coe_cols[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:8px 0; opacity:0.1; border-color: var(--border-color);"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b><br><small class="{b_cls}">{b_sym} {abs(bd)}</small></div>""", unsafe_allow_html=True)

# 9. Fuel Prices (Full Brand Integration)
with st.expander("⛽ Fuel Prices (All Brands)", expanded=True):
    f_cols = st.columns(5)
    for i, ftype in enumerate(list(fuel_data.keys())):
        avg = sum([v[0] for v in fuel_data[ftype].values()]) / len(fuel_data[ftype])
        f_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if f_cols[i].button("Details", key=f"fbtn_full_{i}"):
            show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
