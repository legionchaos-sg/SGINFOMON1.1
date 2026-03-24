import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_config = st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# 2. Adaptive CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 95%; color: var(--text-color); }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 150px; color: var(--text-color); line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; color: var(--text-color); line-height: 1.2; }
    .news-tag { font-size: 0.65rem; background: var(--secondary-background-color); padding: 2px 4px; border-radius: 3px; color: var(--text-color); opacity: 0.8; margin-right: 5px; font-weight: bold; border: 1px solid var(--border-color); }
    .trans-box { font-size: 0.85rem; color: gray; margin-left: 45px; margin-bottom: 8px; font-style: italic; border-left: 2px solid var(--border-color); padding-left: 10px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.82rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.82rem; }
    .stat-label { font-size: 0.72rem; color: var(--text-color); opacity: 0.6; text-transform: uppercase; }
    .holiday-text { font-size: 0.95rem; color: #28a745; font-weight: bold; margin-left: 10px; }
    .svc-card { background: var(--secondary-background-color); padding: 15px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; color: var(--text-color); }
    .svc-card h4 { color: var(--primary-color); margin-top: 0; }
    .svc-card a { color: #007bff; text-decoration: none; }
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
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px; border-bottom:1px solid var(--border-color);'><b>{brand}</b><span><b style='color:#007bff; margin-right:8px;'>{display_price}</b><span class='{'up' if change > 0 else 'down'}'>({change:+.2f})</span></span></div>", unsafe_allow_html=True)

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9")
tab1, tab2 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES"])

with tab1:
    # 1. Clocks
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)
    st.divider()
    
    # 2. News
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
    for item in news_list:
        st.write(f"<span class='news-tag'>{item['src']}</span> **[{item['title']}]({item['link']})**", unsafe_allow_html=True)

    st.divider()

    # 3. Markets & COE (FIXED SYNTAX)
    with st.expander("🚗 COE Bidding (Mar 2026)", expanded=True):
        coe_data = [("Cat A", 111890, 3670, 1264, 1895), ("Cat B", 115568, 1566, 812, 1185), ("Cat C", 78000, 2000, 290, 438), ("Cat D", 9589, 987, 546, 726), ("Cat E", 118119, 3229, 246, 422)]
        cc = st.columns(5)
        for i, (cat, p, d, q, b) in enumerate(coe_data):
            # We use .format() here to avoid f-string curly brace conflicts with HTML
            html_content = """<div class="c-card"><b>{}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${:,}</span><br><small class="up">▲ ${:,}</small><hr style="margin:5px 0; opacity:0.1;"><span class="stat-label">Quota:</span> <b>{:,}</b><br><span class="stat-label">Bids:</span> <b>{:,}</b></div>""".format(cat, p, d, q, b)
            cc[i].markdown(html_content, unsafe_allow_html=True)

    with st.expander("⛽ Fuel Prices", expanded=True):
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
        fc = st.columns(5)
        for i, ftype in enumerate(ftypes):
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)
            if fc[i].button("Details", key=f"fbtn_{ftype}"): show_fuel_details(ftype)

with tab2:
    # 1. Services
    st.header("🏢 Public Services")
    sc1, sc2, sc3 = st.columns(3)
    with sc1: st.markdown('<div class="svc-card"><h4>🔐 Identity</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a><li><a href="https://www.cpf.gov.sg">CPF</a></ul></div>', unsafe_allow_html=True)
    with sc2: st.markdown('<div class="svc-card"><h4>🏠 Housing</h4><ul><li><a href="https://www.hdb.gov.sg">HDB</a><li><a href="https://www.healthhub.sg">HealthHub</a></ul></div>', unsafe_allow_html=True)
    with sc3: st.markdown('<div class="svc-card"><h4>🚆 Transport</h4><ul><li><a href="https://www.lta.gov.sg">OneMotoring</a><li><a href="https://www.nea.gov.sg">NEA</a></ul></div>', unsafe_allow_html=True)

    # 2. Expressway (Order: CTE, PIE, ECP, KJE)
    st.divider()
    with st.expander("🛣️ Major Expressway Traffic", expanded=True):
        expressways = [("CTE", "#1565C0", "Normal", "✅ Clear"), ("PIE", "#2E7D32", "Heavy", "⚠️ Slow near Bedok"), ("ECP", "#00838F", "Normal", "✅ Clear"), ("KJE", "#6A1B9A", "Normal", "✅ Clear")]
        ex_cols = st.columns(4)
        for i, (id, col, stat, det) in enumerate(expressways):
            bg = "rgba(40, 167, 69, 0.15)" if stat == "Normal" else "rgba(220, 53, 69, 0.15)"
            ex_cols[i].markdown(f'<div style="background:{bg}; border-top:4px solid {col}; padding:10px; border-radius:8px; border:1px solid var(--border-color); color:var(--text-color); height:120px;"><b>{id}</b><br><small>{stat}</small><br><div style="font-size:0.75rem; margin-top:10px;">{det}</div></div>', unsafe_allow_html=True)

    # 3. Rail Status (Combined Titles)
    st.divider()
    line_status = {"NSEWL": "🟢", "CCL": "🟠", "DTL": "🟢", "NEL": "🟢"}
    status_summary = f" | NSEWL:{line_status['NSEWL']} | CCL:{line_status['CCL']} | DTL:{line_status['DTL']} | NEL:{line_status['NEL']}"
    
    with st.expander(f"🚆 Rail Status & Engineering {status_summary}", expanded=False):
        l1, l2, l3, l4 = st.columns(4)
        l1.metric("NS/EW Line", "Normal")
        l2.metric("Circle Line", "Advisory", "-10m", delta_color="off")
        l3.metric("Downtown Line", "Normal")
        l4.metric("North East Line", "Normal")
        st.markdown("---")
        st.info("🛠️ Scheduled Works: Circle Line (Mountbatten-Paya Lebar) Single Platform Service.")

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
