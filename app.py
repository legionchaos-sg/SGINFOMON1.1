import streamlit as st
import requests
import pandas as pd
import feedparser
import pytz
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- 1. GLOBAL CONFIG & IDENTITY ---
st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_gold10")
SGT = pytz.timezone('Asia/Singapore')

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 10pt !important; }
    .stMetric { background: var(--secondary-background-color); padding: 5px; border-radius: 5px; border: 1px solid #333; }
    .news-card { border-left: 3px solid #ff4b4b; padding-left: 10px; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CORE LOGIC ---
@st.cache_data(ttl=3600)
def fetch_coe_data():
    rid = "d_69b3380ad7e51aff3a7dcc84eba52b8a"
    url = f"https://data.gov.sg/api/action/datastore_search?resource_id={rid}&limit=150"
    try:
        r = requests.get(url, headers={"User-Agent": "gold-10"}, timeout=10).json()
        df = pd.DataFrame(r['result']['records'])
        for c in ['premium', 'quota', 'bids_received']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        return df.sort_values(['month', 'bidding_no'], ascending=False).reset_index(drop=True)
    except: return pd.DataFrame()

def get_bidding_status():
    now = datetime.now(SGT)
    def get_mons(y, m):
        d = datetime(y, m, 1)
        d += timedelta(days=(0 - d.weekday() + 7) % 7)
        return [d, d + timedelta(days=14)]
    for m_off in [0, 1]:
        m_idx = (now.month + m_off - 1) % 12 + 1
        y_idx = now.year + (now.month + m_off - 1) // 12
        for mon in get_mons(y_idx, m_idx):
            start = SGT.localize(datetime(mon.year, mon.month, mon.day, 12, 0))
            end = start + timedelta(days=2, hours=4)
            if start <= now <= end: return True, end.strftime("%d %b %Y, 4:00 PM")
            if start > now: return False, start.strftime("%d %b %Y, 12:00 PM")
    return False, "TBD"

# --- 4. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 MONITOR", "🏢 SERVICES", "🛠️ TOOLS", "🚗 PMT COE"])

with tab1:
    col_n, col_m = st.columns([2, 1])
    with col_n:
        st.subheader("📰 News")
        f = feedparser.parse("https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416")
        for e in f.entries[:5]: st.markdown(f"<div class='news-card'><b><a href='{e.link}'>{e.title}</a></b></div>", unsafe_allow_html=True)
    with col_m: st.write("**Market Snippet:** SGD/MYR: 3.4412")

with tab2:
    st.subheader("🏢 Essential Services")
    st.write("• [CPF](https://www.cpf.gov.sg) • [IRAS](https://www.iras.gov.sg) • [OneMotoring](https://www.onemotoring.lta.gov.sg)")

# --- REVERTED TAB 3: FX COMMAND CENTER ---
with tab3:
    st.header("🌐 Live FX Command Center")
    rates = {"SGD/CNY": {"price": 5.3789}, "SGD/JPY": {"price": 124.137}, "SGD/THB": {"price": 25.534}}
    pair = st.selectbox("Pair:", list(rates.keys()), key="fx_reverted")
    curr = rates[pair]["price"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Live Market", f"{curr:.4f}")
    c2.metric("Target High", f"{curr*1.01:.4f}")
    c3.metric("Target Low", f"{curr*0.99:.4f}")
    st.line_chart({"Market": [curr * (1 + (i*0.0006)) for i in range(-5, 5)]}, height=150)

# --- TAB 4: COE ENGINE ---
with tab4:
    df = fetch_coe_data()
    is_open, sess_time = get_bidding_status()
    if not df.empty:
        def pred_logic(s):
            v = s.head(3).tolist()
            return (v[0]*0.5 + v[1]*0.3 + v[2]*0.2) if len(v)>=3 else v[0]
        cat_a = df[df['vehicle_class'] == 'Category A']
        cat_b = df[df['vehicle_class'] == 'Category B']
        pa, pb = pred_logic(cat_a['premium']), pred_logic(cat_b['premium'])

        st.markdown(f"### Next Window: **{sess_time}**")
        st.write(f"**Status:** {'🟢 OPEN' if is_open else '⚪ CLOSED'}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Predicted Cat A", f"${int(pa):,}")
            st.write(f"**Allocation:** {cat_a['quota'].iloc[0]}")
            b_a = f"{cat_a['bids_received'].iloc[0]}" if is_open else "SUBMISSION WINDOW NOT OPEN YET"
            st.write(f"**Bids:** {b_a}")
        with c2:
            st.metric("Predicted Cat B", f"${int(pb):,}")
            st.write(f"**Allocation:** {cat_b['quota'].iloc[0]}")
            b_b = f"{cat_b['bids_received'].iloc[0]}" if is_open else "SUBMISSION WINDOW NOT OPEN YET"
            st.write(f"**Bids:** {b_b}")

        st.divider()
        st.subheader("📑 Trade Record Ledger")
        ledger = []
        for m in df['month'].unique()[:6]:
            m_data = df[df['month'] == m]
            prev = df[df['month'] < m].head(10)
            p_a = pred_logic(prev[prev['vehicle_class']=='Category A']['premium'])
            p_b = pred_logic(prev[prev['vehicle_class']=='Category B']['premium'])
            ledger.append({"COE Bid Date": m, "Model Predict Cat A": int(p_a), "Mkt Cat A": int(m_data[m_data['vehicle_class']=='Category A']['premium'].iloc[0]), "Model Predict Cat B": int(p_b), "Mkt Cat B": int(m_data[m_data['vehicle_class']=='Category B']['premium'].iloc[0])})
        st.dataframe(pd.DataFrame(ledger), use_container_width=True, hide_index=True)
        st.download_button("📥 Download Record", pd.DataFrame(ledger).to_csv(index=False), "coe_ledger.csv")

st.caption(f"gold 10 | SGT: {datetime.now(SGT).strftime('%H:%M:%S')}")
