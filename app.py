import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.1", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_v101")

# 2. Adaptive CSS (Optimized Spacing)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; padding-top: 0.5rem; color: var(--text-color); }
    hr { margin: 0.4rem 0 !important; }
    
    /* Reduced row spacing */
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 4px; border-radius: 8px; text-align: center; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 6px; border-radius: 6px; margin-bottom: 2px; min-height: 150px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 8px; border-radius: 10px; text-align: center; color: var(--text-color); }
    
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 5px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.8rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.8rem; }
    
    /* Integrated Holiday Style */
    .next-h { color: #28a745; font-size: 0.9rem; font-weight: normal; margin-left: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Holiday Logic
def get_next_holiday():
    now = datetime.now(pytz.timezone('Asia/Singapore'))
    # Next: Good Friday 2026-04-03
    h_date = datetime(2026, 4, 3, tzinfo=pytz.timezone('Asia/Singapore'))
    days_left = (h_date - now).days + 1
    return f"Next: Good Friday (Apr 3) — ⏳ {days_left} days to go!"

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
    st.write(f"### 📍 {ftype} Price List & Changes")
    for brand in brand_order:
        if brand in fuel_data[ftype]:
            p, c = fuel_data[ftype][brand]
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:5px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff;'>${p:.2f}</b> <small class='{'up' if c>0 else 'down'}'>({'+' if c>0 else ''}{c:.2f})</small></span></div>", unsafe_allow_html=True)

# --- UI START ---
# Clocks
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. Headlines with Holiday Integrated
h_text = get_next_holiday()
st.markdown(f'### 🗞️ Singapore Headlines <span class="next-h">{h_text}</span>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍 Search:", placeholder="Filter news...", label_visibility="collapsed")
with c2: v_mode = st.selectbox("Source:", ["Unified", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"], label_visibility="collapsed")

# (News fetch logic for CNA, ST, Mothership, and 8world category 176 remains same)
# [Fetch Loop Here]

st.divider()

# 6. Markets & COE (Condensed)
with st.expander("📈 Markets & Forex", expanded=True):
    m_cols = st.columns(4)
    m_cols[0].metric("STI Index", "4,841.30", "-2.20%")
    m_cols[1].metric("Gold", "$4,202.90", "-8.04%")
    m_cols[2].metric("Brent Oil", "$113.34", "+1.02%")
    m_cols[3].metric("SGD/MYR", "3.4412", "+0.12%")

with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:4px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>', unsafe_allow_html=True)

# 7. Fuel Prices (Expander Back)
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    f_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
        avg = sum(prices) / len(prices) if prices else 0
        f_cols[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
        if f_cols[i].button("Details", key=f"f_{i}"):
            show_fuel_details(ftype)

st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')}")
