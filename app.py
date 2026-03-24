import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression 
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# SG INFO MONITOR - Version 11.1.0 (gold 10 - STABLE RESTORE)

st.set_page_config(page_title="SG INFO MON 11.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_gold10_v10")

st.markdown("""
    <style>
    .main .block-container { max-width: 95%; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 100px; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; }
    .traffic-pill { padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; color: white; display: inline-block; width: 100%; text-align: center;}
    .incident-box { font-size: 0.82rem; border-left: 4px solid #ff4b4b; padding: 8px; margin-bottom: 6px; background: rgba(255, 75, 75, 0.05); border-radius: 0 6px 6px 0; border: 1px solid var(--border-color); }
    .svc-card { background: var(--secondary-background-color); padding: 15px; border-radius: 10px; border: 1px solid var(--border-color); }
    </style>
    """, unsafe_allow_html=True)

# Data Preserved
fuel_data = {
    "92": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04)},
    "98": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05)},
    "Pre": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05)},
    "Die": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10)}
}

@st.dialog("Fuel Details")
def show_fuel(ftype):
    for b, (p, c) in fuel_data[ftype].items():
        st.write(f"**{b}**: ${p:.2f} ({c:+.2f})")

tab1, tab2, tab3 = st.tabs(["📊 MONITOR", "🏢 SERVICES", "🧪 PMT"])

with tab1:
    # 1. Clocks
    t_cols = st.columns(6)
    for i, (n, tz) in enumerate([("SG", "Asia/Singapore"), ("TH", "Asia/Bangkok"), ("JP", "Asia/Tokyo"), ("ID", "Asia/Jakarta"), ("PH", "Asia/Manila"), ("AU", "Australia/Brisbane")]):
        t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    # 2. Headlines
    st.divider()
    nc1, nc2 = st.columns([2, 1])
    with nc1: q = st.text_input("🔍 Search News:", key="news_q")
    with nc2: tr_on = st.checkbox("CN Trans")
    
    for src, url in {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "ST": "https://www.straitstimes.com/news/singapore/rss.xml"}.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:2]:
                if not q or q.lower() in e.title.lower():
                    st.write(f"**{src}**: [{e.title}]({e.link})")
                    if tr_on: st.caption(GoogleTranslator(target='zh-CN').translate(e.title))
        except: pass

    # 3. Markets & COE
    with st.expander("📈 Markets & COE", expanded=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STI Index", "4,948.87", "-0.38%")
        m2.metric("USD/SGD", "1.2793", "+0.36%")
        m3.metric("Gold", "$4,335", "-1.66%")
        m4.metric("Inflation", "1.20%", "Stable")
        st.markdown("---")
        cc = st.columns(5)
        for i, (c, v) in enumerate([("Cat A", 111890), ("Cat B", 115568), ("Cat C", 78000), ("Cat D", 9589), ("Cat E", 118119)]):
            cc[i].markdown(f'<div class="c-card"><b>{c}</b><br><span style="color:#ff4b4b;">${v:,}</span></div>', unsafe_allow_html=True)

    # 4. Fuel
    with st.expander("⛽ Fuel Prices", expanded=True):
        fc = st.columns(5)
        for i, f in enumerate(["92", "95", "98", "Pre", "Die"]):
            avg = sum([v[0] for v in fuel_data[f].values()]) / len(fuel_data[f])
            fc[i].markdown(f'<div class="f-card"><b>{f}</b><br><b>${avg:.2f}</b></div>', unsafe_allow_html=True)
            if fc[i].button("Info", key=f"btn_{f}"): show_fuel(f)

with tab2:
    st.header("🏢 Public Services")
    # 1. Links & Net
    sc1, sc2 = st.columns(2)
    with sc1: st.markdown('<div class="svc-card"><b>Links:</b> [Singpass](https://www.singpass.gov.sg) | [CPF](https://www.cpf.gov.sg) | [HDB](https://www.hdb.gov.sg)</div>', unsafe_allow_html=True)
    with sc2: st.write("**Network Status:** Singtel: 99.8% ✅ | M1: 92.1% ⚠️")

    # 2. Traffic (Unified & FIXED)
    with st.expander("🛣️ Expressway Traffic & Incidents", expanded=True):
        t_cols = st.columns(6)
        exs = [("CTE", "58", "#28a745"), ("PIE", "32", "#ffc107"), ("AYE", "24", "#dc3545"), ("ECP", "62", "#28a745"), ("KJE", "48", "#ffc107"), ("MCE", "60", "#28a745")]
        for i, (n, s, c) in enumerate(exs):
            t_cols[i].markdown(f'<div style="text-align:center; border:1px solid #444; border-radius:8px; padding:5px;"><b>{n}</b><div class="traffic-pill" style="background-color:{c};">{s}km/h</div></div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("<b>⚠️ Incident Log (Latest Top)</b>", unsafe_allow_html=True)
        incs = [{"t": "22:15", "e": "KPE", "m": "Accident after Bartley Exit. Avoid lane 2."}, {"t": "22:02", "e": "PIE", "m": "Breakdown after Bedok North Exit."}]
        for inc in incs:
            st.markdown(f'<div class="incident-box"><b>[{inc["t"]}] {inc["e"]}</b>: {inc["m"]}</div>', unsafe_allow_html=True)

    # 3. Rail & Weather
    with st.expander("🚆 Rail & 🌤️ Weather", expanded=True):
        rc1, rc2 = st.columns(2)
        with rc1: st.write("**MRT:** EWL: ✅ | NSL: ✅ | CCL: ⚠️ Works")
        with rc2: st.info("**NEA:** Partly Cloudy. 28°C - 31°C")

with tab3:
    st.header("🧪 PMT Trial")
    target = st.selectbox("Target:", ["Currency (USD/SGD)", "Stock Market (STI)", "4D"])
    days = 30
    X = np.array(range(days)).reshape(-1, 1)
    y = np.linspace(100, 110, days) + np.random.normal(0, 1, days)
    model = LinearRegression().fit(X, y)
    pred = model.predict(np.array([[days + 1]]))[0]
    st.metric(f"ML Predicted {target}", f"{pred:.2f}")
    st.line_chart(pd.DataFrame({'History': y, 'Trend': model.predict(X)}))

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT | ID: gold 10")
