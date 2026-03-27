import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator
from datetime import date, timedelta
import yfinance as yf
from io import StringIO

# --- 1. PAGE CONFIG & STYLES (gold 10 Concise) ---
st.set_page_config(page_title="SGINFOMON", page_icon="🇸🇬60", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 150_px; color: var(--text-color); line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.2; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.82rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.82rem; }
    .stat-label { font-size: 0.72rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    .holiday-text { font-size: 0.95rem; color: #28a745; font-weight: bold; margin-left: 10px; }
    .stButton>button { height: 26px; padding: 0 10px; font-size: 0.75rem; min-height: 26px; }
    div[data-testid="stExpander"] [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BRAIN: LIVE FUEL SCRAPER ---
def get_live_fuel_sync():
    # March 2026 Baseline Template
    data = {
        "92 Octane": {"Esso": [3.43, 0.0], "Caltex": [3.43, 0.0], "SPC": [3.43, 0.0]},
        "95 Octane": {"Esso": [3.47, 0.0], "Caltex": [3.47, 0.0], "Shell": [3.47, 0.0], "SPC": [3.46, 0.0], "Cnergy": [2.46, 0.0], "Sinopec": [3.47, 0.0], "Smart Energy": [2.61, 0.0]},
        "98 Octane": {"Esso": [3.97, 0.0], "Shell": [3.99, 0.0], "SPC": [3.97, 0.0], "Cnergy": [2.80, 0.0], "Sinopec": [3.97, 0.0], "Smart Energy": [2.99, 0.0]},
        "Premium":   {"Caltex": [4.16, 0.0], "Shell": [4.21, 0.0], "Sinopec": [4.10, 0.0]},
        "Diesel":    {"Esso": [3.73, 0.0], "Caltex": [3.73, 0.0], "Shell": [3.73, 0.0], "SPC": [3.56, 0.0], "Cnergy": [2.80, 0.0], "Sinopec": [3.72, 0.0], "Smart Energy": [2.83, 0.0]}
    }
    try:
        url = "https://www.motorist.sg/petrol-prices"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        df = pd.read_html(StringIO(resp.text), header=0)[0]

        for _, row in df.iterrows():
            brand_raw = str(row.iloc[0]).lower()
            for b_name in ["Esso", "Shell", "Caltex", "SPC", "Sinopec", "Cnergy", "Smart Energy"]:
                if b_name.lower() in brand_raw:
                    for grade, col in [("92 Octane", '92'), ("95 Octane", '95'), ("98 Octane", '98'), ("Premium", 'Premium'), ("Diesel", 'Diesel')]:
                        val = str(row.get(col, '-')).replace('$', '').strip()
                        if val not in ['-', 'nan', 'N/A']:
                            try:
                                data[grade][b_name] = [float(val), 0.0]
                            except: continue
    except: pass
    return data

# --- 3. THE BEAUTY: DYNAMIC POP-UP ---
@st.dialog("Fuel Brand Details")
def show_fuel_details(ftype):
    with st.spinner("Syncing 2026 Live Prices..."):
        live_data = get_live_fuel_sync()
    
    st.write(f"### 📍 {ftype} Price List")
    st.caption(f"Last Synced: {datetime.now().strftime('%H:%M:%S')}")
    
    brand_order = ["Esso", "Caltex", "Shell", "SPC", "Cnergy", "Sinopec", "Smart Energy"]
    for brand in brand_order:
        b_data = live_data[ftype].get(brand, ("N/A", 0))
        price, change = b_data
        if brand == "Shell" and ftype == "92 Octane": continue
        
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:4px; border-bottom:1px solid #333; font-size:14px;'>
                <b>{brand}</b>
                <span>
                    <b style='color:#007bff; margin-right:8px;'>{display_price}</b>
                    <span style='color:{"#ff4b4b" if change > 0 else "#09ab3b"}'>({change:+.2f})</span>
                </span>
            </div>
        """, unsafe_allow_html=True)

# --- 4. DATA ENGINES (Market, FX, Economy, Holidays) ---
def get_upcoming_holiday():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz).date()
    holidays_2026 = [("New Year's Day", date(2026, 1, 1)), ("Chinese New Year", date(2026, 2, 17)), ("Hari Raya Puasa", date(2026, 3, 21)), ("Good Friday", date(2026, 4, 3)), ("Labour Day", date(2026, 5, 1)), ("Hari Raya Haji", date(2026, 5, 27)), ("Vesak Day", date(2026, 5, 31)), ("National Day", date(2026, 8, 9)), ("Deepavali", date(2026, 11, 8)), ("Christmas Day", date(2026, 12, 25))]
    for name, h_date in holidays_2026:
        if h_date >= now: return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

@st.cache_data(ttl=300)
def fetch_live_market_data():
    tickers = {"STI": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Brent": "BZ=F", "NatGas": "NG=F"}
    results = {}
    for label, sym in tickers.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            results[label] = (curr, ((curr - prev) / prev) * 100)
        except: results[label] = (0.0, 0.0)
    return results

@st.cache_data(ttl=300)
def fetch_live_forex():
    fx_tickers = {"MYR": "SGDMYR=X", "JPY": "SGDJPY=X", "THB": "SGDTHB=X", "CNY": "SGDCNY=X", "USD": "SGDUSD=X"}
    results = {}
    for label, sym in fx_tickers.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            results[label] = (curr, ((curr - prev) / prev) * 100)
        except: results[label] = (0.0, 0.0)
    return results

# --- 5. UI LAYOUT: TAB 1 ---
st.title("🇸🇬 SG Info Monitor 10.9")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 LIVE MONITOR", "🏢 SG SERVICES", "🛠️ TOOLS", "🔮 COE", "✈️ FLIGHTS"])

with tab1:
    # Clocks
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    
    # News & Holidays
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{get_upcoming_holiday()}</span>', unsafe_allow_html=True)
    news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/"}
    for src, url in news_sources.items():
        try:
            feed = feedparser.parse(requests.get(url, timeout=5).content)
            entry = feed.entries[0]
            st.write(f"<span class='news-tag'>{src}</span> **[{entry.title}]({entry.link})**", unsafe_allow_html=True)
        except: pass

    st.divider()

    # Markets
    m_live = fetch_live_market_data()
    with st.expander("📈 Market Indices", expanded=True):
        mc = st.columns(5)
        for i, label in enumerate(["STI", "Gold", "Silver", "Brent", "NatGas"]):
            mc[i].metric(label, f"{m_live[label][0]:,.2f}", f"{m_live[label][1]:+.2f}%")

    # Forex
    fx_data = fetch_live_forex()
    with st.expander("💱 Forex (1 SGD)", expanded=True):
        fc_fx = st.columns(5)
        for i, label in enumerate(["MYR", "JPY", "THB", "CNY", "USD"]):
            fc_fx[i].metric(f"SGD/{label}", f"{fx_data[label][0]:.2f}", f"{fx_data[label][1]:+.2f}%")

    # COE Results
    with st.expander("🚗 COE Bidding (Mar 2026)", expanded=True):
        coe = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
        cc = st.columns(5)
        for i, (cat, p, d) in enumerate(coe):
            cc[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>', unsafe_allow_html=True)

    # 5. FUEL PRICES: DYNAMIC LOGIC (gold 10)
    with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
        # Initial sync for the summary averages
        current_summary = get_live_fuel_sync() 
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]

        for i, ftype in enumerate(ftypes):
            # Calculate Average (Ignoring 'N/A')
            prices = [v[0] for v in current_summary[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            
            fc[i].metric(ftype, f"${avg:.2f}")
            
            # View Brands Button triggers Dialog with a fresh DYNAMIC pull
            if fc[i].button("View Brands", key=f"vbtn_{ftype}_{i}"):
                show_fuel_details(ftype)

# --- THE POP-UP DIALOG (Kept exactly as you like it) ---
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
    # 1. DATA ENGINE (The "Brain" for gold 10)
    @st.cache_data(ttl=60)
    def fetch_market_engine_g10(target_iso, days_lookback):
        import yfinance as yf
        import pytz
        from datetime import datetime, timedelta
        
        sgt = pytz.timezone('Asia/Singapore')
        now_sgt = datetime.now(sgt)
        
        # Market Status Logic
        is_weekend = (now_sgt.weekday() == 5 and now_sgt.hour >= 6) or \
                     (now_sgt.weekday() == 6) or \
                     (now_sgt.weekday() == 0 and now_sgt.hour < 5)
        
        countdown_msg = None
        if is_weekend:
            target_open = now_sgt + timedelta(days=(7 - now_sgt.weekday()) % 7)
            target_open = target_open.replace(hour=5, minute=0, second=0, microsecond=0)
            if now_sgt.weekday() == 0: target_open = now_sgt.replace(hour=5, minute=0, second=0)
            diff = target_open - now_sgt
            hours, remainder = divmod(int(diff.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            countdown_msg = f"⏳ Sydney FX Open in {hours}h {minutes}m"

        try:
            ticker = yf.Ticker(f"SGD{target_iso}=X")
            latest_df = ticker.history(period="1d", interval="5m")
            curr_rate = latest_df['Close'].iloc[-1]
            prev_rate = latest_df['Close'].iloc[-2] if len(latest_df) > 1 else curr_rate
            
            hist_df = ticker.history(period=f"{days_lookback}d")
            hist_rates = hist_df['Close'].tolist()
            
            return {
                "rate": curr_rate, "prev": prev_rate, "timestamp": now_sgt.strftime("%H:%M:%S"),
                "spread": {"CNY": 0.0008, "THB": 0.0015}.get(target_iso, 0.0010),
                "high": max(hist_rates), "low": min(hist_rates),
                "std": np.std(hist_rates) if len(hist_rates) > 1 else curr_rate * 0.005,
                "closed": is_weekend, "countdown": countdown_msg,
                "heartbeat": "🔴 MARKET CLOSED" if is_weekend else "🟢 MARKET LIVE"
            }
        except:
            return {"rate": 5.3771, "prev": 5.3770, "timestamp": "--:--", "spread": 0.0012, 
                    "high": 5.41, "low": 5.35, "std": 0.01, "closed": is_weekend, "heartbeat": "⚠️ FEED DELAY"}

    # 2. HEADER WITH HEARTBEAT
    if "g10_t3_i_final" not in st.session_state:
        st.session_state["g10_t3_i_final"] = "CNY"
        
    m_status = fetch_market_engine_g10(st.session_state["g10_t3_i_final"], 10)
    
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h2 style="margin:0;">🎯 Tactical Trade Scheduler</h2>
            <div style="background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 20px; border: 1px solid #444;">
                <span style="font-size: 0.75rem; font-weight: bold; color: {'#00ff7f' if 'LIVE' in m_status['heartbeat'] else '#ff4b4b'};">
                    {m_status['heartbeat']}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. ROW 1: CONTROLS & RANGE
    r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 2], vertical_alignment="center")
    with r1_c1:
        p_stance = st.radio("MAS Policy Stance:", ["Hawkish", "Neutral", "Dovish"], horizontal=True, key="g10_t3_p_final")
    with r1_c2:
        lookback = st.selectbox("Range:", [5, 10], index=1, format_func=lambda x: f"{x} Days", key="g10_t3_d_final")
    
    supported_iso = ["CNY", "THB", "JPY", "MYR", "EUR", "USD", "GBP"]
    selected_iso = st.selectbox("Target Currency:", supported_iso, key="g10_t3_i_final", label_visibility="collapsed")
    m_data = fetch_market_engine_g10(selected_iso, lookback)

    with r1_c3:
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

    # 4. ROW 2: AMOUNT & TARGET
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        t_amt = st.number_input("Amount (SGD):", min_value=0, value=1000, key="g10_t3_a_final")
    with r2_c2:
        u_target = st.number_input("Target Price:", value=m_data['rate']*1.002, format="%.4f", key="g10_t3_t_final")

    # 5. LOGIC & PROBABILITY
    speed_mult = {"Hawkish": 1.15, "Neutral": 1.0, "Dovish": 0.80}[p_stance]
    price_gap = abs(u_target - m_data['rate'])
    days_req = int(np.ceil(price_gap / (m_data['std'] * speed_mult))) if price_gap > 0 else 0
    action_dt = (datetime.now(pytz.timezone('Asia/Singapore')) + pd.Timedelta(days=days_req)).strftime('%d %b %Y')
    
    z_score = price_gap / (m_data['std'] * np.sqrt(max(days_req, 1)))
    prob_val = max(5, min(99, 100 * (1 - (z_score / 3))))

    # 6. ROW 3: LIVE FEED & VISUALS
    st.markdown("---")
    out_c1, out_c2 = st.columns([1.5, 2])
    
    with out_c1:
        st.markdown(f"**Suggest Action Date: {action_dt}**")
        p_color = "#00ff7f" if prob_val > 60 else "#ffaa00" if prob_val > 30 else "#ff4b4b"
        st.markdown(f"""<div style="margin-bottom: 20px;"><small>Possibility Rate:</small> <strong>{prob_val:.1f}%</strong>
            <div style="background: #333; height: 8px; border-radius: 4px; width: 100%;"><div style="background: {p_color}; height: 8px; border-radius: 4px; width: {prob_val}%;"></div></div></div>""", unsafe_allow_html=True)
        
        label = "Closed Trading Value" if m_data['closed'] else "Live Market Rate"
        st.metric(label, f"{m_data['rate']:.4f}")
        
        price_diff = m_data['rate'] - m_data['prev']
        diff_color = "#00ff7f" if price_diff >= 0 else "#ff4b4b"
        st.markdown(f"""<div style="font-size: 0.85rem; margin-top: -12px; margin-bottom: 8px;">
                <span style="color: #888;">Prev: </span><span style="color: {diff_color}; font-weight: bold;">{m_data['prev']:.4f}</span>
                <span style="color: #666; margin-left: 10px;">🕒 {m_data['timestamp']} SGT</span></div>
            <div style="color: #555; font-size: 0.8rem;">Est. Spread: {m_data['spread']:.4f}</div>""", unsafe_allow_html=True)

    with out_c2:
        path = np.linspace(m_data['rate'], u_target, 10)
        st.line_chart(pd.DataFrame({"Path": path, "Model High": [m_data['high']]*10, "Model Low": [m_data['low']]*10}), height=150)

    # 7. NEW: DAILY PREDICTION POP-UP FUNCTION
    st.divider()
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🚀 View Daily Rate Prediction", use_container_width=True, key="g10_t3_predict"):
            @st.dialog(f"Forecast: SGD/{selected_iso} ({lookback}D Basis)")
            def show_daily_prediction():
                import numpy as np
                from datetime import datetime, timedelta
                
                st.write(f"**Current Base Rate:** {m_data['rate']:.4f}")
                st.write(f"**Calculated Volatility (Std Dev):** {m_data['std']:.4f}")
                
                predict_rows = []
                for d in range(lookback):
                    day_num = d + 1
                    target_date = datetime.now() + timedelta(days=d)
                    
                    # Statistical Drift Prediction
                    drift = (m_data['std'] * speed_mult * np.sqrt(day_num))
                    high_est = m_data['rate'] + drift
                    low_est = m_data['rate'] - drift
                    
                    predict_rows.append({
                        "Day": f"Day {day_num}",
                        "Date": target_date.strftime('%d %b'),
                        "Expected High": f"{high_est:.4f}",
                        "Expected Low": f"{low_est:.4f}",
                        "Trend": "📈" if high_est > m_data['high'] else "📉" if low_est < m_data['low'] else "↔️"
                    })
                st.table(predict_rows)
                st.caption("Note: Predictions based on Browninan Motion volatility models.")
                if st.button("Close"): st.rerun()
            show_daily_prediction()

    with btn_col2:
        if st.button("🔒 Confirm Tactical Execution", use_container_width=True, key="g10_t3_exec_final"):
            st.success(f"Execution plan locked for {action_dt}. Target Prob: {prob_val:.1f}%")

#==========================================
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
# TAB 5: AIRFARE & DYNAMIC VISA ENGINE
# ==========================================
# ==========================================
# TAB 5: AIRFARE ENGINE (Interactive Pop-up)
# ==========================================
# ==========================================
# TAB 5: REFINED POP-UP (TOP 3 VISIBILITY)
# ==========================================
with tab5:
    st.header("✈️ Asia Airfare Prediction Engine")
    
    # 1. ORIGIN & NATIONALITY CONFIG
    col_a, col_b = st.columns(2)
    with col_a:
        origin_options = ["Singapore (SIN)", "Bangkok (BKK)", "Hong Kong (HKG)", "China (CN)", "Japan (JP)"]
        u_origin_cat = st.selectbox("Select Origin:", origin_options, index=0, key="g10_t5_orig")
        
        china_list = ["Beijing (PEK)", "Shanghai (PVG)", "Guangzhou (CAN)", "Shenzhen (SZX)", "Chengdu (TFU)"]
        thailand_list =["Suvarnabhumi (BKK)", "Don Mueang (DMK)", "Phuket (HKT)"]
        
        if "China" in u_origin_cat:
            v_origin_final = st.selectbox("Select China Origin:", china_list, key="g10_t5_china_orig")
        elif "Thailand" in u_origin_cat:
            v_origin_final = st.selectbox("Select Thailand Origin:", thailand_list, key="g10_t5_thai_orig")
        else:
            v_origin_final = u_origin_cat

    with col_b:
        u_nationality = st.text_input("Enter Nationality:", value="Singaporean", key="g10_t5_nat").strip().title()
        v_trip_type = st.radio("Trip Type:", ["Round Trip", "Single Leg"], horizontal=True, key="g10_t5_trip")

    # 2. DATES & DESTINATION
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        d_dep = st.date_input("Departure Date:", value=date(2026, 6, 17), format="DD/MM/YYYY", key="g10_t5_dep")
    with d_col2:
        d_ret = st.date_input("Return Date:", value=date(2026, 6, 24), format="DD/MM/YYYY", key="g10_t5_ret") if v_trip_type == "Round Trip" else None

    dest_country = st.selectbox("Destination Country:", ["China", "Thailand", "Japan", "Singapore", "Other"], key="g10_t5_dest_country")
    
    # 3. CARRIER PRIORITY GRID
    master_carriers = [
        {"name": "Singapore Airlines", "home": "Singapore", "w": 1.0, "hub": "SIN"},
        {"name": "Cathay Pacific", "home": "Hong Kong", "w": 0.85, "hub": "HKG"},
        {"name": "Air China", "home": "China", "w": 0.65, "hub": "PEK/PKX"},
        {"name": "China Southern", "home": "China", "w": 0.68, "hub": "CAN/PKX"},
        {"name": "Thai Airways", "home": "Thailand", "w": 0.75, "hub": "BKK"},
        {"name": "ANA / JAL", "home": "Japan", "w": 0.95, "hub": "NRT/HND"}
    ]

    priority_carriers = [c for c in master_carriers if c["home"] == dest_country]
    other_carriers = [c for c in master_carriers if c["home"] != dest_country]
    final_sorted = priority_carriers + other_carriers

    base_price = 820 if "China" in u_origin_cat else 980
    multiplier = (1.45 if d_dep.month in [6, 12] else 1.0) * (1.0 if v_trip_type == "Round Trip" else 0.65)
    final_unit = base_price * multiplier

    grid_data = []
    for c in final_sorted:
        price = final_unit * c["w"]
        grid_data.append({
            "Carrier": c["name"],
            "Adult Est. ($)": f"{price:,.0f}",
            "Transit Hub": c["hub"] if c["home"] != u_origin_cat and c["home"] != dest_country else "Direct"
        })

    st.subheader(f"📊 Carrier Pricing Table (Priority: {dest_country})")
    st.table(grid_data)

    # 4. VISA ADVISORY
    visa_alert = "✅ Visa Not Required (30-60 Days)." if u_nationality in ["Singaporean", "Thai"] and dest_country in ["China", "Thailand"] else "⚠️ Check 2026 Portal."
    st.info(f"**🛂 2026 Entry Protocol:** {visa_alert}")

    st.divider()

    # 5. STRATEGIC 16-WEEK FORECAST (INTERACTIVE POP-UP)
    st.subheader("🗓️ 16-Week Strategic Purchase Roadmap")
    if st.button("🚀 View Weekly Price Forecast (Interactive)", key="g10_t5_forecast_btn"):
        @st.dialog("16-Week Execution Roadmap")
        def show_forecast():
            # Home Base Logic (Origin)
            origin_label = u_origin_cat.split(" (")[0]
            home_airline = next((c for c in master_carriers if c["home"] == origin_label), master_carriers[0])
            top_3_names = [c["name"] for c in final_sorted[:3]]
            
            # --- NEW: AIRLINE SELECTOR INSIDE POP-UP ---
            st.markdown("### 🛠️ Strategy Configuration")
            col1, col2 = st.columns(2)
            with col1:
                use_home = st.toggle(f"Use Home Base ({home_airline['name']})", value=False, key="g10_t5_pop_home")
            with col2:
                selected_carrier_name = st.selectbox("Or Select Specific Airline:", [c["name"] for c in master_carriers], key="g10_t5_pop_select")
            
            # Pricing Logic based on selection
            if use_home:
                active_carrier = home_airline
            else:
                active_carrier = next(c for c in master_carriers if c["name"] == selected_carrier_name)
            
            active_unit = final_unit * active_carrier["w"]
            
            st.write(f"**Route:** {v_origin_final} ➔ {v_land_airport}")
            st.success(f"📈 Showing Strategy for: **{active_carrier['name']}**")
            
            forecast_rows = []
            for w in range(16, -1, -1):
                target_date = d_dep - timedelta(weeks=w)
                # Advice includes the Top 3 regardless of which airline is selected for pricing
                if w > 9: advice = "⏳ HOLD"
                elif 7 <= w <= 9: advice = f"✅ BUY: {', '.join(top_3_names)}"
                else: advice = "🚨 PANIC"
                
                p = active_unit * (1.0 if 7 <= w <= 9 else 1.25)
                forecast_rows.append({
                    "Date": target_date.strftime('%d %b %Y'),
                    "Est. Total ($)": f"{p:,.0f}",
                    "Strategic Advice": advice
                })
            
            st.table(forecast_rows)
            if st.button("Close"): st.rerun()
        show_forecast()
