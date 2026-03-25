import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator
from datetime import date, timedelta

# SG INFO MONITOR - Weather & Traffic Update 10.9.3

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 150_px; color: var(--text-color); line-height: 1.1; }
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

# NEW: Reliable NEA Data Fetcher
def fetch_nea_live(endpoint):
    try:
        url = f"https://api-open.data.gov.sg/v2/real-time/api/{endpoint}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', {}).get('items', [{}])[0]
    except: return None
    return None

# --- NEW: LIVE MARKET ENGINE (gold 10) ---
@st.cache_data(ttl=300)
def fetch_live_market_data():
    """Fetches STI, Gold, Silver, Brent, and Nat Gas from Yahoo Finance"""
    tickers = {
        "STI": "^STI", 
        "Gold": "GC=F", 
        "Silver": "SI=F", 
        "Brent": "BZ=F", 
        "NatGas": "NG=F"
    }
    results = {}
    for label, sym in tickers.items():
        try:
            ticker = yf.Ticker(sym)
            # Fetch 2 days to calculate delta even if market is currently closed
            hist = ticker.history(period="2d")
            if not hist.empty:
                current_val = hist['Close'].iloc[-1]
                prev_val = hist['Close'].iloc[-2]
                delta_pct = ((current_val - prev_val) / prev_val) * 100
                results[label] = (current_val, delta_pct)
            else:
                results[label] = (0.0, 0.0)
        except:
            results[label] = (0.0, 0.0)
    return results

# --- NEW: SENTIMENT LOGIC ---
def get_market_sentiment(m_data):
    # Aggregating signals from STI and Brent (Proxy for global/local health)
    sti_perf = m_data.get("STI", (0,0))[1]
    brent_perf = m_data.get("Brent", (0,0))[1]
    
    score = sti_perf + (brent_perf * 0.5)
    
    if score > 0.8: return ":green[🚀 BULLISH]", "STRONG BUY"
    elif score < -0.8: return ":red[📉 BEARISH]", "RISK OFF"
    else: return ":orange[⚖️ CAUTIOUS]", "NEUTRAL"

# [Logic Functions for Holidays and Fuel remain as per original code]

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

# UPDATED: We now have 3 tabs defined here
tab1, tab2, tab3,tab4, tab5 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🔮 COE Strategic Feasibility & Prediction", "✈️ Global Airfare Prediction Engine"])

# ==========================================
# TAB 1: LIVE MONITOR (Your EXACT Original)
# ==========================================
with tab1:
    # 1. Clocks
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    
    # 2. News & Holidays
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)
    news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/", "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    nc1, nc2 = st.columns([2, 1])
    with nc1: search_q = st.text_input("🔍 Search Keywords:", key="news_search")
    with nc2: 
        v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
        do_tr = st.checkbox("Translate (EN → CN)", key="do_tr_check")
    
    news_list = []
    for src, url in news_sources.items():
        if "Unified" in v_mode or src in v_mode:
            try:
                resp = requests.get(url, headers=headers, timeout=5)
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

    # 3. Markets & Commodities
# 3. Markets & Commodities (DYNAMIC UPDATE)
    m_live = fetch_live_market_data()
    sentiment_icon, sentiment_text = get_market_sentiment(m_live)
    
    with st.expander(f"📈 Market Indices | Sentiment: {sentiment_icon} {sentiment_text}", expanded=True):
        m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
        
        # STI Logic: Shows Live if open, Last Close if closed
        m1.metric("STI Index", 
                  f"{m_live['STI'][0]:,.2f}", 
                  f"{m_live['STI'][1]:+.2f}%")
        
        m2.metric("Gold (Spot)", 
                  f"${m_live['Gold'][0]:,.2f}", 
                  f"{m_live['Gold'][1]:+.2f}%")
        
        m3.metric("Silver (Spot)", 
                  f"${m_live['Silver'][0]:,.2f}", 
                  f"{m_live['Silver'][1]:+.2f}%")
        
        m4.metric("Brent Crude", 
                  f"${m_live['Brent'][0]:,.2f}", 
                  f"{m_live['Brent'][1]:+.2f}%")
        
        m5.metric("Natural Gas", 
                  f"${m_live['NatGas'][0]:.3f}", 
                  f"{m_live['NatGas'][1]:+.2f}%")
        
        # Static Macro remain for reference
        m6.metric("SG CPI (All)", "100.7", "-0.20%")
        m7.metric("SG Inflation", "1.40%", "+0.40%")

    with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
        f1, f2, f3, f4, f5 = st.columns(5)
        f1.metric("SGD/MYR", "3.4412", "+0.12%")
        f2.metric("SGD/JPY", "118.55", "-0.43%")
        f3.metric("SGD/THB", "26.85", "+0.15%")
        f4.metric("SGD/CNY", "5.3975", "-0.07%")
        f5.metric("SGD/USD", "0.7480", "-0.22%")

    # 4. COE Bidding
    with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
        coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
        cc = st.columns(5)
        for i, (cat, p, d, q, b) in enumerate(coe_data):
            cc[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:5px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>""", unsafe_allow_html=True)

    # 5. Fuel Prices
    with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
        for i, ftype in enumerate(ftypes):
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if fc[i].button("Details", key=f"fbtn_109_{ftype}"): show_fuel_details(ftype)


# ==========================================
# TAB 2: PUBLIC SERVICES (Your EXACT Original)
# ==========================================
with tab2:
    # --- 1. Government & Public Services ---
    st.header("🏢 Government & Public Services")
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    with ps_c1: st.markdown('<div class="svc-card"><h4>🔐 Identity & Finance</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a><li><a href="https://www.cpf.gov.sg">CPF Board</a><li><a href="https://www.iras.gov.sg">IRAS (Tax)</a><li><a href="https://www.myskillsfuture.gov.sg">SkillsFuture</a></ul></div>', unsafe_allow_html=True)
    with ps_c2: st.markdown('<div class="svc-card"><h4>🏠 Housing & Health</h4><ul><li><a href="https://www.hdb.gov.sg">HDB InfoWEB</a><li><a href="https://www.healthhub.sg">HealthHub</a><li><a href="https://www.ica.gov.sg">ICA</a><li><a href="https://www.pa.gov.sg">People\'s Association</a></ul></div>', unsafe_allow_html=True)
    with ps_c3: st.markdown('<div class="svc-card"><h4>🚆 Transport & Environment</h4><ul><li><a href="https://www.lta.gov.sg">OneMotoring</a><li><a href="https://www.spgroup.com.sg">SP Group</a><li><a href="https://www.nea.gov.sg">NEA (PSI/Weather)</a><li><a href="https://www.police.gov.sg">SPF e-Services</a></ul></div>', unsafe_allow_html=True)
    st.error("🚨 Police: 999 | 🚒 SCDF: 995 | 🏥 Non-Emergency: 1777")

    # --- 2. Network & Connectivity Status ---
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

    # --- 3. Rail Service & Engineering Advisory ---
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

    # --- 4. Traffic Info ---
    with st.expander("🚦 Traffic Info", expanded=False):
        st.markdown("#### 🛣️ Expressway Traffic Condition")
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

        st.markdown("<br>#### ⚠️ Traffic Incidents (Last 60 Mins - FIFO)", unsafe_allow_html=True)
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

    # --- 5. LIVE Island Weather ---
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
        with w_c1:
            st.markdown(f'<div class="weather-box"><b>Period: {valid_period.get("start", "Now")[-8:-4]}-2hrs</b><br><span style="font-size:1.5rem;">🌥️</span><br><b>Live Updates</b></div>', unsafe_allow_html=True)
        with w_c2:
             psi_val = p_data.get('items', [{}])[0].get('readings', {}).get('psi_twenty_four_hourly', {}).get('national', "N/A")
             st.markdown(f'<div class="weather-box"><b>Air Quality (PSI)</b><br><span style="font-size:1.5rem;">🍃</span><br><b>{psi_val} (Healthy)</b></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        estates = ["Ang Mo Kio", "Bedok", "Bishan", "Bukit Batok", "Bukit Merah", "Bukit Panjang", "Bukit Timah", "Central Area", "Choa Chu Kang", "Clementi", "Geylang", "Hougang", "Jurong East", "Jurong West", "Kallang/Whampoa", "Marine Parade", "Pasir Ris", "Punggol", "Queenstown", "Sembawang", "Sengkang", "Serangoon", "Tampines", "Toa Payoh", "Woodlands", "Yishun"]
        selected_estate = st.selectbox("📍 Select Estate / Housing Town:", sorted(estates))
        
        area_forecast = "Cloudy"
        for f in items.get('forecasts', []):
            if f['area'] == selected_estate:
                area_forecast = f['forecast']
                break

        temp_readings = t_data.get('items', [{}])[0].get('readings', [])
        current_temp = temp_readings[0].get('value', 31.0) if temp_readings else 31.0

        st.info(f"**Current for {selected_estate}:** {area_forecast} | **Temp:** {current_temp}°C | **PSI:** {psi_val}")

    st.caption("Data source: LTA MyTransport / SMRT / SBS Transit / NEA Open Data. Refresh every 3 mins.")


# ==========================================
# TAB 3: SYSTEM TOOLS (Safely Appended)
# ==========================================
with tab3:
    st.header("PMT Trial")
    
    col_u1, col_u2 = st.columns([1, 1])

# ==========================================
# TAB 3: SYSTEM TOOLS - Macro & Probability
# ==========================================
with tab3:
    st.header("🎯 Tactical Trade Scheduler")
    
    # 1. DATA ENGINE (Isolated for gold 10)
    @st.cache_data(ttl=300)
    def fetch_market_engine_g10(target_iso, days_lookback):
        try:
            url_latest = f"https://api.frankfurter.app/latest?from=SGD&to={target_iso}"
            res_l = requests.get(url_latest, timeout=5).json()
            curr_rate = res_l['rates'][target_iso]
            
            end_date = datetime.now().date()
            start_date = end_date - pd.Timedelta(days=days_lookback)
            url_hist = f"https://api.frankfurter.app/{start_date}..{end_date}?from=SGD&to={target_iso}"
            res_h = requests.get(url_hist, timeout=5).json()
            
            hist_rates = [v[target_iso] for v in res_h['rates'].values()]
            std_dev = np.std(hist_rates) if len(hist_rates) > 1 else curr_rate * 0.005
            return {"rate": curr_rate, "high": max(hist_rates), "low": min(hist_rates), "std": std_dev}
        except:
            fb = {"CNY": 5.3895, "THB": 25.5533}.get(target_iso, 1.0)
            return {"rate": fb, "high": fb*1.01, "low": fb*0.99, "std": fb*0.005}

    # 2. ROW 1: POLICY | DURATION | MODEL RANGE
    r1_col1, r1_col2, r1_col3 = st.columns([2, 1, 2], vertical_alignment="center")
    
    with r1_col1:
        p_stance = st.radio("MAS Policy Stance:", ["Hawkish", "Neutral", "Dovish"], 
                            horizontal=True, key="g10_t3_p_final")
    
    with r1_col2:
        lookback = st.selectbox("Range:", [5, 10], index=1, format_func=lambda x: f"{x} Days", key="g10_t3_d_final")

    supported_iso = ["CNY", "THB", "JPY", "MYR", "EUR", "USD", "GBP"]
    selected_iso = st.selectbox("Target Currency:", supported_iso, key="g10_t3_i_final", label_visibility="collapsed")
    m_data = fetch_market_engine_g10(selected_iso, lookback)

    with r1_col3:
        st.markdown(f"""
            <div style="display: flex; gap: 8px; justify-content: center;">
                <div style="background: rgba(0,255,127,0.1); padding: 5px; border-radius: 5px; border: 1px solid #00ff7f; width: 100px; text-align:center;">
                    <small>Model High</small><br><strong>{m_data['high']:.4f}</strong>
                </div>
                <div style="background: rgba(255,75,75,0.1); padding: 5px; border-radius: 5px; border: 1px solid #ff4b4b; width: 100px; text-align:center;">
                    <small>Model Low</small><br><strong>{m_data['low']:.4f}</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 3. ROW 2: AMOUNT & TARGET PRICE
    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        t_amt = st.number_input("Amount (SGD):", min_value=0, value=1000, key="g10_t3_a_final")
    with r2_col2:
        u_target = st.number_input("Target Price:", value=m_data['rate']*1.002, format="%.4f", key="g10_t3_t_final")

    # 4. PROBABILITY & ACTION DATE LOGIC
    speed_mult = {"Hawkish": 1.15, "Neutral": 1.0, "Dovish": 0.80}[p_stance]
    price_gap = abs(u_target - m_data['rate'])
    days_req = int(np.ceil(price_gap / (m_data['std'] * speed_mult))) if price_gap > 0 else 0
    action_dt = (datetime.now(pytz.timezone('Asia/Singapore')) + pd.Timedelta(days=days_req)).strftime('%d %b %Y')

    z_score = price_gap / (m_data['std'] * np.sqrt(max(days_req, 1)))
    prob_val = max(5, min(99, 100 * (1 - (z_score / 3))))

    # 5. OUTPUT DISPLAY
    st.markdown("---")
    out_c1, out_c2 = st.columns([1.5, 2])
    with out_c1:
        # ENLARGED FONT FOR ACTION DATE
        st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <span style="font-size: 1.15rem; font-weight: bold; color: #ffffff;">
                    Suggest Action Date: {action_dt}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        # Probability Bar
        p_color = "#00ff7f" if prob_val > 60 else "#ffaa00" if prob_val > 30 else "#ff4b4b"
        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <small>Possibility Rate:</small> <strong>{prob_val:.1f}%</strong>
                <div style="background: #333; height: 8px; border-radius: 4px; width: 100%;">
                    <div style="background: {p_color}; height: 8px; border-radius: 4px; width: {prob_val}%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.metric("Live Market Rate", f"{m_data['rate']:.4f}")

    with out_c2:
        path = np.linspace(m_data['rate'], u_target, 10)
        st.line_chart(pd.DataFrame({"Path": path, "Model High": [m_data['high']]*10, "Model Low": [m_data['low']]*10}), height=180)

    # SINGLE CONSOLIDATED EXECUTION BUTTON
    if st.button("🔒 Confirm Tactical Execution", use_container_width=True, key="g10_t3_exec_final"):
        st.success(f"Execution plan locked for {action_dt}. Target Prob: {prob_val:.1f}%")
        st.success(f"Execution Locked. Target Prob: {prob_val:.1f}%")

# [APPEND IMMEDIATELY AFTER TAB 3 BLOCK]
# ==========================================
# TAB 4: PMT: COE - HYBRID PREDICTION ENGINE
# ==========================================
with tab4:
    # 1. LIVE GROUND DATA (March 2nd 2026 Actuals)
    g10_coe_stats = {
        "Cat A": {"p": 111890, "q": 1264, "b": 1895, "date": "06 Apr 2026"},
        "Cat B": {"p": 115568, "q": 812, "b": 1185, "date": "06 Apr 2026"},
        "Cat C": {"p": 78000, "q": 290, "b": 438, "date": "06 Apr 2026"},
        "Cat D": {"p": 9589, "q": 546, "b": 726, "date": "06 Apr 2026"},
        "Cat E": {"p": 118119, "q": 246, "b": 422, "date": "06 Apr 2026"}
    }

    # 2. USER INTERFACE & INPUT
    st.header("🤖 COE Intelligence & Feasibility")
    p_c1, p_c2, p_c3 = st.columns([1.2, 1.3, 1.5], vertical_alignment="center")
    
    with p_c1:
        v_cat = st.selectbox("Category:", list(g10_coe_stats.keys()), key="g10_t4_vcat")
        u_target = st.number_input("Desired COE ($):", min_value=0, value=0, help="Set to 0 for Model Auto-Prediction", key="g10_t4_target")
    
    # FETCH CONTEXTUAL DATA
    current_mas = st.session_state.get("g10_t3_p_final", "Neutral")
    bq_ratio = g10_coe_stats[v_cat]['b'] / g10_coe_stats[v_cat]['q']
    last_p = g10_coe_stats[v_cat]['p']
    
    with p_c2:
        # Automated Sentiment Slider
        m_sent = st.select_slider(
            "Model Market Sentiments:", 
            options=["Bearish", "Neutral", "Bullish"], 
            value="Bullish" if bq_ratio > 1.5 or "3-week gap" in "Cycle Info" else "Neutral",
            key="g10_t4_sent"
        )
        st.caption(f"BQ Ratio: {bq_ratio:.2f}x | Gap: 3-Weeks (High Demand)")

    with p_c3:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border: 1px solid #444; text-align:center;">
                <small>Latest Settled Price</small><br>
                <strong style="font-size:1.4rem; color:#007bff;">${last_p:,.0f}</strong><br>
                <small>Next: {g10_coe_stats[v_cat]['date']}</small>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 3. CORE LOGIC SWITCH
    if u_target == 0:
        # MODE A: FORMER PREDICTION LOGIC
        st.subheader("📡 Next Bidding Prediction (Automated)")
        s_mult = {"Bearish": 0.97, "Neutral": 1.02, "Bullish": 1.06}[m_sent]
        # Factor in the 3-week selling window (+2% pressure)
        pred_val = last_p * (1 + (bq_ratio - 1.4) * 0.05) * s_mult * 1.02
        p_diff = pred_val - last_p
        
        l_res, r_res = st.columns([2, 1])
        with l_res:
            st.markdown(f"""
                <div style="background: rgba(0,255,127,0.08); padding: 25px; border-radius: 12px; border: 1px solid #00ff7f; text-align: center;">
                    <small>MODEL PROJECTED PRICE</small><br>
                    <span style="font-size: 2.8rem; font-weight: bold; color: #00ff7f;">${pred_val:,.0f}</span><br>
                    <span style="font-size: 1.2rem; color: #00ff7f;">▲ ${p_diff:,.0f} (+{(p_diff/last_p)*100:.1f}%)</span>
                </div>
            """, unsafe_allow_html=True)
        with r_res:
            st.metric("Bidding Volume", f"{g10_coe_stats[v_cat]['b']:,}")
            st.metric("Quota Available", f"{g10_coe_stats[v_cat]['q']:,}")
    
    else:
        # MODE B: STRATEGIC FEASIBILITY LOGIC
        gap_pct = (last_p - u_target) / last_p
        if gap_pct <= 0:
            status, s_col, window = "REALITY", "#00ff7f", "Immediate"
        elif gap_pct < 0.15:
            status, s_col, window = "PROBABLE", "#ffaa00", "Late 2026"
        else:
            status, s_col, window = "STRATEGIC", "#ff4b4b", "2027-2028 (Peak Supply)"

        st.subheader(f"🔍 Analysis for Target: ${u_target:,}")
        st.markdown(f"""
            <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; border-left: 5px solid {s_col};">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <span>Feasibility Status:</span> <b style="color:{s_col};">{status}</b>
                    <span>Probable Year: <b>{window}</b></span>
                </div>
                <p style="font-size:0.85rem; color:#ccc; margin:0;">
                    <b>Ground Intel:</b> Demand exceeds supply by {(bq_ratio-1)*100:.0f}%. 
                    A target of ${u_target:,} requires a {gap_pct*100:.1f}% correction, 
                    likely during the 2026/27 deregistration peak.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # 4. DATA VISUALIZATION (ON-THE-FLY)
    st.markdown("---")
    st.write(f"**{v_cat} Price Flux Stream**")

# ==========================================
# TAB 5: AF STRATEGIC BUY - AIRFARE PREDICTOR
# ==========================================
with tab5:
    st.header("✈️ Global Airfare Prediction Engine")
    
    # 1. TRIP & LOCATION CONFIG
    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        v_trip_type = st.radio("Trip Type:", ["Round Trip", "Single Leg"], horizontal=True, key="g10_t5_trip")
    with t_col2:
        u_input = st.text_input("Enter Country or City (Origin: SIN):", value="China", key="g10_t5_loc")

    # 2. INTERNAL AIRPORT ENGINE (Includes China Southern Hubs)
    geo_atlas = {
        "China": ["Guangzhou Baiyun (CAN)", "Shanghai Pudong (PVG)", "Beijing Daxing (PKX)", "Shenzhen (SZX)"],
        "Japan": ["Tokyo Narita (NRT)", "Tokyo Haneda (HND)", "Osaka (KIX)"],
        "Thailand": ["Bangkok (BKK)", "Phuket (HKT)"]
    }
    
    found_hubs = geo_atlas.get(u_input, [f"{u_input} Intl (Primary)"])
    v_selected_hubs = st.multiselect("Strategic Hub Selection:", found_hubs, default=found_hubs[0], key="g10_t5_hubs")

    # 3. DATE & PASSENGER DATA
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        d_dep = st.date_input("Departure Date:", value=date(2026, 6, 17), format="DD/MM/YYYY", key="g10_t5_dep")
        dep_day = d_dep.strftime('%A')
    with col_d2:
        if v_trip_type == "Round Trip":
            d_ret = st.date_input("Return (to SIN):", value=d_dep + timedelta(days=10), format="DD/MM/YYYY", key="g10_t5_ret")
        else:
            st.info("Direct Leg Selected")

    p1, p2, p3 = st.columns(3)
    with p1: adults = st.number_input("Adults (18+):", 1, 10, 1)
    with p2: children = st.number_input("Children (2-11):", 0, 10, 0)
    with p3: teens = st.number_input("Teens (12-17):", 0, 10, 0)

    st.divider()

    # 4. 7-AIRLINE PREDICTION LOGIC (2026 Trends)
    is_peak = d_dep.month in [6, 12]
    is_cheap_day = dep_day in ["Tuesday", "Wednesday"]
    
    # China Southern (CZ) is often cheapest on Tuesdays for the SIN-CAN route.
    rec_buy_week = "18-20 weeks out" if is_peak else "7-9 weeks out"
    predicted_cheapest_day = "Tuesday" if "China Southern" in str(v_selected_hubs) else "Wednesday"
    
    res_l, res_r = st.columns([1.8, 1])
    with res_l:
        st.markdown(f"#### 🔮 Strategic Forecast: All 7 Carriers")
        st.success(f"""
            **Optimal Purchase Window:** {rec_buy_week} before {d_dep.strftime('%d/%m/%y')}  
            **Predicted Cheapest Day:** {predicted_cheapest_day}  
            **Model Stance:** Current departure ({dep_day}) is {'✅ Optimal' if is_cheap_day else '⚠️ Peak Day Pricing'}.
        """)

    with res_r:
        # Multipliers: Base (980) * Peak (1.45) * TripType (0.65 for One-way) * Day (0.88 if CheapDay)
        day_mod = 0.88 if is_cheap_day else 1.05
        trip_mod = 1.0 if v_trip_type == "Round Trip" else 0.65
        peak_mod = 1.45 if is_peak else 1.0
        
        base_unit = 980 * peak_mod * trip_mod * day_mod
        total_price = ((adults + teens) * base_unit) + (children * base_unit * 0.75)
        st.metric("7-Airline Avg Prediction", f"${total_price:,.0f}")

    # 5. FULL 7-CARRIER PERFORMANCE GRID
    # Pricing weights: 1.0 (Base), Connections are 0.6-0.8x of SIA base.
    carriers = {
        "Singapore Airlines": {"base": 1.0, "route": "Direct"},
        "ANA / JAL": {"base": 0.94, "route": "Direct"},
        "Cathay Pacific": {"base": 0.81, "route": "1-Stop via HKG"},
        "Thai Airways (TG)": {"base": 0.72, "route": "1-Stop via BKK"},
        "China Southern (CZ)": {"base": 0.65, "route": "Direct/1-Stop via CAN"},
        "Air China": {"base": 0.62, "route": "1-Stop via PEK"}
    }
    
    grid_data = []
    for c, info in carriers.items():
        p = base_unit * info["base"]
        grid_data.append({
            "Carrier": c,
            "Adult Est.": f"${p:,.0f}",
            "Child Est.": f"${p*0.75:,.0f}",
            "Route Style": info["route"]
        })
    st.table(grid_data)

    # 6. PRICE TREND CHART (Original Syntax)
    st.write(f"**Price Projection: Weeks leading to {d_dep.strftime('%d/%m/%y')}**")
    weeks = list(range(22, 0, -1))
    prices = [total_price * (1.25 if w > 18 else 0.88 if w > 8 else 1.15) for w in weeks]
    st.area_chart(pd.DataFrame({"Price (SGD)": prices}, index=weeks), color="#ffd700")
    
   
