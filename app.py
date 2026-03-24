import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression 
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# SG INFO MONITOR - Version 11.0.8 (gold 10 - Fixed Syntax & Full Logic)

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 11.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_gold10_v8")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 150_px; color: var(--text-color); line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.2; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .trans-box { font-size: 0.85rem; color: #666; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .traffic-pill { padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; color: white; display: inline-block; margin-bottom: 5px; width: 100%; text-align: center;}
    .incident-box { font-size: 0.82rem; border-left: 4px solid #ff4b4b; padding: 8px; margin-bottom: 6px; background: rgba(255, 75, 75, 0.05); border-radius: 0 6px 6px 0; border: 1px solid var(--border-color); border-left-width: 4px; }
    .svc-card { background: var(--secondary-background-color); padding: 15px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 3. Logic Functions
def get_upcoming_holiday():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz).date()
    holidays_2026 = [("New Year's Day", datetime(2026, 1, 1).date()), ("Chinese New Year", datetime(2026, 2, 17).date()), ("Hari Raya Puasa", datetime(2026, 3, 21).date()), ("Good Friday", datetime(2026, 4, 3).date()), ("Labour Day", datetime(2026, 5, 1).date()), ("Hari Raya Haji", datetime(2026, 5, 27).date()), ("Vesak Day", datetime(2026, 5, 31).date()), ("National Day", datetime(2026, 8, 9).date()), ("Deepavali", datetime(2026, 11, 8).date()), ("Christmas Day", datetime(2026, 12, 25).date())]
    for name, h_date in holidays_2026:
        if h_date >= now: return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32), "Cnergy": ("N/A", 0), "Sinopec": ("N/A", 0), "Smart Energy": ("N/A", 0)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02), "Cnergy": (2.46, 0.05), "Sinopec": (3.47, 0.04), "Smart Energy": (2.61, 0.05)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05), "Cnergy": (2.80, 0.05), "Sinopec": (3.97, 0.05), "Smart Energy": (2.99, -0.12)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05), "Sinopec": (4.10, 0.20), "Cnergy": ("N/A", 0), "Smart Energy": ("N/A", 0)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07), "Cnergy": (2.80, 0), "Sinopec": (3.72, 0.10), "Smart Energy": (2.83, 0.02)}
}

@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List")
    brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
    for brand in brand_order:
        data = fuel_data[ftype].get(brand, ("N/A", 0))
        price, change = data
        if brand == "Shell" and ftype == "92 Octane": continue
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff; margin-right:8px;'>{display_price}</b><span class='{'up' if change > 0 else 'down'}'>({change:+.2f})</span></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9")
tab1, tab2, tab3 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🧪 PMT - Prediction Model Trial"])

with tab1:
    # 1. Clocks
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span style="color:#28a745; font-size:0.9rem; margin-left:10px;">{holiday_info}</span>', unsafe_allow_html=True)
    
    # News Section
    news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"}
    nc1, nc2 = st.columns([2, 1])
    with nc1: search_q = st.text_input("🔍 Search Keywords:", key="news_search")
    with nc2: do_tr = st.checkbox("Translate (EN → CN)", key="do_tr_check")
    
    for src, url in news_sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                if not search_q or search_q.lower() in entry.title.lower():
                    st.write(f"<span class='news-tag'>{src}</span> **[{entry.title}]({entry.link})**", unsafe_allow_html=True)
        except: pass

    st.divider()
    with st.expander("📈 Markets & COE", expanded=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STI Index", "4,841.30", "-2.20%")
        m2.metric("SG CPI Index", "116.4", "+0.2%")
        m3.metric("Gold", "$4,391", "+1.66%")
        m4.metric("USD/SGD", "1.3361", "-0.22%")

    with st.expander("⛽ Fuel Prices (Avg)", expanded=True):
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
        for i, ftype in enumerate(ftypes):
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if fc[i].button("Details", key=f"fbtn_v8_{ftype}"): show_fuel_details(ftype)

with tab2:
    st.header("🏢 Government & Public Services")
    
    # --- 1. Service Links & Network ---
    sc1, sc2 = st.columns([1, 1])
    with sc1:
        st.markdown('<div class="svc-card"><h4>🔐 Quick Access</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a><li><a href="https://www.cpf.gov.sg">CPF Board</a><li><a href="https://www.hdb.gov.sg">HDB InfoWEB</a></ul></div>', unsafe_allow_html=True)
    with sc2:
        st.markdown('**🌐 Network Uptime**')
        st.caption("Singtel: 99.8% | M1: 92.1% | Starhub: 98.5%")
        st.progress(0.98)

    # --- 2. Unified Expressway & Incident Section (FIXED SYNTAX) ---
    with st.expander("🛣️ Expressway Traffic & Incident Command", expanded=True):
        st.markdown("<b>🚦 Current Flow Speeds</b>", unsafe_allow_html=True)
        t_cols = st.columns(6)
        ex_data = [{"n": "CTE", "s": "58km/h", "c": "#28a745"}, {"n": "PIE", "s": "32km/h", "c": "#ffc107"}, {"n": "AYE", "s": "24km/h", "c": "#dc3545"}, {"n": "ECP", "s": "62km/h", "c": "#28a745"}, {"n": "KJE", "s": "48km/h", "c": "#ffc107"}, {"n": "MCE", "s": "60km/h", "c": "#28a745"}]
        for i, ex in enumerate(ex_data):
            with t_cols[i]:
                st.markdown(f"""<div style="text-align:center; border:1px solid #444; border-radius:8px; padding:5px;"><b>{ex['n']}</b><div class="traffic-pill" style="background-color:{ex['c']};">{ex['s']}</div></div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("<b>⚠️ Road Incident Log (Latest at Top)</b>", unsafe_allow_html=True)
        incidents = [
            {"t": "22:15", "e": "KPE", "m": "Accident in KPE Tunnel (towards TPE) after Bartley Rd East Exit. Avoid lane 2."},
            {"t": "22:02", "e": "PIE", "m": "Vehicle Breakdown on PIE (towards Changi) after Bedok North Exit."},
            {"t": "21:45", "e": "CTE", "m": "Roadworks on CTE (towards AYE) before Braddell Rd. Heavy traffic expected."},
            {"t": "21:10", "e": "AYE", "m": "Obstacle on AYE (towards Tuas) after Clementi Ave 6 Exit. Lane 3 blocked."}
        ]
        for inc in incidents:
            st.markdown(f"""<div class="incident-box"><b>[{inc['t']}] {inc['e']}</b> — {inc['m']}</div>""", unsafe_allow_html=True)

    # --- 3. Rail & Weather (RESTORED) ---
    with st.expander("🚆 Rail & 🌤️ Weather", expanded=True):
        rc1, rc2 = st.columns(2)
        with rc1:
            st.write("**Rail Status**")
            st.write("EWL: ✅ | NSL: ✅ | CCL: ⚠️ Works")
        with rc2:
            st.write("**NEA Weather**")
            st.info("Partly Cloudy. Temp: 28°C - 32°C")

with tab3:
    # --- PMT - Prediction Model Trial ---
    st.header("🧪 PMT - Machine Learning Prediction")
    target = st.selectbox("Target:", ["Currency (USD/SGD)", "Stock Market (STI)", "Singapore 4D"])
    
    days = 30
    X = np.array(range(days)).reshape(-1, 1)
    if target == "Currency (USD/SGD)":
        y = np.linspace(1.30, 1.27, days) + np.random.normal(0, 0.002, days)
        unit = "SGD"
    elif target == "Stock Market (STI)":
        y = np.linspace(4500, 4841, days) + np.random.normal(0, 20, days)
        unit = "Points"
    else:
        y = np.random.randint(0, 9999, days)
        unit = "Winning No."

    model = LinearRegression().fit(X, y)
    pred = model.predict(np.array([[days + 1]]))[0]
    
    cl1, cl2 = st.columns(2)
    with cl1:
        val = f"{pred:.4f}" if "Currency" in target else f"{int(pred)}"
        st.metric(f"ML Predicted {target}", f"{val} {unit}")
    with cl2:
        st.line_chart(pd.DataFrame({'Historical': y, 'Trend': model.predict(X)}))

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT | ID: gold 10")
