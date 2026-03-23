import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Config MUST be the first Streamlit command
st.set_page_config(page_title="SG INFO MON 7.4", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="master_sync")

# 2. CSS with High-Contrast Trend Colors
st.markdown("""
    <style>
    .block-container {padding-top: 1.2rem !important;}
    .time-card {background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center;}
    .coe-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:10px; border-radius:6px;}
    .fuel-card {background:#f1f7ff; border:1px solid #007bff; padding:15px; border-radius:10px; text-align:center;}
    .trend-up {color: #d32f2f; font-weight: bold; font-size: 0.9rem;} /* RED for increase */
    .trend-down {color: #28a745; font-weight: bold; font-size: 0.9rem;} /* GREEN for decrease */
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    @media (prefers-color-scheme: dark) { 
        .time-card, .coe-card {background:#262730; border-color:#444;}
        .fuel-card {background:#1e2630; border-color:#007bff;}
        .news-tag {background:#444; color:#bbb;} .trans-box {color:#ffbaba;}
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LIVE DATA: March 23, 2026
fuel_trends = {
    "92 Octane": {"Esso": (3.43, 0.04), "Caltex": (3.43, 0.04), "SPC": (3.43, 0.00), "Cnergy": (3.40, -0.01), "SmartEnergy": (3.41, 0.01)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Caltex": (3.47, 0.04), "SPC": (3.46, 0.02), "Sinopec": (3.47, 0.04), "Cnergy": (3.44, -0.02), "SmartEnergy": (3.45, -0.01)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "Caltex": (4.16, 0.08), "SPC": (3.97, 0.05), "Sinopec": (3.97, 0.05), "Cnergy": (3.92, -0.03), "SmartEnergy": (3.94, -0.02)},
    "Premium": {"Shell V-Power": (4.21, 0.05), "Caltex Platinum": (4.16, 0.08), "Sinopec X-Power": (4.10, 0.04), "Esso Supreme+": (3.97, 0.05)},
    "Diesel": {"Esso": (3.73, -0.04), "Shell": (3.73, -0.04), "Caltex": (3.73, -0.04), "SPC": (3.56, -0.06), "Sinopec": (3.72, -0.05), "Cnergy": (3.45, -0.08), "SmartEnergy": (3.49, -0.07)}
}

# 4. Interactive Dialog with Color-Coded Trends
@st.dialog("Fuel Brand Comparison (Live March 2026)")
def show_fuel_details(fuel_type):
    st.subheader(f"📍 {fuel_type} Market Watch")
    data = fuel_trends[fuel_type]
    col1, col2 = st.columns(2)
    for i, (brand, (price, change)) in enumerate(data.items()):
        target = col1 if i % 2 == 0 else col2
        # Trend logic: Increase = Red (▲), Decrease = Green (▼)
        if change > 0:
            trend_html = f'<span class="trend-up">▲ +${change:.2f}</span>'
        elif change < 0:
            trend_html = f'<span class="trend-down">▼ -${abs(change):.2f}</span>'
        else:
            trend_html = '<span style="color:gray;">● Stable</span>'
            
        target.markdown(f"""
            <div style="padding:10px; border-bottom:1px solid #ddd;">
                <b style="font-size:1rem;">{brand}</b><br>
                <span style="font-size:1.2rem; color:#007bff;">${price:.2f}</span><br>
                {trend_html}
            </div>
            """, unsafe_allow_html=True)

# --- UI MAIN ---
st.title("🇸🇬 Singapore Info Monitor 7.4")

# World Times
t_cols = st.columns(6)
zones = [("Singapore","Asia/Singapore"), ("Bangkok","Asia/Bangkok"), ("Tokyo","Asia/Tokyo"), 
         ("Jakarta","Asia/Jakarta"), ("Manila","Asia/Manila"), ("Brisbane","Australia/Brisbane")]
for i, (c, z) in enumerate(zones):
    t_cols[i].markdown(f'<div class="time-card"><div style="font-size:0.7rem;color:#ff4b4b;font-weight:bold;">{c}</div><div style="font-size:1.1rem;font-weight:bold;">{datetime.now(pytz.timezone(z)).strftime("%H:%M")}</div></div>', unsafe_allow_html=True)

st.divider()

# News Feed
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

do_tr = st.checkbox("Translate (Simplified Chinese)")
trans_list = []
if do_tr and unified:
    try:
        mega = "\n".join([x['t'] for x in unified])
        trans_list = GoogleTranslator(target='zh-CN').translate(mega).split("\n")
    except: st.warning("Translation Service Busy")

for i, item in enumerate(unified):
    st.write(f"<span class='news-tag'>{item['n']}</span> **[{item['t']}]({item['l']})**", unsafe_allow_html=True)
    if do_tr and i < len(trans_list):
        st.markdown(f"<div class='trans-box'>🇨🇳 {trans_list[i].strip()}</div>", unsafe_allow_html=True)

st.divider()

# Market & COE (Fixed For-Loop Syntax)
with st.expander("📊 Market & COE (Mar 2026)", expanded=True):
    m_cols = st.columns(4)
    m_cols[0].metric("STI Index", "4,841.30", "-2.2%")
    m_cols[1].metric("Gold", "$4,400.00", "-8.8%")
    m_cols[2].metric("USD/SGD", "1.277", "-0.4%")
    m_cols[3].metric("CNY/SGD", "5.384", "+0.2%")
    st.write("---")
    
    # Corrected Loop Syntax: Single line declaration
    coe_data = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(len(coe_data))
    for i, (cat, price, delta) in enumerate(coe_data):
        c_cols[i].markdown(f'<div class="coe-card"><b>{cat}</b><br><span style="color:#d32f2f;font-weight:bold;">${price:,}</span><br><small>▲ ${delta:,}</small></div>', unsafe_allow_html=True)

# Fuel Pop-up Launchers
with st.expander("⛽ Fuel Prices (Brand Comparison Trends)", expanded=True):
    f_cols = st.columns(5)
    f_types = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
    for i, ftype in enumerate(f_types):
        with f_cols[i]:
            avg_p = sum([v[0] for v in fuel_trends[ftype].values()]) / len(fuel_trends[ftype])
            st.markdown(f'<div class="fuel-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg_p:.2f}</span></div>', unsafe_allow_html=True)
            if st.button(f"Analyze {ftype}", key=f"fbtn_{i}"):
                show_fuel_details(ftype)

st.divider()
st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT | v7.4 Stable")
