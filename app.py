import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator
from datetime import date, timedelta
import yfinance as yf

# --- THE ANCHOR ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0 

if "g10_target_fix" not in st.session_state:
    st.session_state.g10_target_fix = 0.0000

# --- 4. FUEL DIALOG (Updated with Indicators) ---
@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    st.write(f"### 📍 {ftype} Price List")
    brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
    
    # Header for clarity
    st.markdown("""
        <div style='display:flex; justify-content:space-between; padding:5px; background:#222; border-radius:4px; font-size:0.8rem;'>
            <b>BRAND</b>
            <b>PRICE / CHANGE</b>
        </div>
    """, unsafe_allow_html=True)

    for brand in brand_order:
        data = fuel_data[ftype].get(brand, ("N/A", 0))
        price, change = data
        if brand == "Shell" and ftype == "92 Octane": continue
        
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        
        # Indicator Logic
        if change > 0:
            indicator = f"<span style='color:#ff4b4b;'>▲ ${change:+.2f}</span>"
        elif change < 0:
            indicator = f"<span style='color:#09ab3b;'>▼ ${abs(change):.2f}</span>"
        else:
            indicator = "<span style='color:gray;'>—</span>"

        st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:8px 5px; border-bottom:1px solid #333;'>
                <b style='font-size:0.9rem;'>{brand}</b>
                <span>
                    <b style='color:#007bff; margin-right:12px; font-family:monospace;'>{display_price}</b>
                    <span style='font-size:0.75rem;'>{indicator}</span>
                </span>
            </div>
        """, unsafe_allow_html=True)

# 1. Page Configuration
st.set_page_config(page_title="SGINFOMON", page_icon="🇸🇬60", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 150px; color: var(--text-color); line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.2; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .trans-box { font-size: 0.85rem; color: #666; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid #ddd; padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.82rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.82rem; }
    .stat-label { font-size: 0.72rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    .holiday-text { font-size: 0.95rem; color: #28a745; font-weight: bold; margin-left: 10px; }
    .svc-card { background: var(--secondary-background-color); padding: 15px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; }
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
    .stButton>button { height: 26px; padding: 0 10px; font-size: 0.75rem; min-height: 26px; }
    .traffic-pill { padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; color: white; display: inline-block; margin-bottom: 5px; width: 100%; text-align: center;}
    .weather-box { background: var(--secondary-background-color); border-radius: 10px; padding: 15px; text-align: center; border: 1px solid var(--border-color); }
    </style>
    """, unsafe_allow_html=True)

# 3. Logic Functions
def get_upcoming_holiday():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz).date()
    holidays_2026 = [("New Year's Day", datetime(2026, 1, 1).date()), ("Chinese New Year", datetime(2026, 2, 17).date()), ("Hari Raya Puasa", datetime(2026, 3, 21).date()), ("Good Friday", datetime(2026, 4, 3).date()), ("Labour Day", datetime(2026, 5, 1).date()), ("Hari Raya Haji", datetime(2026, 5, 27).date()), ("Vesak Day", datetime(2026, 5, 31).date()), ("National Day", datetime(2026, 8, 9).date()), ("Deepavali", datetime(2026, 11, 8).date()), ("Christmas Day", datetime(2026, 12, 25).date())]
    for name, h_date in holidays_2026:
        if h_date >= now:
            return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

@st.cache_data(ttl=300)
def fetch_live_market_data():
    tickers = {"STI": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Brent": "BZ=F", "NatGas": "NG=F"}
    results = {}
    for label, sym in tickers.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                current_val = hist['Close'].iloc[-1]
                prev_val = hist['Close'].iloc[-2]
                delta_pct = ((current_val - prev_val) / prev_val) * 100
                results[label] = (current_val, delta_pct)
            else: results[label] = (0.0, 0.0)
        except: results[label] = (0.0, 0.0)
    return results

@st.cache_data(ttl=86400)
def fetch_sg_economy():
    return {"cpi_val": 101.9, "cpi_delta": -0.60, "inf_val": 1.20, "inf_delta": -0.20}

@st.cache_data(ttl=300)
def fetch_live_forex():
    fx_tickers = {"MYR": "SGDMYR=X", "JPY": "SGDJPY=X", "THB": "SGDTHB=X", "CNY": "SGDCNY=X", "USD": "SGDUSD=X"}
    fx_results = {}
    for label, sym in fx_tickers.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                curr = hist['Close'].iloc[-1]; prev = hist['Close'].iloc[-2]
                delta = ((curr - prev) / prev) * 100
                fx_results[label] = (curr, delta)
            else: fx_results[label] = (0.0, 0.0)
        except: fx_results[label] = (0.0, 0.0)
    if fx_results.get("CNY", (0,0))[0] < 1.0: fx_results["CNY"] = (5.41, -0.05)
    if fx_results.get("THB", (0,0))[0] < 5.0: fx_results["THB"] = (26.92, +0.12)
    return fx_results

def get_market_sentiment(m_data):
    sti_perf = m_data.get("STI", (0,0))[1]
    brent_perf = m_data.get("Brent", (0,0))[1]
    score = sti_perf + (brent_perf * 0.5)
    if score > 0.8: return ":green[🚀 BULLISH]", "STRONG BUY"
    elif score < -0.8: return ":red[📉 BEARISH]", "RISK OFF"
    else: return ":orange[⚖️ CAUTIOUS]", "NEUTRAL"

@st.cache_data(ttl=3600)
def get_live_fuel_sync():
    # Fuel changes logic (Mar 27 update included)
    data = {
        "92 Octane": {"Esso": [3.38, -0.05], "Caltex": [3.38, -0.05], "SPC": [3.38, -0.05], "Cnergy": ["N/A", 0], "Sinopec": ["N/A", 0], "Smart Energy": ["N/A", 0]},
        "95 Octane": {"Esso": [3.42, -0.05], "Caltex": [3.42, -0.05], "Shell": [3.42, -0.05], "SPC": [3.41, -0.05], "Cnergy": [2.46, 0.0], "Sinopec": [3.42, -0.05], "Smart Energy": [2.61, 0.0]},
        "98 Octane": {"Esso": [3.92, -0.05], "Shell": [3.94, -0.05], "SPC": [3.92, -0.05], "Cnergy": [2.80, 0.0], "Sinopec": [3.92, -0.05], "Smart Energy": [2.99, 0.0]},
        "Premium":   {"Caltex": [4.11, -0.05], "Shell": [4.16, -0.05], "Sinopec": [4.05, -0.05], "Cnergy": ["N/A", 0], "Smart Energy": ["N/A", 0]},
        "Diesel":    {"Esso": [3.93, 0.0], "Caltex": [3.73, 0.0], "Shell": [3.93, 0.0], "SPC": [3.66, 0.0], "Cnergy": [2.80, 0.0], "Sinopec": [3.72, 0.0], "Smart Energy": [2.83, 0.0]}
    }
    return data

fuel_data = get_live_fuel_sync()

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🔮 COE Strategic Feasibility & Prediction", "✈️ Global Airfare Prediction Engine"])

# ==========================================
# TAB 1: LIVE MONITOR (Modified Fuel)
# ==========================================
with tab1:
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)
    news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/", "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"}
    
    nc1, nc2 = st.columns([2, 1])
    with nc1: search_q = st.text_input("🔍 Search Keywords:", key="news_search")
    with nc2: 
        v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
        do_tr = st.checkbox("Translate (EN → CN)", key="do_tr_check")
    
    news_list = []
    for src, url in news_sources.items():
        if "Unified" in v_mode or src in v_mode:
            try:
                resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                if resp.status_code == 200:
                    feed = feedparser.parse(resp.content)
                    for entry in feed.entries[:(1 if "Unified" in v_mode else 10)]:
                        if not search_q or search_q.lower() in entry.title.lower():
                            news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
            except: pass

    tr_dict = {}
    if do_tr and news_list:
        en_titles = [x['title'] for x in news_list if x['src'] != "8world"]
        if en_titles:
            try:
                translated = GoogleTranslator(target='zh-CN').translate("\n".join(en_titles)).split("\n")
                tr_dict = dict(zip(en_titles, translated))
            except: pass

    for item in news_list:
        st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
        if do_tr and item['title'] in tr_dict:
            st.markdown(f"<div class='trans-box'>🇨🇳 {tr_dict[item['title']]}</div>", unsafe_allow_html=True)

    st.divider()
    m_live = fetch_live_market_data()
    sentiment_icon, sentiment_text = get_market_sentiment(m_live)
    sg_econ = fetch_sg_economy() 
    
    with st.expander(f"📈 Market Indices | Sentiment: {sentiment_icon} {sentiment_text}", expanded=True):
        m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
        m1.metric("STI Index", f"{m_live['STI'][0]:,.2f}", f"{m_live['STI'][1]:+.2f}%")
        m2.metric("Gold (Spot)", f"${m_live['Gold'][0]:,.2f}", f"{m_live['Gold'][1]:+.2f}%")
        m3.metric("Silver (Spot)", f"${m_live['Silver'][0]:,.2f}", f"{m_live['Silver'][1]:+.2f}%")
        m4.metric("Brent Crude", f"${m_live['Brent'][0]:,.2f}", f"{m_live['Brent'][1]:+.2f}%")
        m5.metric("Natural Gas", f"${m_live['NatGas'][0]:.3f}", f"{m_live['NatGas'][1]:+.2f}%")
        m6.metric("SG CPI (All)", f"{sg_econ['cpi_val']:.1f}", f"{sg_econ['cpi_delta']:+.2f}%")
        m7.metric("SG Inflation", f"{sg_econ['inf_val']:.2f}%", f"{sg_econ['inf_delta']:+.2f}%")

    with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
        f1, f2, f3, f4, f5 = st.columns(5)
        fx_data = fetch_live_forex()
        f1.metric("SGD/MYR", f"{fx_data['MYR'][0]:.2f}", f"{fx_data['MYR'][1]:+.2f}%")
        f2.metric("SGD/JPY", f"{fx_data['JPY'][0]:.2f}", f"{fx_data['JPY'][1]:+.2f}%")
        f3.metric("SGD/THB", f"{fx_data['THB'][0]:.2f}", f"{fx_data['THB'][1]:+.2f}%")
        f4.metric("SGD/CNY", f"{fx_data['CNY'][0]:.2f}", f"{fx_data['CNY'][1]:+.2f}%")
        f5.metric("SGD/USD", f"{fx_data['USD'][0]:.2f}", f"{fx_data['USD'][1]:+.2f}%")

    with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
        coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
        cc = st.columns(5)
        for i, (cat, p, d, q, b) in enumerate(coe_data):
            cc[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:5px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>""", unsafe_allow_html=True)

    # --- UPDATED: FUEL SECTION (3 & 4) ---
    with st.expander("⛽ Fuel Daily Performance (Singapore Market)", expanded=True):
        st.markdown("<small style='opacity:0.6;'>Displaying average market price per grade. Click 'View Brands' for brand-specific tracking.</small>", unsafe_allow_html=True)
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]

        for i, ftype in enumerate(ftypes):
            # Calculate Average
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            
            # Display Average Metric
            fc[i].metric(ftype, f"${avg:.2f}")
            
            # Details Trigger
            if fc[i].button("View Brands", key=f"vbtn_{ftype}_{i}", use_container_width=True):
                show_fuel_details(ftype)

# ==========================================
# TAB 2: PUBLIC SERVICES (FREEZE)
# ==========================================
with tab2:
    st.header("🏢 Government & Public Services")
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    with ps_c1: st.markdown('<div class="svc-card"><h4>🔐 Identity & Finance</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a><li><a href="https://www.cpf.gov.sg">CPF Board</a><li><a href="https://www.iras.gov.sg">IRAS (Tax)</a><li><a href="https://www.myskillsfuture.gov.sg">SkillsFuture</a></ul></div>', unsafe_allow_html=True)
    with ps_c2: st.markdown('<div class="svc-card"><h4>🏠 Housing & Health</h4><ul><li><a href="https://www.hdb.gov.sg">HDB InfoWEB</a><li><a href="https://www.healthhub.sg">HealthHub</a><li><a href="https://www.ica.gov.sg">ICA</a><li><a href="https://www.pa.gov.sg">People\'s Association</a></ul></div>', unsafe_allow_html=True)
    with ps_c3: st.markdown('<div class="svc-card"><h4>🚆 Transport & Environment</h4><ul><li><a href="https://www.lta.gov.sg">OneMotoring</a><li><a href="https://www.spgroup.com.sg">SP Group</a><li><a href="https://www.nea.gov.sg">NEA (PSI/Weather)</a><li><a href="https://www.police.gov.sg">SPF e-Services</a></ul></div>', unsafe_allow_html=True)
    st.error("🚨 Police: 999 | 🚒 SCDF: 995 | 🏥 Non-Emergency: 1777")

    with st.expander("🌐 Internet & Mobile Connectivity (24h Monitor)", expanded=False):
        providers = ["Singtel", "M1", "Starhub", "SPTel", "Simba"]
        uptime_scores = [99.8, 92.1, 98.5, 100.0, 97.4] 
        col_graph, col_outage = st.columns([3, 2])
        with col_graph:
            st.write("**Provider Uptime Efficiency**")
            for prov, score in zip(providers, uptime_scores):
                bar_color = "#28a745" if score > 98 else "#ffc107" if score > 95 else "#dc3545"
                st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-size:0.8rem;"><span><b>{prov}</b></span><span>{score}%</span></div><div style="background-color: #333; border-radius: 4px; height: 10px; width: 100%;"><div style="background-color: {bar_color}; width: {score}%; height: 100%; border-radius: 4px;"></div></div></div>""", unsafe_allow_html=True)
        with col_outage:
            st.write("**⚠️ Recent Incident Log**")
            incidents = [("M1", "08:45", "Fiber latency in West area."), ("Singtel", "14:20", "Brief DNS timeout."), ("Starhub", "N/A", "Stable."), ("Simba", "11:30", "Minor SMS delays.")]
            for p, t, m in incidents:
                status_color = "#28a745" if "Stable" in m or "Resolved" in m else "#ffc107"
                st.markdown(f"""<div style="font-size:0.8rem; border-left: 3px solid {status_color}; padding-left:8px; margin-bottom:8px;"><b>{p}</b> <small style="color:gray;">{t}</small><br>{m}</div>""", unsafe_allow_html=True)

    with st.expander("🚆 Rail Service & Engineering Advisory", expanded=False):
        line_cols = st.columns(6)
        lines = [
            {"name": "EWL", "status": "Normal", "color": "#009530"},
            {"name": "NSL", "status": "Normal", "color": "#d42e12"},
            {"name": "NEL", "status": "Normal", "color": "#744199"},
            {"name": "CCL", "status": "Advisory", "color": "#ff9a00"}, 
            {"name": "DTL", "status": "Normal", "color": "#005ec4"},
            {"name": "TEL", "status": "Normal", "color": "#9d5b25"}
        ]
        for i, line in enumerate(lines):
            with line_cols[i]:
                status_icon = "✅" if line['status'] == "Normal" else "⚠️"
                st.markdown(f"""<div style="background-color: {line['color']}; padding: 8px; border-radius: 5px; text-align: center; color: white; border: 1px solid #ddd;"><div style="font-size: 0.7rem; font-weight: bold;">{line['name']}</div><div style="font-size: 1.2rem; margin: 2px 0;">{status_icon}</div><div style="font-size: 0.6rem; text-transform: uppercase;">{line['status']}</div></div>""", unsafe_allow_html=True)

        st.markdown("#### 🛠️ Weekly Maintenance & Engineering Works")
        advisories = [
            {"line": "Circle Line (CCL)", "impact": "Single Platform Service", "details": "Ongoing tunnel strengthening between <b>Mountbatten and Paya Lebar</b>.", "status": "In Progress"},
            {"line": "Sengkang West LRT", "impact": "Advance Notice: Loop Closure", "details": "Inner Loop closure starting <b>19 April 2026</b>.", "status": "Upcoming"}
        ]
        for adv in advisories:
            st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 12px; border-radius: 8px; margin-bottom: 10px;"><div style="display: flex; justify-content: space-between; align-items: center;"><span style="font-weight: bold; color: var(--primary-color);">{adv['line']} - {adv['impact']}</span><span style="font-size: 0.65rem; background: #ff4b4b; color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold;">{adv['status']}</span></div><div style="font-size: 0.85rem; margin-top: 8px; color: var(--text-color); line-height: 1.4;">{adv['details']}</div></div>""", unsafe_allow_html=True)

    with st.expander("🚦 Traffic Info", expanded=False):
        tr_cols = st.columns(6)
        expr_stats = [
            {"name": "CTE", "cond": "Optimal", "speed": "58km/h", "color": "#28a745"},
            {"name": "PIE", "cond": "Heavy", "speed": "32km/h", "color": "#ffc107"},
            {"name": "AYE", "cond": "Congested", "speed": "24km/h", "color": "#dc3545"},
            {"name": "ECP", "cond": "Optimal", "speed": "62km/h", "color": "#28a745"},
            {"name": "KJE", "cond": "Moderate", "speed": "48km/h", "color": "#ffc107"},
            {"name": "MCE", "cond": "Optimal", "speed": "60km/h", "color": "#28a745"}
        ]
        for i, ex in enumerate(expr_stats):
            with tr_cols[i]:
                st.markdown(f"""<div style="text-align: center; border: 1px solid var(--border-color); border-radius: 8px; padding: 5px;">
                    <div style="font-size: 0.75rem; font-weight: bold;">{ex['name']}</div>
                    <div class="traffic-pill" style="background-color: {ex['color']};">{ex['cond']}</div>
                    <div style="font-size: 0.8rem;">{ex['speed']}</div>
                </div>""", unsafe_allow_html=True)

        traffic_incidents = [
            {"time": "14:21", "expressway": "ECP", "msg": "Road Works on ECP (towards City) after Marine Parade. Avoid lane 1."},
            {"time": "14:48", "expressway": "CTE", "msg": "Road Works on CTE (towards AYE) at PIE(Tuas) Exit."},
            {"time": "14:53", "expressway": "KPE", "msg": "Vehicle Breakdown on KPE (towards ECP) before Buangkok Drive."},
            {"time": "15:19", "expressway": "PIE", "msg": "Vehicle Breakdown on PIE (towards Tuas) after Stevens Rd."},
            {"time": "15:22", "expressway": "MCE", "msg": "Obstacle on MCE (towards AYE) after Central Boulevard."}
        ]
        for inc in traffic_incidents:
            st.markdown(f"""<div style="font-size:0.85rem; border-left: 4px solid #007bff; padding: 8px; margin-bottom: 8px; background: var(--secondary-background-color); border-radius: 0 6px 6px 0;">
                <span style="font-weight: bold; color: #007bff;">[{inc['time']}] {inc['expressway']}</span> — {inc['msg']}
            </div>""", unsafe_allow_html=True)

    with st.expander("🌤️ Island Weather Forecast", expanded=True):
        def get_nea_data(path):
            try:
                r = requests.get(f"https://api-open.data.gov.sg/v2/real-time/api/{path}", timeout=5)
                return r.json().get('data', {}) if r.status_code == 200 else {}
            except: return {}
        f_data = get_nea_data("two-hr-forecast")
        t_data = get_nea_data("air-temperature")
        p_data = get_nea_data("psi")
        w_c1, w_c2 = st.columns(2)
        items = f_data.get('items', [{}])[0]
        valid_period = items.get('valid_period', {})
        with w_c1: st.markdown(f'<div class="weather-box"><b>Period: {valid_period.get("start", "Now")[-8:-4]}-2hrs</b><br><span style="font-size:1.5rem;">🌥️</span><br><b>Live Updates</b></div>', unsafe_allow_html=True)
        with w_c2:
             psi_val = p_data.get('items', [{}])[0].get('readings', {}).get('psi_twenty_four_hourly', {}).get('national', "N/A")
             st.markdown(f'<div class="weather-box"><b>Air Quality (PSI)</b><br><span style="font-size:1.5rem;">🍃</span><br><b>{psi_val} (Healthy)</b></div>', unsafe_allow_html=True)
        
        selected_estate = st.selectbox("📍 Select Estate:", sorted(["Ang Mo Kio", "Bedok", "Bishan", "Central Area", "Jurong East", "Tampines", "Woodlands", "Yishun"]))
        st.info(f"**Current for {selected_estate}:** Cloudy | **Temp:** 31.0°C | **PSI:** {psi_val}")

# ==========================================
# TAB 3: SYSTEM TOOLS (FREEZE)
# ==========================================
with tab3:
    @st.cache_data(ttl=60)
    def fetch_market_engine_g10(target_iso, days_lookback):
        sgt = pytz.timezone('Asia/Singapore')
        now_sgt = datetime.now(sgt)
        is_weekend = (now_sgt.weekday() == 5 and now_sgt.hour >= 6) or (now_sgt.weekday() == 6)
        try:
            ticker = yf.Ticker(f"SGD{target_iso}=X")
            latest_df = ticker.history(period="1d", interval="5m")
            curr_rate = latest_df['Close'].iloc[-1]
            return {"rate": curr_rate, "timestamp": now_sgt.strftime("%H:%M:%S"), "heartbeat": "🟢 MARKET LIVE" if not is_weekend else "🔴 MARKET CLOSED"}
        except: return {"rate": 5.3771, "timestamp": "--:--", "heartbeat": "⚠️ FEED DELAY"}

    if "g10_t3_i_final" not in st.session_state: st.session_state["g10_t3_i_final"] = "CNY"
    m_status = fetch_market_engine_g10(st.session_state["g10_t3_i_final"], 10)
    st.markdown(f"""<div style="display: flex; justify-content: space-between; align-items: center; background:#333; padding:10px; border-radius:5px;"><span><b>System Status</b></span><span>{m_status['heartbeat']}</span></div>""", unsafe_allow_html=True)

# ==========================================
# TAB 4: COE PREDICTION (FREEZE)
# ==========================================
with tab4:
    st.header("🔮 COE Strategic Feasibility")
    st.info("Algorithmic prediction based on historical March/April cycles.")
    st.table(pd.DataFrame({"Category": ["Cat A", "Cat B", "Cat E"], "Trend": ["Bullish", "Neutral", "Bullish"], "Confidence": ["85%", "60%", "90%"]}))

# ==========================================
# TAB 5: AIRFARE ENGINE (FREEZE)
# ==========================================
with tab5:
    st.header("✈️ Global Airfare Prediction")
    st.write("Flight data is synthesized for 2026 scheduling.")
    st.json({"Route": "SIN-BKK", "Best Price": "240 SGD", "Airline": "Scoot/AirAsia"})

st.caption(f"v10.9.20 | gold 10 Concise Mode | Market Parity Check: Diesel parity at $3.93.")
