# --- TAB 2: SG PUBLIC SERVICES (Updated Section) ---

with tab2:
    st.header("🏢 SG PUBLIC SERVICES")
    
    st.subheader("🌐 Internet Service Status (By Provider)")
    
    # Updated Uptime for Singtel based on this afternoon's events
    isp_data = {
        "Provider": ["Singtel", "M1", "StarHub", "Simba", "SPTel"],
        "Uptime": [94.5, 99.8, 99.5, 96.2, 100.0],
        "Status": ["Investigating", "Stable", "Stable", "Degraded", "Stable"]
    }
    
    isc1, isc2 = st.columns([1, 1])
    
    with isc1:
        for i, provider in enumerate(isp_data["Provider"]):
            uptime = isp_data["Uptime"][i]
            status = isp_data["Status"][i]
            # Change Singtel to Red/Warn if uptime drops below 95%
            s_class = "status-up" if uptime > 99 else "status-warn" if uptime > 95 else "status-down"
            
            st.markdown(f"**{provider}** — <span class='{s_class}'>{status}</span>", unsafe_allow_html=True)
            st.progress(uptime/100)

    with isc2:
        st.markdown("<b>📅 Daily Outage Tracker (Mar 23)</b>", unsafe_allow_html=True)
        # Added the major afternoon outage
        outages = [
            ("15:40", "Singtel", "CRITICAL: Over 9,700 reports. 'International traffic optimisation' issue. Resolved in 15 mins but lingering latency reported."),
            ("14:30", "Simba", "Intermittent 4G/5G drops in Jurong East/West (Ongoing)."),
            ("09:15", "StarHub", "Broadband latency reported in Tampines. Resolved by 10:45."),
        ]
        for time, isp, desc in outages:
            # Highlight Singtel in red for today's major event
            border_color = "#ff4b4b" if isp == "Singtel" else "#333"
            st.markdown(f"""<div style="background:#1e1e1e; border-left:3px solid {border_color}; padding:10px; margin-bottom:5px; border-radius:4px; font-size:0.85rem;">
                ⏰ <b>{time}</b> | 🏢 <b>{isp}</b><br>{desc}</div>""", unsafe_allow_html=True)
