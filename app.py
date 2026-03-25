import streamlit as st
import feedparser, requests, pytz
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# 1. Page Configuration & Identity
st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_gold10_final")
SGT = pytz.timezone('Asia/Singapore')

# 2. Adaptive CSS (Optimized for 10pt concise space)
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 10pt !important; }
    .main .block-container { max-width: 95%; padding-top: 1rem; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 5px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; line-height: 1.2; }
    .news-tag { font-size: 0.65rem; background: #333; padding: 2px 4px; border-radius: 3px; color: white; margin-right: 5px; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.8rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.8rem; }
    .svc-card { background: var(--secondary-background-color); padding: 12px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 3. Global Logic Functions
def get_upcoming_holiday():
    now = datetime.now(SGT).date()
    holidays_2026 = [("Hari Raya Puasa", datetime(2026, 3, 21).date()), ("Good Friday", datetime(2026, 4, 3).date()), ("Labour Day", datetime(2026, 5, 1).date())]
    for name, h_date in holidays_2026:
        if h_date >= now: return f"🗓️ Next: {name} ({h_date.strftime('%d %b')}) — ⏳ {(h_date - now).days} days"
    return ""

@st.cache_data(ttl=3600)
def fetch_coe_live():
    rid = "d_69b3380ad7e51aff3a7dcc84eba52b8a"
    url = f"https://data.gov.sg/api/action/datastore_search?resource_id={rid}&limit=100"
    try:
        r = requests.get(url, timeout=10).json()
        df = pd.DataFrame(r['result']['records'])
        for c in ['premium', 'quota', 'bids_received']: df[c] = pd.to_numeric(df[c], errors='coerce')
        return df.sort_values(['month', 'bidding_no'], ascending=False).reset_index(drop=True)
    except: return pd.DataFrame()

def get_bidding_status():
    now = datetime.now(SGT)
    def find_mons(y, m):
        d = datetime(y, m, 1)
        d += timedelta(days=(0 - d.weekday() + 7) % 7)
        return [d, d + timedelta(days=14)]
    for mo in [0, 1]:
        m_idx = (now.month + mo - 1) % 12 + 1
        y_idx = now.year + (now.month + mo - 1) // 12
        for mon in find_mons(y_idx, m_idx):
            start = SGT.localize(datetime(mon.year, mon.month, mon.day, 12, 0))
            end = start + timedelta(days=2, hours=4)
            if start <= now <= end: return True, end.strftime("%d %b, 4pm")
            if start > now: return False, start.strftime("%d %b, 12pm")
    return False, "TBD"

fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Shell": (3.47, 0.04), "Sinopec": (3.47, 0.04)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05)},
    "Diesel": {"Esso": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07)}
}

# --- UI START ---
st.title("🇸🇬 SG Info Monitor 10.9.4")
tab1, tab2, tab3, tab4 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES", "🛠️ SYSTEM TOOLS", "🚗 PMT COE"])

# TAB 1: LIVE MONITOR
with tab1:
    t_cols = st.columns(6)
    for i, (n, tz) in enumerate([("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]):
        t_cols[i].markdown(f'<div class="t-card"><small>{n}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)
    
    st.markdown(f'### 🗞️ Headlines <span style="color:#28a745; font-size:0.9rem;">{get_upcoming_holiday()}</span>', unsafe_allow_html=True)
    feed = feedparser.parse("https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416")
    for entry in feed.entries[:4]:
        st.write(f"<span class='news-tag'>CNA</span> **[{entry.title}]({entry.link})**", unsafe_allow_html=True)
    
    st.divider()
    with st.expander("💱 Foreign Exchange (1 SGD)", expanded=True):
        f1, f2, f3, f4, f5 = st.columns(5)
        f1.metric("SGD/MYR", "3.4412", "+0.12%")
        f2.metric("SGD/JPY", "118.55", "-0.43%")
        f3.metric("SGD/THB", "26.85", "+0.15%")
        f4.metric("SGD/CNY", "5.3975", "-0.07%")
        f5.metric("SGD/USD", "0.7480", "-0.22%")

# TAB 2: PUBLIC SERVICES
with tab2:
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="svc-card"><b>🔐 Finance</b><br>• <a href="https://www.singpass.gov.sg">Singpass</a><br>• <a href="https://www.cpf.gov.sg">CPF</a><br>• <a href="https://www.iras.gov.sg">IRAS</a></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="svc-card"><b>🏠 Housing</b><br>• <a href="https://www.hdb.gov.sg">HDB</a><br>• <a href="https://www.ica.gov.sg">ICA</a><br>• <a href="https://www.healthhub.sg">HealthHub</a></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="svc-card"><b>🚆 Transport</b><br>• <a href="https://www.lta.gov.sg">OneMotoring</a><br>• <a href="https://www.nea.gov.sg">NEA PSI</a><br>• <a href="https://www.spgroup.com.sg">SP Group</a></div>', unsafe_allow_html=True)

# TAB 3: SYSTEM TOOLS (FX Command Center)
with tab3:
    st.header("🌐 Live FX Command Center")
    rates = {"SGD/CNY": 5.3789, "SGD/JPY": 124.137, "SGD/THB": 25.534}
    pair = st.selectbox("Pair:", list(rates.keys()))
    curr = rates[pair]
    col1, col2, col3 = st.columns(3)
    col1.metric("Market", f"{curr:.4f}")
    col2.metric("Target High", f"{curr*1.005:.4f}")
    col3.metric("Target Low", f"{curr*0.995:.4f}")
    st.line_chart([curr * (1 + (i*0.0005)) for i in range(-10, 5)], height=150)

# TAB 4: PMT COE ENGINE (Integration)
with tab4:
    df = fetch_coe_live()
    is_open, target_time = get_bidding_status()
    if not df.empty:
        def calc_pred(s):
            v = s.head(3).tolist()
            return (v[0]*0.5 + v[1]*0.3 + v[2]*0.2) if len(v)>=3 else 0
        
        ca, cb = df[df['vehicle_class']=='Category A'], df[df['vehicle_class']=='Category B']
        pa, pb = calc_pred(ca['premium']), calc_pred(cb['premium'])

        st.markdown(f"### Next Session: **{target_time}** | Window: {'🟢 OPEN' if is_open else '⚪ CLOSED'}")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.metric("Model Prediction (Cat A)", f"${int(pa):,}")
            st.write(f"**Quota:** {ca['quota'].iloc[0]} | **Bids:** {ca['bids_received'].iloc[0] if is_open else 'SUBMISSION WINDOW NOT OPEN YET'}")
        with mc2:
            st.metric("Model Prediction (Cat B)", f"${int(pb):,}")
            st.write(f"**Quota:** {cb['quota'].iloc[0]} | **Bids:** {cb['bids_received'].iloc[0] if is_open else 'SUBMISSION WINDOW NOT OPEN YET'}")

        st.divider()
        st.subheader("📑 Trade Record Ledger")
        records = []
        for m in df['month'].unique()[:6]:
            m_df = df[df['month'] == m]
            prev = df[df['month'] < m].head(10)
            p_a, p_b = calc_pred(prev[prev['vehicle_class']=='Category A']['premium']), calc_pred(prev[prev['vehicle_class']=='Category B']['premium'])
            records.append({"Date": m, "Pred A": int(p_a), "Mkt A": int(m_df[m_df['vehicle_class']=='Category A']['premium'].iloc[0]), "Pred B": int(p_b), "Mkt B": int(m_df[m_df['vehicle_class']=='Category B']['premium'].iloc[0])})
        ledger_df = pd.DataFrame(records)
        st.dataframe(ledger_df, hide_index=True, use_container_width=True)
        st.download_button("📥 Download Record", ledger_df.to_csv(index=False), "coe_ledger.csv")

st.caption("Data: NEA/LTA/MAS 2026. Fonts: -10pt. gold 10 active.")
