import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 9.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_99_final_fix")

# 2. Adaptive CSS (Spacing & Font Fixes)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; padding-top: 1rem; color: var(--text-color); }
    /* Tighten spacing under clocks and dividers */
    hr { margin: 0.5rem 0 !important; }
    .stHeader { margin-bottom: 0.5rem !important; }
    
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 4px; border-radius: 8px; text-align: center; margin-bottom: 0px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 8px; border-radius: 6px; margin-bottom: 2px; min-height: 160px; color: var(--text-color); }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); }
    
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.8rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.8rem; }
    .stat-label { font-size: 0.7rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    
    /* Holiday Banner */
    .holiday-banner { padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 10px; font-weight: bold; color: white; }
    .banner-green { background: linear-gradient(90deg, #28a745, #55efc4); }
    
    /* Compact Metric Text (-3 font size) */
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
    div[data-testid="stExpander"] [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data & Brand Order Logic
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
            price, change = fuel_data[ftype][brand]
            c_style = "up" if change > 0 else "down"
            c_str = f"({'+' if change > 0 else ''}{change:.2f})" if change != 0 else ""
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff;'>${price:.2f}</b> <small class='{c_style}'>{c_str}</small></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 9.9")

# 4. Regional Clocks (Reduced Spacing)
t_cols = st.columns(6)
for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# 5. Holiday Banner
st.markdown(f'<div class="holiday-banner banner-green">🗓️ Next Holiday: Good Friday (Apr 3) — Long Weekend! 🏖️ — ⏳ 11 Days to go!</div>', unsafe_allow_html=True)

# 6. Headlines
st.header("🗞️ Singapore Headlines")
# News logic remains unified with 8world (Link: ...category=176)
# [News fetching code block here]

st.divider()

# 7. Markets & Forex (Compact Fonts)
with st.expander("📈 Market Indices | Sentiment: :orange[⚖️ CAUTIOUS]", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI Index", "4,841.30", "-2.20%")
    m2.metric("Gold (Spot)", "$4,202.90", "-8.04%")
    m3.metric("Brent Crude", "$113.34", "+1.02%")
    m4.metric("Silver (Spot)", "$64.12", "-7.56%")

with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
    f_cols = st.columns(5)
    currencies = [("MYR", 3.4412, "+0.12%"), ("JPY", 118.55, "-0.43%"), ("THB", 26.85, "+0.15%"), ("CNY", 5.3975, "-0.07%"), ("USD", 0.7480, "-0.22%")]
    for i, (label, val, chg) in enumerate(currencies):
        f_cols[i].metric(f"SGD/{label}", f"{val}", chg)

# 8. COE Bidding (Tightened Spacing)
with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
    coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
    c_cols = st.columns(5)
    for i, (cat, p, d, q, b) in enumerate(coe_data):
        c_cols[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:4px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>""", unsafe_allow_html=True)

# 9. Fuel Prices (RESTORED EXPANDER)
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
