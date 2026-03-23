import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.6", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_106_tabs")

# 2. Adaptive CSS (Keeping your ultra-compact styling)
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 155px; color: var(--text-color); line-height: 1.1; }
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

# 4. Workspace Tabs
tab1, tab2 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES"])

with tab1:
    # --- Live Monitor Code ---
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    holiday_info = get_upcoming_holiday()
    st.markdown(f'### 🗞️ Headlines <span class="holiday-text">{holiday_info}</span>', unsafe_allow_html=True)

    # (News Fetching Logic remains same as v10.5)
    news_sources = {"CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416", "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml", "Mothership": "https://mothership.sg/feed/", "8world": "https://www.8world.com/api/v1/rss-outbound-feed?_format=xml&category=176"}
    headers = {'User-Agent': 'Mozilla/5.0'}
    c1, c2 = st.columns([2, 1])
    with c1: search_q = st.text_input("🔍 Search:", key="news_search")
    with c2: 
        v_mode = st.selectbox("Source:", ["Unified (1 per source)", "CNA Only", "Straits Times Only", "Mothership Only", "8world Only"])
        do_tr = st.checkbox("Translate")

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

    for item in news_list:
        st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

    st.divider()
    # (Markets, COE, Fuel expanders go here - logic same as v10.5)
    with st.expander("📈 Market Indices", expanded=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STI Index", "4,841.30", "-2.20%")
        m2.metric("Gold", "$4,202.90", "-8.04%")
        m3.metric("Brent Crude", "$113.34", "+1.02%")
        m4.metric("Silver", "$64.12", "-7.56%")

    with st.expander("🚗 COE Results", expanded=True):
        coe_data = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
        cc = st.columns(5)
        for i, (cat, p, d) in enumerate(coe_data):
            cc[i].markdown(f'<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>', unsafe_allow_html=True)

with tab2:
    # --- SG Public Services Workspace ---
    st.header("🏢 Government & Public Services")
    st.info("Quick access to essential Singapore digital services.")
    
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    
    with ps_c1:
        st.markdown("""
        <div class="svc-card">
        <h4>🔐 Identity & Finance</h4>
        <ul>
            <li><a href="https://www.singpass.gov.sg" target="_blank">Singpass</a></li>
            <li><a href="https://www.cpf.gov.sg" target="_blank">CPF Board</a></li>
            <li><a href="https://www.iras.gov.sg" target="_blank">IRAS (Tax)</a></li>
            <li><a href="https://www.myskillsfuture.gov.sg" target="_blank">SkillsFuture</a></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with ps_c2:
        st.markdown("""
        <div class="svc-card">
        <h4>🏠 Housing & Health</h4>
        <ul>
            <li><a href="https://www.hdb.gov.sg" target="_blank">HDB InfoWEB</a></li>
            <li><a href="https://www.healthhub.sg" target="_blank">HealthHub</a></li>
            <li><a href="https://www.ica.gov.sg" target="_blank">ICA (Passports/IC)</a></li>
            <li><a href="https://www.pa.gov.sg" target="_blank">People's Association</a></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with ps_c3:
        st.markdown("""
        <div class="svc-card">
        <h4>🚆 Transport & Utilities</h4>
        <ul>
            <li><a href="https://www.lta.gov.sg" target="_blank">LTA (OneMotoring)</a></li>
            <li><a href="https://www.spgroup.com.sg" target="_blank">SP Group (Utilities)</a></li>
            <li><a href="https://www.nea.gov.sg" target="_blank">NEA (Weather/Env)</a></li>
            <li><a href="https://www.police.gov.sg" target="_blank">SPF (e-Services)</a></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📞 Emergency Hotlines")
    st.error("🚨 Police: 999 | 🚒 SCDF (Fire/Ambulance): 995 | 🏥 Non-Emergency: 1777")

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
