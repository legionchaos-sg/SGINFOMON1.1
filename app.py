import streamlit as st
import feedparser, requests, pytz
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# SG INFO MONITOR - Weather & Traffic Update 10.9.3 - FINAL INTEGRATED
# Identification: gold 10

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
    .pmt-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
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

def get_nea_data(path):
    try:
        r = requests.get(f"https://api-open.data.gov.sg/v2/real-time/api/{path}", timeout=5)
        return r.json().get('data', {}) if r.status_code == 200 else {}
    except: return {}

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
        display_price = f"${price:.2f}" if isinstance(price, (int, float)) else price
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px; border-bottom:1px solid #333;'><b>{brand}</b><span><b style='color:#007bff; margin-right:8px;'>{display_price}</b><span class='{'up' if change > 0 else 'down'}'>({change:+.2f})</span></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9")
tab1, tab2, tab3, tab4 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🚗 PMT COE"])

# TAB 1: LIVE MONITOR
with tab1:
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)
    st.divider()
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
    with st.expander("📈 Market Indices", expanded=True):
        m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
        m1.metric("STI Index", "4,841.30", "-2.20%")
        m2.metric("Gold (Spot)", "$4,391.00", "+1.66%")
        m3.metric("Silver (Spot)", "$64.63", "-6.11%")
        m4.metric("Brent Crude", "$112.61", "+0.40%")
        m5.metric("Natural Gas", "$3.09", "-2.21%")
        m6.metric("SG CPI (All)", "100.7", "-0.20%")
        m7.metric("SG Inflation", "1.40%", "+0.40%")
    with st.expander("💱 Foreign Exchange (1 SGD Base)", expanded=True):
        f1, f2, f3, f4, f5 = st.columns(5)
        f1.metric("SGD/MYR", "3.4412", "+0.12%")
        f2.metric("SGD/JPY", "118.55", "-0.43%")
        f3.metric("SGD/THB", "26.85", "+0.15%")
        f4.metric("SGD/CNY", "5.3975", "-0.07%")
        f5.metric("SGD/USD", "0.7480", "-0.22%")
    with st.expander("🚗 COE Bidding Results (Mar 2026)", expanded=True):
        coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
        cc = st.columns(5)
        for i, (cat, p, d, q, b) in enumerate(coe_data):
            cc[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small><hr style="margin:5px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{q:,}</b><br><span class="stat-label">Bids:</span> <b>{b:,}</b></div>""", unsafe_allow_html=True)
    with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
        for i, ftype in enumerate(ftypes):
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if fc[i].button("Details", key=f"fbtn_109_{ftype}"): show_fuel_details(ftype)

# TAB 2: PUBLIC SERVICES
with tab2:
    st.header("🏢 Government & Public Services")
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    with ps_c1: st.markdown('<div class="svc-card"><h4>🔐 Identity & Finance</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a><li><a href="https://www.cpf.gov.sg">CPF Board</a><li><a href="https://www.iras.gov.sg">IRAS (Tax)</a><li><a href="https://www.myskillsfuture.gov.sg">SkillsFuture</a></ul></div>', unsafe_allow_html=True)
    with ps_c2: st.markdown('<div class="svc-card"><h4>🏠 Housing & Health</h4><ul><li><a href="https://www.hdb.gov.sg">HDB InfoWEB</a><li><a href="https://www.healthhub.sg">HealthHub</a><li><a href="https://www.ica.gov.sg">ICA</a><li><a href="https://www.pa.gov.sg">People\'s Association</a></ul></div>', unsafe_allow_html=True)
    with ps_c3: st.markdown('<div class="svc-card"><h4>🚆 Transport & Environment</h4><ul><li><a href="https://www.lta.gov.sg">OneMotoring</a><li><a href="https://www.spgroup.com.sg">SP Group</a><li><a href="https://www.nea.gov.sg">NEA (PSI/Weather)</a><li><a href="https://www.police.gov.sg">SPF e-Services</a></ul></div>', unsafe_allow_html=True)
    
    with st.expander("🌤️ Island Weather Forecast", expanded=True):
        f_data, t_data = get_nea_data("two-hr-forecast"), get_nea_data("air-temperature")
        items = f_data.get('items', [{}])[0]
        estates = ["Ang Mo Kio", "Bedok", "Bishan", "Bukit Batok", "Bukit Merah", "Bukit Panjang", "Bukit Timah", "Central Area", "Choa Chu Kang", "Clementi", "Geylang", "Hougang", "Jurong East", "Jurong West", "Kallang/Whampoa", "Marine Parade", "Pasir Ris", "Punggol", "Queenstown", "Sembawang", "Sengkang", "Serangoon", "Tampines", "Toa Payoh", "Woodlands", "Yishun"]
        sel_estate = st.selectbox("📍 Select Estate:", sorted(estates))
        area_f = next((f['forecast'] for f in items.get('forecasts', []) if f['area'] == sel_estate), "Cloudy")
        temp = t_data.get('items', [{}])[0].get('readings', [{}])[0].get('value', 31.0)
        st.info(f"**{sel_estate}:** {area_f} | **Temp:** {temp}°C")

# TAB 3: SYSTEM TOOLS
with tab3:
    st.header("🌐 Live FX Command Center")
    rates = {"SGD/CNY": {"price": 5.3789}, "SGD/JPY": {"price": 124.137}, "SGD/THB": {"price": 25.534}}
    pair = st.selectbox("Pair:", list(rates.keys()), key="fx_final")
    curr = rates[pair]["price"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Live Market", f"{curr:.4f}")
    c2.metric("Target High", f"{curr*1.01:.4f}")
    c3.metric("Target Low", f"{curr*0.99:.4f}")
    st.line_chart({"Market": [curr * (1 + (i*0.0006)) for i in range(-5, 5)]}, height=120)

# TAB 4: PMT COE (LIVE RECENT-WEIGHTED ENGINE)
with tab4:
    import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# PMT COE Logic - gold 10
st.markdown('<div style="background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px;"><h3>🚗 PMT: 3-Month Weighted Forecast</h3></div>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_live_coe():
    # Official LTA Dataset ID (Active as of March 2026)
    rid = "d_69b3380ad7e51aff3a7dcc84eba52b8a"
    url = f"https://data.gov.sg/api/action/datastore_search?resource_id={rid}&limit=100"
    
    try:
        # Added User-Agent to prevent 403 Forbidden errors
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data['result']['records'])
        
        # Data Cleaning
        df['premium'] = pd.to_numeric(df['premium'], errors='coerce')
        df['quota'] = pd.to_numeric(df['quota'], errors='coerce')
        df['bids_received'] = pd.to_numeric(df['bids_received'], errors='coerce')
        
        # Sort so index 0 is always the latest bidding round
        df = df.sort_values(by=['month', 'bidding_no'], ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"⚠️ Connection to LTA Feed Failed: {e}")
        return pd.DataFrame()

# Execute Data Pull
live_df = fetch_live_coe()

if not live_df.empty:
    # Filter for Category A and B
    cat_a = live_df[live_df['vehicle_class'] == 'Category A'].head(12)
    cat_b = live_df[live_df['vehicle_class'] == 'Category B'].head(12)
    
    # Calculation Engine: 0.5 (M), 0.3 (M-1), 0.2 (M-2)
    def calculate_weighted_forecast(series):
        vals = series.tolist()
        if len(vals) < 3: return vals[0] if vals else 0
        return (vals[0] * 0.5) + (vals[1] * 0.3) + (vals[2] * 0.2)

    pred_a = calculate_weighted_forecast(cat_a['premium'])
    pred_b = calculate_weighted_forecast(cat_b['premium'])
    
    # UI Layout
    c1, c2 = st.columns(2)
    with c1: 
        st.subheader("Cat A Trend (LTA Live)")
        st.line_chart(cat_a.set_index('month')['premium'])
    with c2: 
        st.subheader("Cat B Trend (LTA Live)")
        st.line_chart(cat_b.set_index('month')['premium'])

    st.divider()
    
    # Prediction Outputs
    latest_month = cat_a['month'].iloc[0]
    st.markdown(f"#### 🤖 Recency-Weighted Prediction: April 2026 (Ref: {latest_month})")
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Cat A Prediction", f"${int(pred_a):,}", f"vs Last: ${int(cat_a['premium'].iloc[0]):,}")
    res2.metric("Cat B Prediction", f"${int(pred_b):,}", f"vs Last: ${int(cat_b['premium'].iloc[0]):,}")
    
    # Bid Pressure Calculation
    pressure = cat_a['bids_received'].iloc[0] / cat_a['quota'].iloc[0]
    res3.metric("Latest Bid Pressure", f"{pressure:.2f}x", "High" if pressure > 1.8 else "Stable")

    # Data Table for Verification
    with st.expander("📝 View Raw API Data (Last 12 Months)"):
        st.dataframe(live_df[['month', 'bidding_no', 'vehicle_class', 'premium', 'quota', 'bids_received']])

else:
    st.warning("No data retrieved. Ensure you are connected to the internet.")

st.caption(f"gold 10 | SGT: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')}")
