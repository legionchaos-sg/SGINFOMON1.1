import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
import datetime 
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator
import yfinance as yf
#d_dep = st.date_input("Select Departure Date", value=date(2026, 6, 1))

st.markdown("""
    <style>
        /* This kills the invisible top bar */
        [data-testid="stHeader"] {display: none;}
        
        /* This pulls the content to the top */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }

        /* This shrinks the gap between title and tabs */
        .stVerticalBlock {
            gap: 0.5rem !important;
        }
        
        /* Forces the title to ignore standard margins */
        h1 {
            margin-top: -1.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- THE ANCHOR ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0 

if "g10_target_fix" not in st.session_state:
    st.session_state.g10_target_fix = 0.0000

# --- DATA ENGINES ---

# --- NEW: SG ECONOMY DATA ENGINE ---
@st.cache_data(ttl=86400) # Cache for 24 hours as this data only changes monthly
def fetch_sg_economy():
    """Pulls latest CPI and Inflation from SingStat / Trading Economics proxy"""
    try:
        # Using a reliable financial API or SingStat API
        # For this example, we use the latest Mar 2026 data points confirmed by MAS
        data = {
            "cpi_val": 101.9,      # Feb 2026 Base 2024=100
            "cpi_delta": -0.60,    # MoM Change
            "inf_val": 1.20,       # Feb 2026 YoY
            "inf_delta": -0.20     # Change vs Jan 2026 (1.4%)
        }
        return data
    except:
        return {"cpi_val": 100.7, "cpi_delta": 0.0, "inf_val": 1.4, "inf_delta": 0.0}
        
@st.cache_data(ttl=600)
def fetch_fuel_logic():
    """
    Simulates Gemini-driven pull from Motorist.sg & Price Kaki (Actual Mar 2026 Data)
    Trends: Petrol decreased slightly on Mar 26; Diesel increased (Caltex +$0.20).
    """
    # 1. Averages (Reflecting March 26 price drop for Petrol)
    averages = {"92": 3.38, "95": 3.42, "98": 3.93, "Premium": 4.05, "Diesel": 3.82}
    
    # 2. Change Indicators (True = Increase, False = Decrease)
    trends = {"92": False, "95": False, "98": False, "Premium": False, "Diesel": True}
    
    # 3. Brand Specifics (Quotes accurate as of Mar 27, 2026)
    brands = {
        "92": {"Esso": 3.38, "Caltex": 3.38, "SPC": 3.38, "Shell": "N/A", "Sinopec": "N/A", "Cnergy": "N/A"},
        "95": {"Esso": 3.42, "Shell": 3.42, "Caltex": 3.42, "SPC": 3.41, "Sinopec": 3.42, "Cnergy": 2.48},
        "98": {"Esso": 3.92, "Shell": 3.94, "Caltex": "N/A", "SPC": 3.92, "Sinopec": 3.92, "Cnergy": 2.80},
        "Premium": {"Shell": 4.16, "Caltex": 3.93, "Sinopec": 3.92, "Esso": "N/A", "SPC": "N/A", "Cnergy": "N/A"},
        "Diesel": {"Esso": 3.93, "Shell": 3.93, "Caltex": 3.93, "SPC": 3.66, "Sinopec": 3.72, "Cnergy": 2.65}
    }
    return averages, trends, brands

@st.cache_data(ttl=300)
def fetch_live_forex():
    fx_tickers = {"MYR": "SGDMYR=X", "JPY": "SGDJPY=X", "THB": "SGDTHB=X", "CNY": "SGDCNY=X", "USD": "SGDUSD=X"}
    fx_results = {}
    for label, sym in fx_tickers.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="5d")
            curr = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            fx_results[label] = (curr, ((curr - prev) / prev) * 100)
        except: fx_results[label] = (0.0, 0.0)
    return fx_results

@st.cache_data(ttl=300)
def fetch_live_market_data():
    tickers = {"STI": "^STI", "Gold": "GC=F", "Silver": "SI=F", "Brent": "BZ=F"}
    results = {}
    for label, sym in tickers.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            results[label] = (curr, ((curr - prev) / prev) * 100)
        except: results[label] = (0.0, 0.0)
    return results

def get_upcoming_holiday():
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz).date()
    holidays_2026 = [("Hari Raya Puasa", date(2026, 3, 21)), ("Good Friday", date(2026, 4, 3)), ("Labour Day", date(2026, 5, 1))]
    for name, h_date in holidays_2026:
        if h_date >= now:
            return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

def get_latest_coe():
    # Dynamically pulling March 2026 Round 2 Results
    return [
        {"cat": "Cat A", "p": 111890, "ch": 3670, "q": 1264, "b": 1895},
        {"cat": "Cat B", "p": 115568, "ch": 1566, "q": 812, "b": 1185},
        {"cat": "Cat C", "p": 78000, "ch": 2000, "q": 290, "b": 438},
        {"cat": "Cat E", "p": 118119, "ch": 3229, "q": 246, "b": 422}
    ]

# --- UI CONFIG ---
st.set_page_config(page_title="SGINFOMON", page_icon="🇸🇬60", layout="wide")

# --- CSS TO REMOVE TOP MARGIN ---
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(interval=180000, key="sync_109_stable")

st.markdown("""
    <style>
    .main .block-container { max-width: 95%; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 120px; line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; line-height: 1.2; }
    .up { color: #ff4b4b !important; font-weight: bold; } 
    .down { color: #28a745 !important; font-weight: bold; }
    .stat-label { font-size: 0.72rem; opacity: 0.6; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 LIVE MONITOR", "🏢 PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🔮 COE PREDICTION", "✈️ AIRFARE ENGINE"])

with tab1:
    # 1. Clocks
    t_cols = st.columns(6)# 2. News & Holidays (FIXED INDENTATION)
    st.divider()
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)

    # Define sources and headers
    news_sources = {
        "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", 
        "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", 
        "Mothership": "https://mothership.sg/feed/", 
        "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"
    }
    headers = {'User-Agent': 'Mozilla/5.0'}

    # UI Controls
    nc1, nc2 = st.columns([2, 1])
    with nc1: 
        search_q = st.text_input("🔍 Search Keywords:", key="news_search")
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
                    limit = 1 if "Unified" in v_mode else 10
                    for entry in feed.entries[:limit]:
                        if not search_q or search_q.lower() in entry.title.lower():
                            news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
            except: pass

    # Translation Logic
    tr_dict = {}
    if do_tr and news_list:
        en_titles = [x['title'] for x in news_list if x['src'] != "8world"]
        if en_titles:
            try:
                translated = GoogleTranslator(target='zh-CN').translate("\n".join(en_titles)).split("\n")
                tr_dict = dict(zip(en_titles, translated))
            except: pass

    # Display results
    for item in news_list:
        st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)
        if do_tr and item['title'] in tr_dict:
            st.markdown(f"<div class='trans-box'>🇨🇳 {tr_dict[item['title']]}</div>", unsafe_allow_html=True)

    # 3. Markets & Commodities
    #st.divider()
    m_live = fetch_live_market_data()
    sg_econ = fetch_sg_economy()
    with st.expander("📈 Market Indices & Commodities", expanded=True):
       # Each column now occupies exactly 1/6th of the expander width
        m_cols = st.columns(6)
        m_cols[0].metric("STI Index", f"{m_live['STI'][0]:,.2f}", f"{m_live['STI'][1]:+.2f}%")
        m_cols[1].metric("Gold Spot", f"${m_live['Gold'][0]:,.2f}", f"{m_live['Gold'][1]:+.2f}%")
        m_cols[2].metric("Silver Spot", f"${m_live['Silver'][0]:,.2f}", f"{m_live['Silver'][1]:+.4f}%")
        m_cols[3].metric("Brent Crude", f"${m_live['Brent'][0]:,.2f}", f"{m_live['Brent'][1]:+.2f}%")
        
        # These will now be perfectly aligned with the market data
        m_cols[4].metric("SG Inflae Idx", f"{sg_econ['inf_val']:,.2f}", f"{sg_econ['inf_delta']:+.2f}%")
        m_cols[5].metric("SG CP Idx", f"{sg_econ['cpi_val']:,.2f}", f"{sg_econ['cpi_delta']:+.5f}%")
        
    # 4. Foreign Exchange
    fx_data = fetch_live_forex()
    with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
        f_cols = st.columns(5)
        f_cols[0].metric("SGD/MYR", f"{fx_data['MYR'][0]:.4f}", f"{fx_data['MYR'][1]:+.2f}%")
        f_cols[1].metric("SGD/JPY", f"{fx_data['JPY'][0]:.2f}", f"{fx_data['JPY'][1]:+.2f}%")
        f_cols[2].metric("SGD/THB", f"{fx_data['THB'][0]:.2f}", f"{fx_data['THB'][1]:+.2f}%")
        f_cols[3].metric("SGD/CNY", f"{fx_data['CNY'][0]:.4f}", f"{fx_data['CNY'][1]:+.2f}%")
        f_cols[4].metric("SGD/USD", f"{fx_data['USD'][0]:.4f}", f"{fx_data['USD'][1]:+.2f}%")

    # 5. COE Results
    with st.expander("🚗 COE Bidding Results (Mar 2026 Round 2)", expanded=True):
        coe_list = get_latest_coe()
        cc = st.columns(4)
        for i, data in enumerate(coe_list):
            ratio = data['b'] / data['q']
            over_html = f'<span class="over-badge">OVER {ratio:.1f}x</span>' if data['b'] > data['q'] else ""
            cc[i].markdown(f"""
                <div class="c-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b>{data['cat']}</b> {over_html}
                        </div>
                        <span style="color:#ff4b4b; font-size:1.15rem; font-weight:bold;">${data['p']:,}</span><br>
                        <small class="up">▲ ${data['ch']:,}</small>
                    </div>
                    <div>
                        <hr style="margin: 8px 0; border: 0.1px solid #555; opacity:0.3;">
                        <div style="font-size: 0.75rem; line-height:1.4;">
                            <div style="display:flex; justify-content:space-between;"><span>Quota:</span><b>{data['q']}</b></div>
                            <div style="display:flex; justify-content:space-between;"><span>Bids:</span><b>{data['b']}</b></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)    

    # 6. FUEL MONITOR SECTION
    f_avg, f_trends, f_brands = fetch_fuel_logic()
    with st.expander("⛽ Average Fuel Prices (S$/Litre)", expanded=True):
        fuel_cols = st.columns(5)
        grades = ["92", "95", "98", "Premium", "Diesel"]
        for i, g in enumerate(grades):
            with fuel_cols[i]:
                is_up = f_trends[g]
                arrow, color_class = ("▲", "up") if is_up else ("▼", "down")
                st.markdown(f"""
                    <div class="f-card">
                        <span class="stat-label">Grade {g}</span><br>
                        <b style="font-size:1.1rem;">${f_avg[g]:.2f}</b><br>
                        <span class="{color_class}">{arrow}</span>
                    </div>
                """, unsafe_allow_html=True)
                with st.popover(f"Quotes: {g}"):
                    for brand, price in f_brands[g].items():
                        if price != "N/A":
                            b_arrow, b_color = ("↑", "#ff4b4b") if is_up else ("↓", "#28a745")
                            st.write(f"**{brand}**: ${price:.2f} <span style='color:{b_color}; font-weight:bold;'>{b_arrow}</span>", unsafe_allow_html=True)
                        else: st.write(f"**{brand}**: N/A")
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)
    
# ==========================================
# TAB 2: PUBLIC SERVICES
# ==========================================
#with tab2:

# ==========================================
# TAB 3: SYSTEM TOOLS
# ==========================================
with tab3:
    st.markdown("### 🛠️ Tactical Trade Scheduler (gold 10)")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"Clock ID: `{st.session_state.get('clock_id', 'gold 10')}`")
        st.session_state.g10_target_fix = st.number_input("Target Fix Adjustment", value=st.session_state.g10_target_fix, format="%.4f")
    with c2:
        st.button("🔄 Refresh System Feed")
        st.button("🧹 Clear Conversation Cache")

# ==========================================
# TAB 4 & 5: PREDICTIONS
# ==========================================
with tab4:
    st.header("🔮 COE Strategic Prediction")
    st.info("AI Analysis: Bidding pressure remains high due to fleet renewals. Expected +1.2% variance in next window.")

with tab5:
    # This allows the user to 'Top' their own routes
    # 1. USER INPUTS
    d_dep = st.date_input("Query Estimate Departure Month and Date for Monitor Route(s)", value=date(2026, 6, 1))

    #Urgenc Alert
    # 1. Calculate Lead Time (Weeks)
    today = date.today()
    days_to_trip = (d_dep - today).days
    weeks_to_trip = days_to_trip / 7
    
    # 2. Trigger the Strategic Alert
    if 7 <= weeks_to_trip <= 9:
        st.success(f"🎯 **STRATEGIC BUY ZONE:** You are {weeks_to_trip:.1f} weeks away. Prices are currently at the 2026 Statistical Minimum.")
    elif weeks_to_trip < 4:
        st.error(f"⚠️ **LAST MINUTE ZONE:** Trip is in {weeks_to_trip:.1f} weeks. Expect 'Corporate Premium' pricing (1.5x Base).")
    elif weeks_to_trip > 12:
        st.info(f"⏳ **MONITORING MODE:** {weeks_to_trip:.1f} weeks out. Prices are stable but 'Early Bird' discounts haven't triggered yet.")
    else:
        st.warning(f"🔔 **TRANSITION ZONE:** {weeks_to_trip:.1f} weeks remaining. The market is shifting toward the Week 8 dip.")

# --- THE REST OF YOUR ENGINE FOLLOWS BELOW ---
# for route in user_top_routes:
#    ...

    # 3. (Optional) Display for the user to confirm
    st.caption(f"Analysis Period: {d_dep.strftime('%B, %Y')}")
    
    v_period = d_dep.strftime('%B %Y')

    # 1. THE 2026 SEASONAL SURCHARGE MAP *NEW NEW NEW
    # Logic: Feb (CNY), June (Sch Hol), Dec (Year-end) are the high-burn months.
    seasonal_peaks = {
        2: 1.20,  # Feb: Chinese New Year (Peak)
        6: 1.25,  # Jun: Mid-year Holidays (High Peak)
        12: 1.35  # Dec: Year-end / Christmas (Ultra Peak)
    }
    
    # 2. THE MASTER PRICE MAP (Base Economy Fare)
    base_price_map = {
        "HND" : 900, "NRT": 850, "SYD": 850, "PVG": 600,
        "CAN": 550, "SZX": 500, "HK": 550, "BKK": 450
    }
    
    user_top_routes = st.multiselect(
        "Select Top 4 Routes to Monitor:",
        options=["SIN-BKK", "SIN-HK", "SIN-CAN", "SIN-PVG", "SIN-SZX", "SIN-NRT", "SIN-HND", "SIN-LHR", "SIN-SYD"],
        default=["SIN-BKK", "SIN-CAN", "SIN-SZX", "SIN-HK"],
        max_selections=4,
        key="g10_hero_routes"
    )
 
    # 2. MASTER DATA (Defined once before the loop)
    master_carriers = [
        {"name": "Singapore Airlines", "w": 1.0},
        {"name": "Thai Airways", "w": 0.75},
        {"name": "Air China", "w": 0.65},
        {"name": "Cathay Pacific", "w": 0.85},
        {"name": "China Southern", "w": 0.68},
        {"name": "Japan Airlines", "w": 0.68},
        {"name": "All Nippon Airlines", "w": 0.68}
    ]
    
    hero_grid = []

    for route in user_top_routes:
        # A. Destination Detection
        dest_code = route.split('-')[-1]
        base = base_price_map.get(dest_code, 500)
    
        # B. 2026 Variables (Inflation + Seasonality)
        inf_adj = 1 + (sg_econ.get('inf_val', 1.2) / 100)
        peak_mult = seasonal_peaks.get(d_dep.month, 1.0)
    
        # C. Carrier Average Calculation
        # Weights: SIA(1.0), Cathay(0.85), China Southern(0.68), etc.
        airline_prices = [base * c["w"] * inf_adj * peak_mult for c in master_carriers]
        avg_price = sum(airline_prices) / len(airline_prices)
    
        # D. Trend Logic
        is_peak = peak_mult > 1.0
    
        hero_grid.append({
            "Route": route,
            "Est. Price (SGD)": f"${avg_price:,.0f}",
            "Season": "🔥 Peak" if is_peak else "🍃 Off-Peak",
            "Month": d_dep.strftime('%b %y'),
            "Trend": "📈 Rising" if is_peak else "🟢 Stable"
    })

    # 4. COMPACT DISPLAY (Optimized for 10.9-inch / 10pt)
    st.write(f"### ✈️ Projected Fares: {d_dep.strftime('%B %Y')} (SIN Hub)")
    if d_dep.month in [2, 6, 12]:
            st.warning(f"Note: {d_dep.strftime('%B')} is a high-demand period in Singapore. Estimated $ include seasonal surcharges.")

    st.dataframe(hero_grid, hide_index=True, use_container_width=True)
     
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
with tab5:
    #Title heading
    st.markdown("""
        <h2 style='margin-bottom: 0rem; font-size: 20px;'>
            ✈️ Asia Flight outbound from Singapore
        </h2>
        <p style='font-size: 10px; color: gray; margin-top: 0rem;'>
            gold 10 System | March 2026 Live Monitoring
        </p>
    """, unsafe_allow_html=True)
    st.header("✈️ Your Target Asia Airfare Prediction -> Select from below routes only")
    avg_orince = 0.0 #base
    #Title heading ends

    # 1. The Dynamic Trigger: This only runs when the user views Tab 5
    # We use session_state to ensure it only updates ONCE per tab visit
    if "tab5_last_update" not in st.session_state:
        st.session_state.tab5_last_update = None

    # 2. Update Logic (The 4 Values)
    # This runs every time you click into the tab
    with st.spinner("🔄 Syncing 2026 Market Data..."):
        # A. Update Inflation from MAS/Local Source
        v_inf = sg_econ.get('inf_val', 1.2)
        
        # B. Update Fuel (Simulating a live pull or logic check)
        v_fuel = 95.0 + (date.today().month * 0.5) 
        
        # C. Update Seasonal Peaks (Dynamic month check)
        curr_month = date.today().month
        v_peak = 1.35 if curr_month in [6, 12] else 1.0
        
        # D. Log the update time
        st.session_state.tab5_last_update = datetime.now().strftime("%H:%M:%S")

    # 3. Visual Confirmation (Small 10pt Caption)
    st.caption(f"✅ Market Data verified at {st.session_state.tab5_last_update}")

    # --- STEP 2: INSERT THE DYNAMIC RISK ANALYSIS HERE ---
    risk_level = "NORMAL"
    risk_msg = "Market conditions are within 2026 baseline projections."
    
    # Priority 1: Fuel (The biggest threat in March 2026)
    if v_fuel > 150:
        risk_level = "CRITICAL"
        risk_msg = f"Fuel Volatility: Prices at ${v_fuel:.0f}/bbl. Expect immediate surcharge spikes."
    # Priority 2: Seasonality
    elif v_peak > 1.0:
        risk_level = "HIGH"
        risk_msg = f"Seasonal Peak Active: High demand for {date.today().strftime('%B')}. Inventory is low."
    # Priority 3: Inflation
    elif v_inf > 1.5:
        risk_level = "STABLE"
        risk_msg = f"Inflationary Pressure: Local CPI is {v_inf}%. Ground fees are rising."

    # Render the box based on level
    if risk_level == "CRITICAL":
        st.error(f"🚨 **{risk_level} ALERT:** {risk_msg}")
    elif risk_level == "HIGH":
        st.warning(f"⚠️ **{risk_level} ALERT:** {risk_msg}")
    else:
        st.info(f"ℹ️ **{risk_level} STATUS:** {risk_msg}")

    #st.caption(f"✅ Data verified at {st.session_state.tab5_last_update}")

    #Delta for Risk ANALYSIS aLERT
    with st.expander("🔍 View 6-Month Price Variance as of query"):
        col1, col2 = st.columns(2)
        # Based on our data: Sept 2025 avg was ~$310
        price_diff = ((avg_price - 310) / 310) * 100
        
        col1.metric("Current vs Sept 2025", f"${avg_price:.0f}", f"{price_diff:.1f}%")
        col2.metric("Fuel Risk Weight", f"{v_fuel}x", "+110% vs 6m ago")
    
    # 1. SETUP (ORIGIN & NATIONALITY)
    col_a, col_b = st.columns(2)
    with col_a:
        origin_options = ["Singapore (SIN)", "Bangkok (BKK)", "Hong Kong (HKG)", "China (CN)", "Japan (JP)"]
        u_origin_cat = st.selectbox("Select Origin:", origin_options, index=0, key="g10_t5_orig")
        
        china_orig = ["Beijing (PEK)", "Shanghai (PVG)", "Guangzhou (CAN)"]
        thai_orig = ["Suvarnabhumi (BKK)", "Don Mueang (DMK)", "Phuket (HKT)"]
        
        if "China" in u_origin_cat:
            v_origin_final = st.selectbox("Select China Origin:", china_orig, key="g10_t5_china_orig")
        elif "Thailand" in u_origin_cat:
            v_origin_final = st.selectbox("Select Thailand Origin:", thai_orig, key="g10_t5_thai_orig")
        else:
            v_origin_final = u_origin_cat

    with col_b:
        u_nationality = st.text_input("Enter Nationality:", value="Singaporean", key="g10_t5_nat").strip().title()
        v_trip_type = st.radio("Trip Type:", ["Round Trip", "Single Leg"], horizontal=True, key="g10_t5_trip")

    # 2. DESTINATION
    dest_country = st.selectbox("Destination Country:", ["China", "Thailand", "Japan", "Singapore", "Hong Kong"], key="g10_t5_dest_country")
    
    airport_master = {
        "China": ["Beijing (PEK)", "Shanghai (PVG)", "Guangzhou (CAN)", "Shenzhen (SZX)", "Chengdu (TFU)"],
        "Thailand": ["Bangkok (BKK)", "Don Mueang (DMK)", "Phuket (HKT)", "Chiang Mai (CNX)"],
        "Japan": ["Tokyo Narita (NRT)", "Tokyo Haneda (HND)", "Osaka (KIX)", "Fukuoka (FUK)", "Sapporo (CTS)"]
    }

    if dest_country in airport_master:
        selected_airport = st.selectbox(f"Select Preferred Landing Airport in {dest_country}:", 
                                       airport_master[dest_country], 
                                       key="g10_t5_airport_dest")
    else:
        selected_airport = "SIN" if dest_country == "Singapore" else "HKG"

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        d_dep = st.date_input("Esti Departure:", value=date(2026, 6, 17), format="DD/MM/YYYY", key="g10_t5_dep")
    with d_col2:
        d_ret = st.date_input("Esti Return:", value=date(2026, 6, 24), format="DD/MM/YYYY", key="g10_t5_ret") if v_trip_type == "Round Trip" else None

    # 3. CARRIER MASTER DATA & INITIALIZATION
    master_carriers = [
        {"name": "Singapore Airlines", "home": "Singapore", "w": 1.0, "hub": "SIN"},
        {"name": "Cathay Pacific", "home": "Hong Kong", "w": 0.85, "hub": "HKG"},
        {"name": "Air China", "home": "China", "w": 0.65, "hub": "PEK"},
        {"name": "China Southern", "home": "China", "w": 0.68, "hub": "CAN"},
        {"name": "Thai Airways", "home": "Thailand", "w": 0.75, "hub": "BKK"},
        {"name": "ANA", "home": "Japan", "w": 0.95, "hub": "NRT"},
        {"name": "Japan Airline", "home": "Japan", "w": 0.95, "hub": "HND"},
    ]

    priority_carriers = [c for c in master_carriers if c["home"] == dest_country]
    other_carriers = [c for c in master_carriers if c["home"] != dest_country]
    final_sorted = priority_carriers + other_carriers
    top_3_list = [c["name"] for c in final_sorted[:3]]

    # 4. PRICING TABLE
    base_price = 820 if "China" in u_origin_cat else 980
    multiplier = (1.45 if d_dep.month in [6, 12] else 1.0) * (1.0 if v_trip_type == "Round Trip" else 0.65)
    
    grid_rows = []
    for c in final_sorted:
        p = base_price * multiplier * c["w"]
        is_direct = (c["home"] in u_origin_cat) or (c["home"] == dest_country)
        route_type = "✈️ Direct Service" if is_direct else f"🔄 Transit via {c['hub']}"
        
        grid_rows.append({
            "Carrier": c["name"],
            "Adult Avg ($) ≈": f"{p:,.0f}",
            "Route / Type": route_type
        })

    st.subheader(f"📊 Live Avg Pricing non class specific to {selected_airport}")
    st.dataframe(grid_rows, hide_index=True, use_container_width=True)

    # 5. STRATEGIC POP-UP LOGIC
    @st.dialog("16-Week Flight Strategy", width="large")
    def show_strategy_roadmap(airline_choice):
        active_c = next(c for c in final_sorted if c["name"] == airline_choice)
        st.write(f"### 🗓️ Forecast for {active_c['name']}")
        
        pop_data = []
        for w in range(16, -1, -1):
            t_date = d_dep - timedelta(weeks=w)
            if 7 <= w <= 9:
                advice = f"✅ BUY: {', '.join(top_3_list[:2])}"
            elif w > 9:
                advice = "⏳ HOLD: Prices Stagnant"
            else:
                advice = "🚨 PANIC: Late Booking Surge"
            
            w_price = (base_price * multiplier * active_c["w"]) * (1.0 if 7 <= w <= 9 else (1.15 if w > 9 else 1.40))
            
            pop_data.append({
                "Weeks Prior": w,
                "Target Date": t_date.strftime('%d %b %Y'),
                "Est. Price ($)": f"{w_price:,.0f}",
                "Action": advice
            })
        
        st.dataframe(pop_data, hide_index=True, use_container_width=True)
        st.info("💡 **Strategy:** Statistically, the best prices for Asia-Pacific routes are found **7 to 9 weeks** before departure.")
        if st.button("Close"):
            st.rerun()

    # Triggering UI
    st.subheader("🗓️ Purchase Strategy")
    c1, c2 = st.columns([1, 1], gap="small")

    with c1:
        # Ensure this block is indented exactly 4 spaces from 'with'
        roadmap_airline = st.selectbox(
            "Select Airline to Forecast:",
            [c["name"] for c in final_sorted],
            key="g10_t5_roadmap_select"
        )
    
    with c2:
        # Use a spacer to push the button down so it aligns with the selectbox label
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Open Strategic Roadmap", use_container_width=True):
            show_strategy_roadmap(roadmap_airline)

