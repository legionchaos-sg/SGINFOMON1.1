with tab2:
    # --- 1. Government & Public Services ---
    st.header("🏢 Government & Public Services")
    ps_c1, ps_c2, ps_c3 = st.columns(3)
    
    with ps_c1:
        st.markdown('<div class="svc-card"><h4>🔐 Identity & Finance</h4><ul><li><a href="https://www.singpass.gov.sg">Singpass</a><li><a href="https://www.cpf.gov.sg">CPF Board</a><li><a href="https://www.iras.gov.sg">IRAS (Tax)</a><li><a href="https://www.myskillsfuture.gov.sg">SkillsFuture</a></ul></div>', unsafe_allow_html=True)
    with ps_c2:
        st.markdown('<div class="svc-card"><h4>🏠 Housing & Health</h4><ul><li><a href="https://www.hdb.gov.sg">HDB InfoWEB</a><li><a href="https://www.healthhub.sg">HealthHub</a><li><a href="https://www.ica.gov.sg">ICA</a><li><a href="https://www.pa.gov.sg">People\'s Association</a></ul></div>', unsafe_allow_html=True)
    with ps_c3:
        st.markdown('<div class="svc-card"><h4>🚆 Transport & Environment</h4><ul><li><a href="https://www.lta.gov.sg">OneMotoring</a><li><a href="https://www.spgroup.com.sg">SP Group</a><li><a href="https://www.nea.gov.sg">NEA (PSI/Weather)</a><li><a href="https://www.police.gov.sg">SPF e-Services</a></ul></div>', unsafe_allow_html=True)

    st.divider()
    st.error("🚨 Police: 999 | 🚒 SCDF: 995 | 🏥 Non-Emergency: 1777")

    # --- 2. Network & Connectivity Status ---
    st.subheader("🌐 Internet & Mobile Connectivity (24h Monitor)")
    col_graph, col_outage = st.columns([3, 2])

    with col_graph:
        st.write("**Provider Uptime Efficiency**")
        providers = ["Singtel", "M1", "Starhub", "SPTel", "Simba"]
        uptime_scores = [99.8, 92.1, 98.5, 100.0, 97.4] 
        for prov, score in zip(providers, uptime_scores):
            bar_color = "#28a745" if score > 98 else "#ffc107" if score > 95 else "#dc3545"
            st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color: var(--text-color);">
                        <span><b>{prov}</b></span><span>{score}%</span>
                    </div>
                    <div style="background-color: var(--border-color); border-radius: 4px; height: 10px; width: 100%;">
                        <div style="background-color: {bar_color}; width: {score}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.link_button("🚀 Run Instant Speed Test (Ookla)", "https://www.speedtest.net", use_container_width=True)

    with col_outage:
        st.write("**⚠️ Recent Incident Log**")
        incidents = [
            ("M1", "08:45", "Fiber latency in West area. (Resolved)"),
            ("Singtel", "14:20", "Brief DNS timeout; auto-recovered."),
            ("Starhub", "N/A", "Stable - No issues reported."),
            ("Simba", "11:30", "Minor SMS delays for roaming users.")
        ]
        for p, t, m in incidents:
            status_color = "#28a745" if "Resolved" in m or "Stable" in m else "#ffc107"
            st.markdown(f"""
                <div style="font-size:0.8rem; border-left: 3px solid {status_color}; padding-left:8px; margin-bottom:12px; color: var(--text-color);">
                    <b style="color: var(--primary-color);">{p}</b> <small style="opacity:0.6;">{t}</small><br>{m}
                </div>
            """, unsafe_allow_html=True)

    # --- 3. Rail Service & Engineering Advisory ---
    st.divider()
    st.subheader("🚆 Rail Service & Engineering Advisory")
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
            st.markdown(f"""
                <div style="background-color: {line['color']}; padding: 8px; border-radius: 5px; text-align: center; color: white; border: 1px solid rgba(255,255,255,0.2);">
                    <div style="font-size: 0.7rem; font-weight: bold;">{line['name']}</div>
                    <div style="font-size: 1.2rem; margin: 2px 0;">{status_icon}</div>
                    <div style="font-size: 0.6rem; text-transform: uppercase;">{line['status']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 🛠️ Weekly Maintenance & Engineering Works")
    advisories = [
        {"line": "Circle Line (CCL)", "impact": "Single Platform Service", "details": "Ongoing tunnel strengthening between <b>Mountbatten and Paya Lebar</b>. Shuttle trains running every 10 mins.", "status": "In Progress"},
        {"line": "Sengkang West LRT", "impact": "Advance Notice: Loop Closure", "details": "Inner Loop will close starting 19 April 2026 for 6 months.", "status": "Upcoming"},
        {"line": "Downtown/East-West", "impact": "Early Closure/Late Opening", "details": "System integration works for DTL3 extension. Check station posters.", "status": "Scheduled"}
    ]

    for adv in advisories:
        # ADAPTIVE FIX: Using CSS Variables for readability in Light/Dark mode
        st.markdown(f"""
            <div style="background-color: var(--secondary-background-color); border: 1px solid var(--border-color); padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: var(--primary-color);">{adv['line']} - {adv['impact']}</span>
                    <span style="font-size: 0.65rem; background: #ff4b4b; color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold;">{adv['status']}</span>
                </div>
                <div style="font-size: 0.85rem; margin-top: 8px; color: var(--text-color); line-height: 1.4;">{adv['details']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.caption("Data source: LTA MyTransport / SMRT / SBS Transit / ISP Status Feeds.")
