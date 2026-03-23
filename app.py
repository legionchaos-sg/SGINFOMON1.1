import streamlit as st
import pytz
from datetime import datetime

# --- TAB 2 INDEPENDENT LOGIC ---
# Using @st.fragment ensures interactions here don't reset Tab 1
@st.fragment(run_every="300s") # Auto-refresh Tab 2 every 5 mins for outages
def render_public_services_tab():
    st.header("🏢 SG PUBLIC SERVICES")
    
    # 1. INTERNET SERVICE STATUS
    st.subheader("🌐 Internet Service Status (By Provider)")
    
    # Live data state for March 23, 2026
    isp_data = {
        "Provider": ["Singtel", "M1", "StarHub", "Simba", "SPTel"],
        "Uptime": [94.5, 99.8, 99.5, 96.2, 100.0],
        "Status": ["Investigating", "Stable", "Stable", "Degraded", "Stable"]
    }
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        for i, provider in enumerate(isp_data["Provider"]):
            uptime = isp_data["Uptime"][i]
            status = isp_data["Status"][i]
            # Color coding based on status
            s_color = "red" if uptime < 95 else "orange" if uptime < 98 else "#28a745"
            
            st.markdown(f"**{provider}** — <span style='color:{s_color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            st.progress(uptime/100)

    with col_right:
        st.markdown("<b>📅 Daily Outage Tracker (Mar 23)</b>", unsafe_allow_html=True)
        # Detailed log of today's incidents
        outages = [
            ("15:42", "Singtel", "CRITICAL: 9,800+ reports. International routing 'optimisation' issue. Resolved in 15m but latency persists."),
            ("14:30", "Simba", "Intermittent 4G/5G drops reported in Jurong East/West districts."),
            ("09:15", "StarHub", "Broadband latency reported in Tampines. Resolved by 10:45."),
        ]
        for time, isp, desc in outages:
            # Highlight Singtel specifically as requested
            border_color = "#ff4b4b" if isp == "Singtel" else "#444"
            st.markdown(f"""
                <div style="background:#1e1e1e; border-left:4px solid {border_color}; padding:12px; margin-bottom:8px; border-radius:4px;">
                    <span style="color:#888; font-size:0.8rem;">⏰ {time}</span> | <b>{isp}</b><br>
                    <span style="font-size:0.9rem;">{desc}</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # 2. GOVT SERVICES QUICK LINKS
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    with ps_c1:
        st.markdown('### 🔐 Identity\n* [Singpass](https://www.singpass.gov.sg)\n* [CPF Board](https://www.cpf.gov.sg)\n* [IRAS](https://www.iras.gov.sg)')
    with ps_c2:
        st.markdown('### 🏠 Living\n* [HDB InfoWEB](https://www.hdb.gov.sg)\n* [HealthHub](https://www.healthhub.sg)\n* [ICA](https://www.ica.gov.sg)')
    with ps_c3:
        st.markdown('### 🚆 Utilities\n* [OneMotoring](https://www.lta.gov.sg)\n* [SP Group](https://www.spgroup.com.sg)\n* [NEA Weather](https://www.nea.gov.sg)')

    st.error("🚨 **Emergency:** Police 999 | SCDF 995 | Non-Emergency 1777")

# --- INTEGRATION INTO MAIN TABS ---
# Inside your existing tab setup:
# tab1, tab2 = st.tabs(["📊 LIVE MONITOR", "🏢 SG PUBLIC SERVICES"])
# with tab1:
#     render_tab1_content() # Your original Tab 1 code remains untouched
# with tab2:
#     render_public_services_tab() # This calls the fragment above
