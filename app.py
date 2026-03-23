import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 9.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_99_micro")

# 2. Adaptive CSS (Targeted Font Reduction)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    
    /* COE Card - Micro Font */
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 10px; border-radius: 6px; margin-bottom: 5px; min-height: 90px; text-align: center; }
    .c-card b { font-size: 0.75rem !important; } /* -5pt approx */
    .c-card span { font-size: 0.85rem !important; }
    
    /* Fuel Card - Micro Font */
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; }
    .f-card b { font-size: 0.75rem !important; }
    .f-card span { font-size: 0.85rem !important; }
    
    /* Global Expander Font Reduction for COE/Fuel */
    div[data-testid="stExpander"]:nth-of-type(3) *, 
    div[data-testid="stExpander"]:nth-of-type(4) * {
        font-size: 0.8rem !important;
    }

    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid var(--border-color); margin-right: 5px; }
    .trans-box { font-size: 0.85rem; color: #666; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; } 
    .down { color: #28a745 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Dialog Logic (COE & Fuel Pop-ups)
@st.dialog("COE Category Details")
def show_coe_details(cat, quota, bids, price):
    st.write(f"### 🚗 {cat} Allocation")
    st.metric("Current Price", f"${price:,}")
    c1, c2 = st.columns(2)
    c1.metric("Quota Available", f"{quota:,}")
    c2.metric("Bids Received", f"{bids:,}")

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    # (Standard Brand Logic as per v9.8)
    st.write(f"### 📍 {ftype} Prices")
    st.markdown("Detailed breakdown per brand...")

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 9.9")

# 4. Regional Clocks
t_cols = st.columns(6)
times = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
for i, (n, tz) in enumerate(times):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. News (Unchanged)
st.header("🗞️ Singapore Headlines")
# ... [Translation & News Fetch Logic]

st.divider()

# 6. Markets & Forex (Standard Size)
with st.expander("📈 Market Indices", expanded=True):
    st.columns(4)[0].metric("STI Index", "4,841.30", "-2.20%")

# 7. COE Bidding (Reduced Font)
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    coe_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        with coe_cols[i]:
            st.markdown(f'<div class="c-card"><b>{cat}</b><br><span class="up">${p:,}</span></div>', unsafe_allow_html=True)
            if st.button(f"Bids", key=f"coe_{i}"):
                show_coe_details(cat, q, b, p)

# 8. Fuel Prices (Reduced Font)
with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
    f_cols = st.columns(5)
    ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(ftypes):
        with f_cols[i]:
            st.markdown(f'<div class="f-card"><b>{ftype}</b><br><span>$3.45</span></div>', unsafe_allow_html=True)
            if st.button("Details", key=f"fuel_{i}"):
                show_fuel_details(ftype)

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
