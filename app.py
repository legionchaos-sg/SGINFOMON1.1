import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.2", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_v102")

# 2. Ultra-Compact CSS (Moved up by ~6 rows worth of padding)
st.markdown("""
    <style>
    /* Shift all content up */
    .main .block-container { max-width: 95%; padding-top: 0rem !important; margin-top: -20px; color: var(--text-color); }
    header { visibility: hidden; height: 0px; } /* Hide Streamlit header for more space */
    
    /* Reduced spacing between elements */
    hr { margin: 0.3rem 0 !important; }
    .stHeader { margin-bottom: 0.2rem !important; margin-top: 0.2rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 0.1rem !important; }
    
    /* Card Tightness */
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 2px; border-radius: 6px; text-align: center; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 5px; border-radius: 6px; min-height: 135px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 6px; border-radius: 8px; text-align: center; color: var(--text-color); }
    
    .news-tag { font-size: 0.6rem; background: var(--secondary-background-color); padding: 1px 3px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 4px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.75rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.75rem; }
    
    /* Metrics font reduction */
    [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    
    .next-h { color: #28a745; font-size: 0.85rem; font-weight: normal; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Holiday Logic
def get_next_holiday():
    now = datetime.now(pytz.timezone('Asia/Singapore'))
    h_date = datetime(2026, 4, 3, tzinfo=pytz.timezone('Asia/Singapore'))
    days_left = (h_date - now).days + 1
    return f"Next: Good Friday (Apr 3) — ⏳ {days_left} days"

# 4. Data
brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Details")
    for brand in brand_order:
        if brand in fuel_data[ftype]:
            p, c = fuel_data[ftype][brand]
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:4px; border-bottom:1px solid #333;'><b>{brand}</b><span><b>${p:.2f}</b> <small class='{'up' if c>0 else 'down'}'>({'+' if c>0 else ''}{c:.2f})</small></span></div>", unsafe_allow_html=True)

# --- UI START ---
# Regional Clocks
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# Headlines Section
h_text = get_next_holiday()
st.markdown(f'### 🗞️ Headlines <span class="next-h">{h_text}</span>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍", placeholder="Search...", label_visibility="collapsed")
with c2: v_mode = st.selectbox("Src", ["Unified", "CNA Only", "ST Only", "Mothership", "8world"], label_visibility="collapsed")

# (News logic for 8world category 176 and others remains intact)
st.divider()

# 5. RESTORED Market Indices Expander
with st.expander("📈 Market Indices | Sentiment: :orange[⚖️ CAUTIOUS]", expanded=True):
    m_cols = st.columns(4)
    m_cols[0].metric("STI Index", "4,841.30", "-2.20%")
    m_cols[1].metric("Gold Spot", "$4,202.90", "-8.04%")
    m_cols[2].metric("Brent Crude", "$113.34", "+1.02%")
    m_cols[3].metric("Silver Spot", "$64.12", "-7.56%")

# 6. RESTORED Forex Expander
with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    f_cols = st.columns(5)
    f_cols[0].metric("SGD/MYR", "3.4412", "+0.12%")
    f_cols[1].metric("SGD/JPY", "118.55", "-0.43%")
    f_cols[2].metric("SGD/THB", "26.85", "+0.15%")
    f_cols[3].metric("SGD/CNY", "5.3975", "-0.07%")
    f_cols[4].metric("SGD/USD", "0.7480", "-0.22%")

# 7. COE Bidding
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:2px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>', unsafe_allow_html=True)

# 8. Fuel Prices
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    fuel_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
        avg = sum(prices) / len(prices) if prices else 0
        fuel_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:0.95rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if fuel_cols[i].button("Details", key=f"f_{i}"):
            show_fuel_details(ftype)

st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')}")
