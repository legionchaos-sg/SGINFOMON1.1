import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# SG INFO MONITOR - GOLD VERSION 10.0 (RESTORED + INTEGRATED WEATHER)

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.0", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_10_gold_restored")

# 2. Adaptive CSS (Ver 10 Original)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 150px; color: var(--text-color); line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.2; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.82rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.82rem; }
    .holiday-text { font-size: 0.95rem; color: #28a745; font-weight: bold; margin-left: 10px; }
    .svc-card { background: var(--secondary-background-color); padding: 15px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; }
    .traffic-pill { padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; color: white; display: inline-block; margin-bottom: 5px; width: 100%; text-align: center;}
    .weather-info { font-size: 1.1rem; font-weight: bold; color: #007bff; }
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

def fetch_nea_api(endpoint):
    try:
        url = f"https://api-open.data.gov.sg/v2/real-time/api/{endpoint}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and 'items' in data['data'] and len(data['data']['items']) > 0:
                return data['data']['items'][0]
        return None
    except: return None

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
        p, c = fuel_data[ftype].get(brand, ("N/A", 0))
        dp = f"${p:.2f}" if isinstance(p, (int, float)) else p
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff; margin-right:8px;'>{dp}</b><span class='{'up' if c > 0 else 'down'}'>({c:+.2f})</span></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.0 (GOLD)")
tab1, tab2 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES"])

# --- TAB 1 (FULLY PRESERVED) ---
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
    with nc2: v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
    
    news_list = []
    for src, url in news_sources.items():
        if "Unified" in v_mode or src in v_mode:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    feed = feedparser.parse(resp.content)
                    for entry in feed.entries[:(1 if "Unified" in v_mode else 10)]:
                        if not search_q or search_q.lower() in entry.title.lower():
                            news_list.append({'src': src, 'title': entry.title, 'link': entry.link})
            except: pass
    for item in news_list:
        st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

    st.divider()
    with st.expander("📈 Market Indices", expanded=True):
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("STI Index", "4,841.30", "-2.20%")
        m2.metric("Gold (Spot)", "$4,391.00", "+1.66%")
        m3.metric("Silver (Spot)", "$64.63", "-6.11%")
        m4.metric("Brent Crude", "$112.61", "+0.40%")
        m5.metric("Natural Gas", "$3.09", "-2.21%")

    with st.expander("🚗 COE Bidding Results", expanded=True):
        coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
        cc = st.columns(5)
        for i, (cat, p, d, q, b) in enumerate(coe_data):
            cc[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>""", unsafe_allow_html=True)

    with st.expander("⛽ Fuel Prices", expanded=True):
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
        for i, ftype in enumerate(ftypes):
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if fc[i].button("Details", key=f"fbtn_{ftype}"): show_fuel_details(ftype)

# --- TAB 2 (PRESERVED TOP + NEW INTEGRATED WEATHER) ---
with tab2:
    st.header("🏢 Government & Public Services")
    st.markdown('<div class="svc-card"><h4>🔐 Identity, Health & Transport</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a> | <a href="https://www.healthhub.sg">HealthHub</a> | <a href="https://www.lta.gov.sg">LTA OneMotoring</a></ul></div>', unsafe_allow_html=True)
    st.error("🚨 Police: 999 | 🚒 SCDF: 995")

    st.divider()
    with st.expander("🚆 Rail Service Status", expanded=False):
        l_cols = st.columns(6)
        lines = [("EWL", "✅"), ("NSL", "✅"), ("NEL", "✅"), ("CCL", "⚠️"), ("DTL", "✅"), ("TEL", "✅")]
        for i, (n, s) in enumerate(lines): l_cols[i].metric(n, s)

    st.divider()
    with st.expander("🚦 Traffic Info", expanded=False):
        tr_cols = st.columns(6)
        expr = [("CTE", "Optimal", "#28a745"), ("PIE", "Heavy", "#ffc107"), ("AYE", "Congested", "#dc3545"), ("ECP", "Optimal", "#28a745"), ("KJE", "Moderate", "#ffc107"), ("MCE", "Optimal", "#28a745")]
        for i, (n, c, clr) in enumerate(expr):
            tr_cols[i].markdown(f'<div class="traffic-pill" style="background:{clr}">{n}<br>{c}</div>', unsafe_allow_html=True)

    # --- INTEGRATED WEATHER: ESTATE / TEMP / PSI ---
    st.divider()
    with st.expander("🌤️ Live Weather & Air Quality", expanded=True):
        f_data = fetch_nea_api("two-hr-forecast")
        t_data = fetch_nea_api("air-temperature")
        p_data = fetch_nea_api("psi")
        
        if f_data:
            estates = sorted([f['area'] for f in f_data['forecasts']])
            sel_est = st.selectbox("📍 Select Estate:", estates)
            
            # Forecast Status
            status = next((f['forecast'] for f in f_data['forecasts'] if f['area'] == sel_est), "Cloudy")
            
            # Safe Temp Access
            temp = "N/A"
            if t_data and 'readings' in t_data:
                temp = f"{t_data['readings'][0].get('value', 'N/A')}°C"
                
            # Safe PSI Access
            psi = "N/A"
            if p_data and 'readings' in p_data:
                psi = p_data['readings'].get('psi_twenty_four_hourly', {}).get('national', "N/A")
            
            # Integrated Combined Output
            st.markdown(f"""
            <div class="weather-info">
            {sel_est.upper()}: {status} | TEMP: {temp} | PSI: {psi}
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("Connecting to NEA Data Feed...")

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
