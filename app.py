import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup & Auto-Refresh
st.set_page_config(page_title="SG INFO MON 7.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="master_sync")

# 2. Advanced CSS
st.markdown("""
    <style>
    .block-container {padding-top: 1.2rem !important;}
    .time-card {background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center;}
    .coe-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:10px; border-radius:6px;}
    .fuel-card {background:#f1f7ff; border:1px solid #007bff; padding:15px; border-radius:10px; text-align:center;}
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    @media (prefers-color-scheme: dark) { 
        .time-card, .coe-card {background:#262730; border-color:#444;}
        .fuel-card {background:#1e2630; border-color:#007bff;}
        .news-tag {background:#444; color:#bbb;} .trans-box {color:#ffbaba;}
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Storage (March 23, 2026 Prices)
fuel_details = {
    "92 Octane": {"Esso": 3.43, "Caltex": 3.43, "SPC": 3.43, "Shell": "N.A.", "Sinopec": "N.A.", "Cnergy": 3.40, "SmartEnergy": 3.41},
    "95 Octane": {"Esso": 3.47, "Shell": 3.47, "Caltex": 3.47, "SPC": 3.46, "Sinopec": 3.47, "Cnergy": 3.44, "SmartEnergy": 3.45},
    "98 Octane": {"Esso": 3.97, "Shell": 3.99, "Caltex": 4.16, "SPC": 3.97, "Sinopec": 3.97, "Cnergy": 3.92, "SmartEnergy": 3.94},
    "Premium": {"Shell V-Power": 4.21, "Caltex Platinum": 4.16, "Sinopec X-Power": 4.10, "Esso Supreme+": 3.97},
    "Diesel": {"Esso": 3.56, "Shell": 3.56, "Caltex": 3.56, "SPC": 3.49, "Sinopec": 3.55, "Cnergy": 3.45, "SmartEnergy": 3.49}
}

# 4. Pop-out Dialog Function
@st.dialog("Brand Pricing Details")
def show_fuel_details(fuel_type):
    st.subheader(f"📍 {fuel_type} Comparison")
    st.write("Prices shown are before credit card/loyalty discounts.")
    
    data = fuel_details[fuel_type]
    # Display as a clean table
    col1, col2 = st.columns(2)
    for i, (brand, price) in enumerate(data.items()):
        target_col = col1 if i % 2 == 0 else col2
        price_str = f"${price:.2f}/L" if isinstance(price, (int, float)) else price
        target_col.metric(brand, price_str)
    
    st.caption("Data source: Fuel Kaki / Public Monitoring (Mar 2026)")

# --- MAIN UI ---
st.title("🇸🇬 Singapore Info Monitor 7.0")

# Times
t_cols = st.columns(6)
zones = [("Singapore","Asia/Singapore"), ("Bangkok","Asia/Bangkok"), ("Tokyo","Asia/Tokyo"), 
         ("Jakarta","Asia/Jakarta"), ("Manila","Asia/Manila"), ("Brisbane","Australia/Brisbane")]
for i, (c, z) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{c}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(z)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# News (Unified Pool)
st.header("🗞️ Singapore Headlines")
srcs = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
        "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
        "Mothership": "https://mothership.sg/feed/"}

unified = []
for n, u in srcs.items():
    try:
        f = feedparser.parse(requests.get(u, timeout=5).content)
        if f.entries: unified.append({'n': n, 't': f.entries[0].title, 'l': f.entries[0].link})
    except: pass

do_tr = st.checkbox("Fast Translation (Simplified Chinese)")
trans_map = {}
if do_tr and unified:
    try:
        mega = "\n".join([x['t'] for x in unified])
        translated = GoogleTranslator(target='zh-CN').translate(mega).split("\n")
        trans_map = {unified[i]['t']: translated[i] for i in range(len(unified))}
    except: st.error("Translation Unavailable")

for item in unified:
    st.write(f"<span class='news-tag'>{item['n']}</span> **[{item['t']}]({item['l']})**", unsafe_allow_html=True)
    if do_tr and item['t'] in trans_map:
        st.markdown(f"<div class='trans-box'>🇨🇳 {trans_map[item['t']]}</div>", unsafe_allow_html=True)

st.divider()

# Markets & Forex
with st.expander("📊 Market Info & Forex", expanded=True):
    m = st.columns(4)
    m[0].metric("STI Index", "4,841.30", "-2.2%")
    m[1].metric("Gold (Spot)", "$4,282.40", "-4.8%")
    m[2].metric("Silver (Spot)", "$63.47", "-6.1%")
    m[3].metric("Brent Crude", "$112.91", "+0.6%")
    st.write("---")
    f = st.columns(6)
    fx = [("CNY","5.384"),("THB","23.04"),("JPY","111.2"),("MYR","2.747"),("AUD","1.117"),("USD","0.773")]
    for i, (n, v) in enumerate(fx): f[i].metric(n, v)

# COE Bidding
with st.expander("🚗 COE Bidding - Mar 2026", expanded=True):
    coe = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, p, d) in enumerate(coe):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-weight:bold;font-size:1.1rem;">${p:,}</span><br><small>▲ ${d:,}</small></div>', unsafe_allow_html=True)

# FUEL PRICES WITH POPUP
with st.expander("⛽ Fuel Prices (Click for Brand Details)", expanded=True):
    f_cols = st.columns(5)
    labels = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    avg_prices = ["$3.43", "$3.47", "$3.98", "$4.10", "$3.54"]
    
    for i in range(5):
        with f_cols[i]:
            st.markdown(f'<div class="fuel-card"><b>{labels[i]}</b><br><span style="color:#007bff;font-size:1.2rem;font-weight:bold;">{avg_prices[i]}</span></div>', unsafe_allow_html=True)
            if st.button(f"Details: {labels[i]}", key=f"btn_{i}"):
                show_fuel_details(labels[i])

st.divider()
st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT | v7.0 Interactive")
