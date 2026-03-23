import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config & Unlimited Vertical Space
st.set_page_config(page_title="SG INFO MON 7.5", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="master_sync")

# 2. CSS for Responsive Grids & Unlimited Height
st.markdown("""
    <style>
    /* Prevent vertical clipping */
    .main .block-container { max-width: 95%; padding-top: 1rem; height: auto !important; }
    
    /* Time & Card Styling */
    .time-card {background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center; margin-bottom:5px;}
    .coe-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:12px; border-radius:6px; margin-bottom:10px; min-height:100px;}
    .fuel-card {background:#f1f7ff; border:1px solid #007bff; padding:15px; border-radius:10px; text-align:center;}
    
    /* Trend Indicators */
    .trend-up {color: #d32f2f; font-weight: bold; font-size: 0.9rem;}
    .trend-down {color: #28a745; font-weight: bold; font-size: 0.9rem;}
    
    /* News Styling */
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    
    @media (prefers-color-scheme: dark) { 
        .time-card, .coe-card {background:#262730; border-color:#444;}
        .fuel-card {background:#1e2630; border-color:#007bff;}
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA: March 23, 2026
fuel_trends = {
    "92 Octane": {"Esso": (3.43, 0.04), "Caltex": (3.43, 0.04), "SPC": (3.43, 0.00), "Cnergy": (3.40, -0.01), "SmartEnergy": (3.41, 0.01)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Caltex": (3.47, 0.04), "SPC": (3.46, 0.02), "Sinopec": (3.47, 0.04), "Cnergy": (3.44, -0.02), "SmartEnergy": (3.45, -0.01)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "Caltex": (4.16, 0.08), "SPC": (3.97, 0.05), "Sinopec": (3.97, 0.05), "Cnergy": (3.92, -0.03), "SmartEnergy": (3.94, -0.02)},
    "Premium": {"Shell V-Power": (4.21, 0.05), "Caltex Platinum": (4.16, 0.08), "Sinopec X-Power": (4.10, 0.04), "Esso Supreme+": (3.97, 0.05)},
    "Diesel": {"Esso": (3.73, -0.04), "Shell": (3.73, -0.04), "Caltex": (3.73, -0.04), "SPC": (3.56, -0.06), "Sinopec": (3.72, -0.05), "Cnergy": (3.45, -0.08), "SmartEnergy": (3.49, -0.07)}
}

# 4. Brand Dialog Pop-up
@st.dialog("Fuel Brand Comparison (Mar 2026)")
def show_fuel_details(fuel_type):
    st.subheader(f"📍 {fuel_type} Breakdown")
    data = fuel_trends[fuel_type]
    col1, col2 = st.columns(2)
    for i, (brand, (price, change)) in enumerate(data.items()):
        target = col1 if i % 2 == 0 else col2
        trend = f'<span class="trend-up">▲ +${change:.2f}</span>' if change > 0 else (f'<span class="trend-down">▼ -${abs(change):.2f}</span>' if change < 0 else '<span style="color:gray;">● Stable</span>')
        target.markdown(f'<div style="padding:10px; border-bottom:1px solid #ddd;"><b>{brand}</b><br><span style="font-size:1.2rem; color:#007bff;">${price:.2f}</span><br>{trend}</div>', unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 Singapore Info Monitor 7.5")

# Times (Grid: 3 cols x 2 rows for stability)
st.write("### 🌍 Global Exchange Times")
t_row1 = st.columns(3)
t_row2 = st.columns(3)
zones = [("Singapore SGT","Asia/Singapore"), ("Bangkok ICT","Asia/Bangkok"), ("Tokyo JST","Asia/Tokyo"), 
         ("Jakarta WIB","Asia/Jakarta"), ("Manila PHT","Asia/Manila"), ("Brisbane AEST","Australia/Brisbane")]

for i, (name, tz) in enumerate(zones):
    target_col = t_row1[i] if i < 3 else t_row2[i-3]
    target_col.markdown(f'<div class="time-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()

# News Section
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

do_tr = st.checkbox("Enable Chinese Translation")
trans_list = []
if do_tr and unified:
    try:
        mega = "\n".join([x['t'] for x in unified])
        trans_list = GoogleTranslator(target='zh-CN').translate(mega).split("\n")
    except: st.warning("Translator limited.")

for i, item in enumerate(unified):
    st.write(f"<span class='news-tag'>{item['n']}</span> **[{item['t']}]({item['l']})**", unsafe_allow_html=True)
    if do_tr and i < len(trans_list):
        st.markdown(f"<div class='trans-box'>🇨🇳 {trans_list[i].strip()}</div>", unsafe_allow_html=True)

st.divider()

# MARKET & FOREX (Fixed Messy Layout)
with st.expander("📊 Market & Forex Watch", expanded=True):
    # Using 2 rows of 2 for better spacing
    f1, f2 = st.columns(2)
    f3, f4 = st.columns(2)
    f1.metric("STI Index", "4,841.30", "-2.2%", delta_color="inverse")
    f2.metric("Gold (Spot)", "$4,400.00", "-8.8%")
    f3.metric("USD / SGD", "1.2770", "-0.4%")
    f4.metric("CNY / SGD", "5.3842", "+0.2%")

# COE RESULTS (Fixed Grid)
with st.expander("🚘 COE Results (Mar 2026 2nd Bidding)", expanded=True):
    # Use 3 columns for better fit
    c1, c2, c3 = st.columns(3)
    c4, c5, _ = st.columns(3)
    coe_list = [
        (c1, "Cat A", 111890, 3670), (c2, "Cat B", 115568, 1566), (c3, "Cat C", 78000, 2000),
        (c4, "Cat D", 9589, 987), (c5, "Cat E", 118119, 3229)
    ]
    for col, cat, price, delta in coe_list:
        col.markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-size:1.3rem;font-weight:bold;">${price:,}</span><br><small>▲ ${delta:,}</small></div>', unsafe_allow_html=True)

# FUEL SECTION
with st.expander("⛽ Fuel Prices (Interactive Trends)", expanded=True):
    f_cols = st.columns(5)
    f_types = ["92 Octane", "9
