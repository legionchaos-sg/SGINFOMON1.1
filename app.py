import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression 
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# SG INFO MONITOR - Version 11.1.5 (gold 10 - TOTAL STABILITY)

st.set_page_config(page_title="SG INFO MON 11.1", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_gold10_v11")

# Global CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 5px; border-radius: 5px; text-align: center; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
    .traffic-pill { padding: 3px; border-radius: 4px; font-size: 0.75rem; color: white; text-align: center; font-weight: bold; }
    .incident-box { font-size: 0.82rem; border-left: 4px solid #ff4b4b; padding: 8px; margin-bottom: 5px; background: rgba(255,75,75,0.1); border: 1px solid var(--border-color); border-left-width: 4px; }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 MONITOR", "🏢 SERVICES", "🧪 PMT"])

with tab1:
    # 1. Clocks
    cols = st.columns(6)
    zones = [("SG", "Asia/Singapore"), ("TH", "Asia/Bangkok"), ("JP", "Asia/Tokyo"), ("ID", "Asia/Jakarta"), ("PH", "Asia/Manila"), ("AU", "Australia/Brisbane")]
    for i, (n, z) in enumerate(zones):
        cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(z)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    # 2. News
    st.divider()
    c1, c2 = st.columns([2, 1])
    q = c1.text_input("🔍 Search:", key="nq")
    tr = c2.checkbox("CN Trans")
    for s, u in {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "ST": "https://www.straitstimes.com/news/singapore/rss.xml"}.items():
        try:
            f = feedparser.parse(u)
            for e in f.entries[:2]:
                if not q or q.lower() in e.title.lower():
                    st.write(f"**{s}**: [{e.title}]({e.link})")
                    if tr: st.caption(GoogleTranslator(target='zh-CN').translate(e.title))
        except: pass

    # 3. Markets & COE
    with st.expander("📈 Markets & COE", expanded=True):
        m = st.columns(4)
        m[0].metric("STI Index", "4,948.87", "-0.38%")
        m[1].metric("USD/SGD", "1.2793", "+0.36%")
        m[2].metric("Gold", "$4,335", "-1.66%")
        m[3].metric("Inflation", "1.2%", "Stable")
        st.write("---")
        ce = st.columns(5)
        for i, (c, v) in enumerate([("Cat A", 111890), ("Cat B", 115568), ("Cat C", 78000), ("Cat D", 9589), ("Cat E", 118119)]):
            ce[i].markdown(f'<div class="c-card"><b>{c}</b><br><span style="color:#ff4b4b;">${v:,}</span></div>', unsafe_allow_html=True)

    # 4. Fuel
    with st.expander("⛽ Fuel (Avg)", expanded=True):
        fl = st.columns(5)
        for i, (g, p) in enumerate([("92", 3.43), ("95", 3.47), ("98", 3.98), ("Pre", 4.18), ("Die", 3.67)]):
            fl[i].metric(g, f"${p:.2f}")

with tab2:
    st.header("🏢 Public Services")
    # 1. Links & Network
    l1, l2 = st.columns(2)
    l1.info("🔗 [Singpass](https://www.singpass.gov.sg) | [CPF](https://www.cpf.gov.sg) | [HDB](https://www.hdb.gov.sg)")
    l2.write("**Network:** Singtel: 99% ✅ | M1: 92% ⚠️")

    # 2. Unified Traffic & Incidents
    with st.expander("🛣️ Expressway Status & Incidents", expanded=True):
        tx = st.columns(6)
        exs = [("CTE", "58", "#28a745"), ("PIE", "32", "#ffc107"), ("AYE", "24", "#dc3545"), ("ECP", "62", "#28a745"), ("KJE", "48", "#ffc107"), ("MCE", "60", "#28a745")]
        for i, (n, s, c) in enumerate(exs):
            tx[i].markdown(f'<div style="text-align:center;border:1px solid #444;border-radius:5px;padding:3px;"><b>{n}</b><div class="traffic-pill" style="background-color:{c};">{s}km/h</div></div>', unsafe_allow_html=True)
        
        st.divider()
        st.write("**⚠️ Incident Log (Latest Top)**")
        incs = [
            {"t": "22:15", "e": "KPE", "m": "Accident after Bartley Exit. Avoid lane 2."},
            {"t": "22:02", "e": "PIE", "m": "Breakdown after Bedok North Exit."},
            {"t": "21:45", "e": "CTE", "m": "Roadworks before Braddell Rd. Heavy traffic."}
        ]
        for inc in incs:
            st.markdown(f'<div class="incident-box"><b>[{inc["t"]}] {inc["e"]}</b>: {inc["m"]}</div>', unsafe_allow_html=True)

    # 3. Rail & Weather
    with st.expander("🚆 Rail & Weather", expanded=True):
        r1, r2 = st.columns(2)
        r1.write("MRT: EWL ✅ | NSL ✅ | CCL ⚠️")
        r2.info("Weather: Partly Cloudy. 28°C")

with tab3:
    st.header("🧪 PMT Prediction")
    target = st.selectbox("Predict:", ["USD/SGD", "STI Index", "4D"])
    X = np.array(range(30)).reshape(-1, 1)
    y = np.linspace(100, 110, 30) + np.random.normal(0, 1, 30)
    model = LinearRegression().fit(X, y)
    st.metric(f"ML Prediction", f"{model.predict([[31]])[0]:.2f}")
    st.line_chart(y)

st.caption(f"Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} | ID: gold 10")
