import streamlit as st
import feedparser, requests, pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# SG INFO MONITOR - Version 10.9.9 (Panel Relocation & Wide Fix)

# 1. Page Configuration
st.set_page_config(page_title="SG INFO MON 10.9", page_icon="🇸🇬", layout="wide")
st_autorefresh(interval=180000, key="sync_109_stable")

# 2. Enhanced CSS for True Wide Mode & Styling
st.markdown("""
    <style>
    [data-testid="stMainBlockContainer"] { max-width: 98% !important; padding-top: 1rem !important; }
    .t-card { background: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; }
    .c-card { background: var(--secondary-background-color); border-left: 5px solid #ff4b4b; padding: 7px; border-radius: 6px; margin-bottom: 8px; min-height: 120px; line-height: 1.1; }
    .f-card { background: var(--secondary-background-color); border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; }
    .up { color: #ff4b4b !important; font-weight: bold; font-size: 0.82rem; } 
    .down { color: #28a745 !important; font-weight: bold; font-size: 0.82rem; }
    .svc-card { background: var(--secondary-background-color); padding: 15px; border-radius: 10px; border: 1px solid var(--border-color); height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data & Logic
fuel_data = {
    "92 Octane": {"Esso": (3.43, 0.39), "Caltex": (3.43, 0.32), "SPC": (3.43, 0.32)},
    "95 Octane": {"Esso": (3.47, 0.04), "Caltex": (3.47, 0.04), "Shell": (3.47, 0.04), "SPC": (3.46, 0.02)},
    "98 Octane": {"Esso": (3.97, 0.05), "Shell": (3.99, 0.05), "SPC": (3.97, 0.05)},
    "Premium": {"Caltex": (4.16, 0.20), "Shell": (4.21, 0.05)},
    "Diesel": {"Esso": (3.73, 0.10), "Caltex": (3.73, 0.10), "Shell": (3.73, 0.10), "SPC": (3.56, 0.07)}
}

# --- UI START ---
tab1, tab2 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES & NETWORK"])

with tab1:
    # 1. Clocks
    t_cols = st.columns(6)
    countries = [("Singapore", "Asia/Singapore"), ("Thailand", "Asia/Bangkok"), ("Japan", "Asia/Tokyo"), ("Indonesia", "Asia/Jakarta"), ("Philippines", "Asia/Manila"), ("Australia", "Australia/Brisbane")]
    for i, (name, tz) in enumerate(countries):
        t_cols[i].markdown(f'<div class="t-card"><small>{name}</small><br><b>{datetime.now(pytz.timezone(tz)).strftime("%H:%M")}</b></div>', unsafe_allow_html=True)

    st.divider()
    
    # 2. Market Indices, Economic Data & Forex
    with st.expander("📈 Market Indices & Economic Data", expanded=True):
        ec1, ec2, ec3, ec4, ec5 = st.columns(5)
        ec1.metric("STI Index", "4,841.30", "-2.20%")
        ec2.metric("Gold (Spot)", "$4,391.00", "+1.66%")
        ec3.metric("Brent Crude", "$112.61", "+0.40%")
        ec4.metric("SG Inflation (YoY)", "1.20%", "-0.20%")
        ec5.metric("SG CPI Index", "101.91", "+0.60")

        st.markdown("#### 💱 Foreign Exchange Rates (Against 1 SGD)")
        fx1, fx2, fx3, fx4, fx5 = st.columns(5)
        fx1.metric("SGD/MYR", "3.0932", "+0.12%")
        fx2.metric("SGD/USD", "0.7480", "-0.22%")
        fx3.metric("SGD/JPY", "112.45", "+0.85%")
        fx4.metric("SGD/THB", "24.52", "-0.15%")
        fx5.metric("SGD/CNY", "5.4036", "+0.08%")

    # 3. COE Results
    with st.expander("🚗 COE Bidding Results", expanded=True):
        coe_data = [("Cat A", 111890, 3670), ("Cat B", 115568, 1566), ("Cat C", 78000, 2000), ("Cat D", 9589, 987), ("Cat E", 118119, 3229)]
        cc = st.columns(5)
        for i, (cat, p, d) in enumerate(coe_data):
            cc[i].markdown(f"""<div class="c-card"><b>{cat}</b><br><span style="color:#ff4b4b; font-size:1.1rem; font-weight:bold;">${p:,}</span><br><small class="up">▲ ${d:,}</small></div>""", unsafe_allow_html=True)

    # 4. Fuel Prices
    with st.expander("⛽ Fuel Prices (Avg per Grade)", expanded=True):
        fc = st.columns(5)
        ftypes = ["92 Octane", "95 Octane", "98 Octane", "Premium", "Diesel"]
        for i, ftype in enumerate(ftypes):
            prices = [v[0] for v in fuel_data[ftype].values() if isinstance(v[0], (int, float))]
            avg = sum(prices) / len(prices) if prices else 0
            fc[i].markdown(f'<div class="f-card"><b>{ftype}</b><br><span style="color:#007bff;font-size:1.1rem;font-weight:bold;">${avg:.2f}</span></div>', unsafe_allow_html=True)

with tab2:
    # 1. Internet & Mobile Connectivity (MOVED BACK HERE)
    with st.expander("🌐 Internet & Mobile Connectivity (Live Monitor)", expanded=True):
        providers = ["Singtel", "M1", "Starhub", "SPTel", "Simba"]
        uptime_scores = [99.8, 92.1, 98.5, 100.0, 97.4] 
        col_graph, col_outage = st.columns([3, 2])
        with col_graph:
            for prov, score in zip(providers, uptime_scores):
                bar_color = "#28a745" if score > 98 else "#ffc107"
                st.markdown(f"""<div style="margin-bottom:10px;"><div style="display:flex; justify-content:space-between; font-size:0.8rem;"><span><b>{prov}</b></span><span>{score}%</span></div><div style="background-color: #333; height: 8px; width: 100%; border-radius: 4px;"><div style="background-color: {bar_color}; width: {score}%; height: 100%; border-radius: 4px;"></div></div></div>""", unsafe_allow_html=True)
        with col_outage:
            st.markdown("🏁 **Recent Incidents**")
            st.caption("⚠️ M1: Latency reported in Jurong (08:45)")
            st.caption("✅ Singtel: All systems operational.")

    st.divider()

    # 2. Government Services
    st.header("🏢 Government & Public Services")
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    with ps_c1: st.markdown('<div class="svc-card"><h4>🔐 Finance</h4><ul><li>Singpass<li>CPF Board<li>IRAS</ul></div>', unsafe_allow_html=True)
    with ps_c2: st.markdown('<div class="svc-card"><h4>🏠 Housing</h4><ul><li>HDB<li>HealthHub<li>ICA</ul></div>', unsafe_allow_html=True)
    with ps_c3: st.markdown('<div class="svc-card"><h4>🚆 Transport</h4><ul><li>OneMotoring<li>NEA<li>SPF</ul></div>', unsafe_allow_html=True)

    # 3. Rail & Traffic
    with st.expander("🚆 Rail & Traffic Status", expanded=False):
        st.write("✅ All MRT Lines operating normally.")
        st.write("🚦 PIE (Towards Changi): Heavy traffic near Lornie Rd.")

st.caption(f"Last Sync: {datetime.now(pytz.timezone('Asia/Singapore')).strftime('%H:%M:%S')} SGT")
