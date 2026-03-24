st.markdown("#### 🛠️ Weekly Maintenance & Engineering Works")
    
    # 1. Defined uniquely once
    advisories = [
        {
            "line": "Circle Line (CCL)", 
            "impact": "Single Platform Service", 
            "details": "Tunnel strengthening between <b>Mountbatten and Paya Lebar</b>. Shuttle trains running every 10 mins.", 
            "status": "In Progress"
        },
        {
            "line": "Sengkang West LRT", 
            "impact": "Advance Notice: Loop Closure", 
            "details": "Inner Loop will close starting <b>19 April 2026</b> for 6 months. Use Outer Loop.", 
            "status": "Upcoming"
        }
    ]

    # 2. Loop through and apply Adaptive Colors
    for adv in advisories:
        st.markdown(f"""
            <div style="
                background-color: var(--secondary-background-color); 
                border: 1px solid var(--border-color); 
                padding: 12px; 
                border-radius: 8px; 
                margin-bottom: 10px;
                color: var(--text-color);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: var(--primary-color); font-size: 1rem;">
                        {adv['line']} - {adv['impact']}
                    </span>
                    <span style="
                        font-size: 0.65rem; 
                        background: #ff4b4b; 
                        color: white; 
                        padding: 2px 8px; 
                        border-radius: 12px; 
                        font-weight: bold;
                    ">
                        {adv['status']}
                    </span>
                </div>
                <div style="
                    font-size: 0.9rem; 
                    margin-top: 8px; 
                    line-height: 1.4;
                    opacity: 0.9;
                ">
                    {adv['details']}
                </div>
            </div>
        """, unsafe_allow_html=True)
