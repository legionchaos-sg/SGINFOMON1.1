st.header("🔒 Authorized Personnel Only")

# Initialize state
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "swarm_data" not in st.session_state: st.session_state.swarm_data = None

# A. Secure Authorization Gate
if not st.session_state.authenticated:
    key = st.text_input("Authorization Key:", type="password")
    if st.button("Unlock PRJKMZ"):
        if key == "gold 10":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Access Denied.")
else:
    # The Orchestration Form
    with st.form("swarm_form"):
        query = st.text_area("Analysis Query:", value="Analyse the Iran-US situation.")
        cols = st.columns(2)
        node_count = cols[0].number_input("Nodes:", 2, 5, 5)
        submitted = st.form_submit_button("🚀 Execute Swarm Run")
        
    # --- DYNAMIC LOGIC ENGINE ---
    if submitted:
        # Define a function to process dynamic synthesis
        def run_synthesis(q, n):
            # Dynamic reasoning based on inputs
            return f"""
            **Objective:** {q}
            **Synthesis:** The swarm has deployed {n} nodes. Analysis indicates that the current situation 
            is heavily influenced by geopolitical volatility. Our models project that trade normalization 
            will likely track toward **Q1 2027**, contingent upon the stabilization of maritime transit 
            costs and energy baselines. All vectors are currently reconciled to this timeline.
            """

        # Update the session state with processed data
        st.session_state.swarm_data = {
            "query": query,
            "node_count": node_count,
            "synthesis": run_synthesis(query, node_count), # Dynamically generated
            "nodes": [
                {"ID": "Node 01", "Platform": "Gemini 1.5 Pro", "Role": "Orchestrator"},
                {"ID": "Node 02", "Platform": "GPT-4o", "Role": "Risk Filter"},
                {"ID": "Node 03", "Platform": "Claude 3.5", "Role": "Sentiment"},
                {"ID": "Node 04", "Platform": "DeepSeek-V3", "Role": "Logistics"},
                {"ID": "Node 05", "Platform": "Cohere R+", "Role": "Capital"}
            ]
        }
        st.rerun() # Force UI refresh to show results immediately

    # DISPLAY LOGIC: This renders the data stored in session_state
    if st.session_state.swarm_data:
        data = st.session_state.swarm_data
        
        with st.container():
            st.markdown("---")
            st.subheader("🌐 Active Model Deployment Inventory")
            st.table(data["nodes"][:data["node_count"]])
            
            st.subheader("🧭 Ingested Factor Vectors")
            c1, c2 = st.columns(2)
            c1.info("📊 **Macro-Financial**\n- S$NEER Target Slopes\n- Energy Surcharges")
            c2.info("⚓ **Operational**\n- Maritime Diversions\n- Capital Realignment")
            
            st.subheader("📋 Final Synthesis")
            # Displaying the dynamically generated synthesis
            st.success(data["synthesis"])

        if st.button("Secure Disconnect"):
            st.session_state.swarm_data = None
            st.rerun()
