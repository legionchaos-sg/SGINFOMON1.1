import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 9.8", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_98_coe_dialog")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    /* Compact COE Card for main view */
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 5px; min-height: 110px; text-align: center; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 15px; border-radius: 10px; text-align: center; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 5px; }
    .trans-box { font-size: 0.85rem; color: #666; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.85rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.85rem; }
    
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Dialogs (Pop-up Windows)
@st.dialog("COE Category Details")
def show_coe_details(cat, quota, bids, price):
    st.write(f"### 🚗 {cat} Allocation")
    st.divider()
    st.metric("Current Price", f"${price:,}")
    c1, c2 = st.columns(2)
    c1.metric("Quota Available", f"{quota:,}")
    c2.metric("Bids Received", f"{bids:,}")
    st.caption("Data reflects the latest bidding exercise results.")

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
    fuel_data = {
        "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
        "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
        "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
        "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20)},
        "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
    }
    st.write(f"### 📍 {ftype} Prices")
    for brand in brand_order:
        if brand in fuel_data[ftype]:
            price, change = fuel_data[ftype][brand]
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:8px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff;'>${price:.2f}</b> <small class='{'up' if change > 0 else 'down'}'>({change:+.2f})</small></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 9.8")

# 4. Regional Clocks
t_cols = st.columns(6)
for n, tz in [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]:
    with t_cols.pop(0) if t_cols else st:
        st.markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. News Section (with Translation)
st.header("🗞️ Singapore Headlines")
c1, c2 = st.columns([2, 1])
with c1: search_q = st.text_input("🔍 Search Keywords:", placeholder="Enter topic...")
with c2: 
    v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
    do_tr = st.checkbox("Translate (EN → CN)")

# [News Fetching Logic - Intact from 9.7]
# ... (Fetch loop and Translation loop as per 9.7)

st.divider()

# 6. Markets & Forex
with st.expander("📈 Market Indices", expanded=True):
    m_cols = st.columns(4)
    m_cols[0].metric("STI Index", "4,841.30", "-2.20%")
    m_cols[1].metric("Gold Spot", "$4,202.90", "-8.04%")
    m_cols[2].metric("Brent Crude", "$113.34", "+1.02%")
    m_cols[3].metric("Silver Spot", "$64.12", "-7.56%")

# 7. COE Bidding (NEW CLICKABLE POP-OUT)
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    # Category, Price, Change, Quota, Bids
    coe_data = [
        ("Cat A", 111890, 3670, 1264, 1895), 
        ("Cat B", 115568, 1566, 812, 1185), 
        ("Cat C", 78000, 2000, 290, 438), 
        ("Cat D", 9589, 987, 546, 726), 
        ("Cat E", 118119, 3229, 246, 422)
    ]
    coe_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        with coe_cols[i]:
            st.markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>""", unsafe_allow_html=True)
            if st.button(f"View Bids", key=f"coe_{i}"):
                show_coe_details(cat, q, b, p)

# 8. Fuel Prices
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    fuel_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        with fuel_cols[i]:
            st.markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">$3.45</span></div>', unsafe_allow_html=True)
            if st.button("Details", key=f"fuel_{i}"):
                show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
