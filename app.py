import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Setup
st.set_page_config(page_title="SG INFO MON 7.6", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync")

st.markdown("""
    <style>
    .main .block-container { max-width: 95%; height: auto !important; }
    .t-card {background:#f8f9fa; border:1px solid #ddd; padding:8px; border-radius:8px; text-align:center; margin-bottom:5px;}
    .c-card {background:#f8f9fa; border-left:4px solid #ff4b4b; padding:12px; border-radius:6px; margin-bottom:10px;}
    .f-card {background:#f1f7ff; border:1px solid #007bff; padding:15px; border-radius:10px; text-align:center;}
    .news-tag {font-size:0.65rem; background:#eee; padding:2px 4px; border-radius:3px; color:#666; margin-right:5px; font-weight:bold;}
    .trans-box {font-size:0.85rem; color:#d32f2f; margin-left:55px; margin-top:-10px; margin-bottom:12px; font-style:italic;}
    .up {color: #d32f2f; font-weight: bold;} .down {color: #28a745; font-weight: bold;}
    @media (prefers-color-scheme: dark) { .t-card, .c-card {background:#262730; border-color:#444;} .f-card {background:#1e2630;} }
    </style>
    """, unsafe_allow_html=True)

# 2. Data
fuel_trends = {
    "92 Octane": {"Esso": (3.43, 0.04), "Caltex": (3.43, 0.04), "SPC": (3.43, 0.00), "Cnergy": (3.40, -0.01)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Caltex": (3.47, 0.04), "SPC": (3.46, 0.02), "Sinopec": (3.47, 0.04)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "Caltex": (4.16, 0.08), "SPC": (3.97, 0.05)},
    "Premium": {"V-Power": (4.21, 0.05), "Platinum": (4.16, 0.08), "X-Power": (4.10, 0.04)},
    "Diesel": {"Esso": (3.73, -0.04), "Shell": (3.73, -0.04), "SPC": (3.56, -0.06), "Cnergy": (3.45, -0.08)}
}

@st.dialog("Fuel Brand Comparison")
def show_fuel(ftype):
    st.subheader(f"📍 {ftype} Breakdown")
    data = fuel_trends[ftype]
    cols = st.columns(2)
    for i, (brand, (p, c)) in enumerate(data.items()):
        tr = f'<span class="{"up" if c>0 else "down"}">{"▲" if c>0 else "▼"} ${abs(c):.2f}</span>' if c!=0 else "Stable"
        cols[i%2].markdown(f'<div style="padding:10px; border-bottom:1px solid #ddd;"><b>{brand}</b><br><span style="font-size:1.2rem; color:#007bff;">${p:.2f}</span><br>{tr}</div>', unsafe_allow_html=True)

# --- UI ---
st.title("🇸🇬 Singapore Info Monitor 7.6")
zones = [("SGT","Asia/Singapore"),("ICT","Asia/Bangkok"),("JST","Asia/Tokyo"),("WIB","Asia/Jakarta"),("PHT","Asia/Manila"),("AEST","Australia/Brisbane")]
t_cols = st.columns(6)
for i, (n, z) in enumerate(zones):
    t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(z)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

st.divider()
st.header("🗞️ Singapore Headlines")
srcs = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "ST": "https://www.straitstimes.com/news/singapore/rss.xml", "MS": "https://mothership.sg/feed/"}
unified = []
for n, u in srcs.items():
    try:
        f = feedparser.parse(requests.get(u, timeout=5).content)
        if f.entries: unified.append({'n': n, 't': f.entries[0].title, 'l': f.entries[0].link})
    except: pass

do_tr = st.checkbox("Translate")
tr_list = []
if do_tr and unified:
    try: tr_list = GoogleTranslator(target='zh-CN').translate("\n".join([x['t'] for x in unified])).split("\n")
    except: pass

for i, item in enumerate(unified):
    st.write(f"<span class='news-tag'>{item['n']}</span> **[{item['t']}]({item['l']})**", unsafe_allow_html=True)
    if do_tr and i < len(tr_list): st.markdown(f"<div class='trans-box'>🇨🇳 {tr_list[i].strip()}</div>", unsafe_allow_html=True)

st.divider()
with st.expander("📊 Markets & COE", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STI", "4,841.30", "-2.2%")
    m2.metric("Gold", "$4,400.00", "-8.8%")
    m3.metric("USD/SGD", "1.2770", "-0.4%")
    m4.metric("CNY/SGD", "5.3842", "+0.2%")
    st.write("---")
    coe = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
    c_cols = st.columns(5)
    for i, (cat, p, d) in enumerate(coe):
        c_cols[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#d32f2f;font-size:1.1rem;font-weight:bold;">${p:,}</span><br><small>▲ ${d:,}</small></div>', unsafe_allow_html=True)

with st.expander("⛽ Fuel Prices", expanded=True):
    f_types = list(fuel_trends.keys())
    f_cols = st.columns(5)
    for i, ftype in enumerate(f_types):
        with f_cols[i]:
            avg = sum([v[0] for v in fuel_trends[ftype].values()]) / len(fuel_trends[ftype])
            st.markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if st.button(f"View {ftype}", key=f"b_{i}"): show_fuel(ftype)

st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
